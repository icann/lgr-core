# -*- coding: utf-8 -*-
"""
merge_lgr_set.py - merge a LGR set

Algorithm:
 - prefix rules common to all LGR in the set with 'Common-'
 - prefix other rules, tags, character classes by the script code for its LGR
 - tag codepoints with their script extensions values (scx: i.e. a list of script identifiers)
 - merge actions preserving their order of precedence
 - set all variants types to blocked
"""
from __future__ import unicode_literals

import copy
import logging
import re
from datetime import date
from cStringIO import StringIO
# OrderedDict is used in replacement for set in order to get OrderedSets
from collections import OrderedDict

from lgr.exceptions import LGRFormatException, CharAlreadyExists
from lgr.core import LGR, DEFAULT_ACTIONS
from lgr.metadata import Metadata, Version, Description
from lgr.tools.compare.utils import compare_objects
from lgr.parser.xml_parser import XMLParser
from lgr.parser.xml_serializer import serialize_lgr_xml
from lgr.utils import let_user_choose

logger = logging.getLogger(__name__)

MSR_2_RULES = ['leading-combining-mark']
MSR_NEGATIVE_LOOK_AHEAD = r'(?!' + '|'.join(MSR_2_RULES) + r')'


def get_script(lgr):
    try:
        return lgr.metadata.languages[0]
    except IndexError:
        raise LGRFormatException(reason=LGRFormatException.LGRFormatReason.INVALID_LANGUAGE_TAG)


def merge_version(lgr_set):
    """
    Merge versions from LGR set.

    :param lgr_set: The LGRs in the set
    :return: The merged version object
    """
    values = OrderedDict()
    comments = OrderedDict()
    for version in [lgr.metadata.version for lgr in lgr_set]:
        if not version:
            continue
        if version.value:
            values.update(OrderedDict.fromkeys([version.value]))
        if version.comment:
            comments.update(OrderedDict.fromkeys([version.comment]))

    return Version('|'.join(values.keys()), '|'.join(comments.keys()))


def merge_description(lgr_set):
    """
    Merge description from LGR set.

    :param lgr_set: The LGRs in the set
    :return: The merged description object
    """
    # Check that none of the object is None before processing
    values = []
    all_html = True
    for lgr in lgr_set:
        description = lgr.metadata.description
        script = get_script(lgr)
        if description:
            values.append((script, description))
            all_html &= description.description_type == 'text/html'

    description_type = 'text/plain'
    if all_html:
        template = """{value}"""
        join_prefix = ''
        description_type = 'text/html'
    else:
        template = """
Script: '{script}' - MIME-type: '{type}':
{value}
"""
        join_prefix = '----\n'

    merged_description = join_prefix.join([template.format(script=d[0], type=d[1].description_type, value=d[1].value) for d in values])

    return Description(merged_description, description_type)


def merge_metadata(lgr_set):
    """
    Merge metadata from LGR set.

    :param lgr_set: The LGRs in the set
    :return: The merged metadata object
    """
    logger.debug("Merge metadata")

    output = Metadata()

    output.version = merge_version(lgr_set)
    output.description = merge_description(lgr_set)

    scopes = OrderedDict()
    languages = OrderedDict()
    for metadata in [lgr.metadata for lgr in lgr_set]:
        scopes.update(OrderedDict.fromkeys(metadata.scopes))
        languages.update(OrderedDict.fromkeys(metadata.languages))
        output.validity_start = compare_objects(output.validity_start,
                                                metadata.validity_start,
                                                max)
        output.validity_end = compare_objects(output.validity_end,
                                              metadata.validity_end,
                                              min)

        output.unicode_version = compare_objects(output.unicode_version,
                                                 metadata.unicode_version,
                                                 max)

    output.scopes = list(scopes.keys())
    output.languages = list(languages.keys())

    output.date = date.today().isoformat()

    return output


def merge_references(lgr, script, merged_lgr, ref_mapping):
    """
    Merge references from LGR set.

    :param lgr: The LGR for which to merge references
    :param script:  The LGR script
    :param merged_lgr: The merged LGR
    :param ref_mapping: The reference id mapping from base LGR to LGR set
    """
    ref_mapping.setdefault(script, OrderedDict())
    if lgr.reference_manager:
        inserted_references = {x['value']: ref_id for ref_id, x in merged_lgr.reference_manager.items()}
        for ref_id, ref_dict in lgr.reference_manager.items():
            ref = ref_dict['value']
            if ref not in inserted_references:
                if ref_id not in merged_lgr.reference_manager.keys():
                    merged_lgr.reference_manager.add_reference(ref, ref_id=ref_id, comment=ref_dict.get('comment'))
                else:
                    new_id = merged_lgr.add_reference(ref, comment=ref_dict.get('comment'))
                    ref_mapping[script][ref_id] = new_id
            else:
                if ref_id != inserted_references[ref]:
                    ref_mapping[script][ref_id] = inserted_references[ref]


def rename_action(action, action_xml, script):
    """
    Prefix action matches with script
    
    :param action: The action 
    :param action_xml: The action XML
    :param script:  The LGR script
    :return: Updated action, updated action XML
    """
    new_action = copy.deepcopy(action)
    if action.match:
        if action.match not in MSR_2_RULES:
            new_action.match = script + '-' + action.match
        else:
            # Prefix MSR action with 'Common-'
            new_action.match = 'Common-' + action.match
        action_xml = action_xml.replace(action.match, new_action.match)
    if action.not_match:
        if action.not_match not in MSR_2_RULES:
            new_action.not_match = script + '-' + action.not_match
        else:
            # Prefix MSR action with 'Common-'
            new_action.not_match = 'Common-' + action.not_match
        action_xml = action_xml.replace(action.not_match, new_action.not_match)

    return new_action, action_xml


def merge_actions(lgr, script, merged_lgr, ref_mapping):
    """
    Merge actions from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :param ref_mapping: The reference mapping from base LGR to new LGR
    """
    logger.debug("Merge actions")

    for idx in range(len(lgr.actions)):
        action = lgr.actions[idx]
        action_xml = lgr.actions_xml[idx]
        if action in DEFAULT_ACTIONS:
            continue
        merged_action, merged_action_xml = rename_action(action, action_xml, script)

        # Replace references in python object and XML
        new_ref = [ref_mapping.get(script, {}).get(x, x) for x in action.references]
        merged_action.references = new_ref
        merged_action_xml = re.sub(r'(?<!by-)ref="([^"]+)"', r'ref="{}"'.format(" ".join(new_ref)), merged_action_xml)

        merged_lgr.actions.append(merged_action)
        merged_lgr.actions_xml.append(merged_action_xml)


def rename_rule(rule, rule_xml, script):
    """
    Prefix rule name or reference with script

    :param rule: The rule
    :param rule_xml: The rule XML
    :param script:  The LGR script
    :return: Updated rule name, updated rule XML
    """
    if rule.name not in MSR_2_RULES:
        new_rule_name = script + '-' + rule.name
        rule_xml = re.sub(r'name="' + rule.name + '"', r'name="{}-{}"'.format(script, rule.name), rule_xml)
    else:
        # Prefix MSR rule with 'Common-'
        new_rule_name = 'Common-' + rule.name
    rule_xml = re.sub(r'name="' + rule.name + '"', r'name="' + new_rule_name + '"', rule_xml)

    # do not replace references in MSR Rules that keep unchanged
    # the following sub should replace all references in rules content, ignore tags with ':'
    rule_xml = re.sub(r'by-ref="' + MSR_NEGATIVE_LOOK_AHEAD + r'([^"]+)"', r'by-ref="{}-\1"'.format(script), rule_xml)
    # Prefix MSR references with 'Common-'
    rule_xml = re.sub(r'by-ref="(' + '|'.join(MSR_2_RULES) + r')"', r'by-ref="Common-\1"'.format(script), rule_xml)
    # Rule can contain (anonymous) classes, so also deal with from-tag
    rule_xml = re.sub(r'from-tag="([^:"]+)"', r'from-tag="{}-\1"'.format(script), rule_xml)

    return new_rule_name, rule_xml


def merge_rules(lgr, script, merged_lgr, ref_mapping, specific=None):
    """
    Merge rules from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :param ref_mapping: The reference mapping from base LGR to new LGR
    :param specific: Merge only a specific rule
    """
    logger.debug("Merge rules")

    for rule in lgr.rules_lookup.values():
        if specific and rule.name != specific:
            continue
        rule_xml = lgr.rules_xml[lgr.rules.index(rule.name)]
        merged_rule_name, merged_rule_xml = rename_rule(rule, rule_xml, script)
        if merged_rule_name in merged_lgr.rules:
            # MSR-2
            continue

        # Replace references in python object and XML
        new_ref = [ref_mapping.get(script, {}).get(x, x) for x in rule.references]
        merged_rule_xml = re.sub(r'(?<!by-)ref="([^"]+)"', r'ref="{}"'.format(" ".join(new_ref)), merged_rule_xml)

        merged_lgr.rules.append(merged_rule_name)
        merged_lgr.rules_xml.append(merged_rule_xml)


def rename_class(classe, class_xml, script):
    """
    Prefix class name or reference with script

    :param classe: The class 
    :param class_xml: The class XML
    :param script:  The LGR script
    :return: Updated class name, updated class XML
    """
    new_class_name = script + '-' + classe.name

    class_xml = re.sub(r'name="([^:"]+)"', r'name="{}-\1"'.format(script), class_xml)
    class_xml = re.sub(r'by-ref="([^"]+)"', r'by-ref="{}-\1"'.format(script), class_xml)
    # ignore tags containing ':'
    class_xml = re.sub(r'from-tag="([^:"]+)"', r'from-tag="{}-\1"'.format(script), class_xml)

    return new_class_name, class_xml


def merge_classes(lgr, script, merged_lgr, ref_mapping):
    """
    Merge classes from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :param ref_mapping: The reference mapping from base LGR to new LGR
    """
    logger.debug("Merge classes")

    for class_name, classe in lgr.classes_lookup.items():
        if class_name not in lgr.classes:
            # fake classes from tags
            continue
        class_xml = lgr.classes_xml[lgr.classes.index(classe.name)]
        merged_class_name, merged_class_xml = rename_class(classe, class_xml, script)

        # Replace references in python object and XML
        new_ref = [ref_mapping.get(script, {}).get(x, x) for x in classe.references]
        merged_class_xml = re.sub(r'(?<!by-)ref="([^"]+)"', r'ref="{}"'.format(" ".join(new_ref)), merged_class_xml)

        merged_lgr.classes.append(merged_class_name)
        merged_lgr.classes_xml.append(merged_class_xml)


def merge_chars(lgr, script, merged_lgr, ref_mapping, previous_scripts):
    """
    Merge chars from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :param ref_mapping: The reference mapping from base LGR to new LGR
    :param previous_scripts: The scripts that has already been processed
    """
    new_variants = []
    merged_chars = set([char for char in merged_lgr.repertoire])
    for char in lgr.repertoire:
        if len(char.cp) == 1 and lgr.unicode_database is not None:
            script_extensions = lgr.unicode_database.get_script_extensions(char.cp[0])
        else:
            script_extensions = []
        new_tags = set(script + '-' + x if ':' not in x else x for x in char.tags) | set(script_extensions)
        existing_char = None
        for merged_char in merged_chars:
            if merged_char == char:
                # Note that we actually want the object from merged_chars, that contains additional information
                # not present on cp, even if Char.__hash__() lets think so.
                # For example, cannot use:
                # if char in merged_chars:
                #   existing_char = char
                existing_char = merged_char
                break

        if existing_char:
            # same cp already in LGR
            existing_char.comment = let_user_choose(existing_char.comment, char.comment)
            existing_char.tags = list(set.union(set(existing_char.tags), set(new_tags)))
            existing_char.references = set.union(set(existing_char.references), set(char.references))

            # if 2 scripts have different variants on a character, we need to add the variants for script 1 as
            # variant on script 2 to keep transitivity (e.g. b is variant of a in script 1, c is variant of a in
            # script 2, we need to set b as c variant and conversely). We do that after processing all code points
            # as the code point for the new variant may not be in the merged LGR in the current iteration.
            new_v1 = set.difference(set(char.get_variants()), set(existing_char.get_variants()))
            new_v2 = set.difference(set(existing_char.get_variants()), set(char.get_variants()))
            # remove cp itself to avoid error with reflexive variants
            for v in new_v1:
                if v.cp == existing_char.cp:
                    new_v1.remove(v)
                    break
            for v in new_v2:
                if v.cp == existing_char.cp:
                    new_v2.remove(v)
                    break
            if new_v1 and new_v2:
                new_variants.append((new_v1, new_v2))

            # add new variants to current code point
            # do not keep new_v1 as reflexive variant may have been removed
            for v in set.difference(set(char.get_variants()), set(existing_char.get_variants())):
                new_ref = [ref_mapping[script].get(x, x) for x in v.references]
                new_when = None
                new_not_when = None
                if v.when:
                    new_when = script + '-' + v.when
                if v.not_when:
                    new_not_when = script + '-' + v.not_when
                merged_lgr.add_variant(existing_char.cp, v.cp, variant_type='blocked',
                                       when=new_when, not_when=new_not_when,
                                       comment=v.comment, ref=new_ref)
                # existing variants comment or references are not updated as it is not really important

            # if when or not-when:
            #  - if existing cp has no concurrent rule or conversely, keep the rule as is (i.e. if existing cp has
            #    no rule but cp has one, keep the cp rule with prefixed with the current script)
            #  - if existing cp has the same when/not-when rules (same name, content is not checked), update cp WLE with
            #    the prefix from this script
            #  - if existing cp has a different rule (not the same name), raise an exception
            existing_when = existing_char.when
            existing_not_when = existing_char.not_when
            # retrieve WLE names
            for other_script in reversed(previous_scripts):
                if existing_char.when:
                    existing_when = re.sub(r'^{}-'.format(other_script), '', existing_when)
                if existing_char.not_when:
                    existing_not_when = re.sub(r'^{}-'.format(other_script), '', existing_not_when)

            if char.when:
                if not existing_when:
                    existing_char.when = script + '-' + char.when
                elif existing_when == char.when:
                    existing_char.when = script + '-' + existing_char.when
                    # add a merged rule
                    matching_script = re.sub(r'-{}$'.format(existing_when), '', existing_char.when)
                    merge_rules(lgr, matching_script, merged_lgr, ref_mapping, specific=existing_when)
                else:
                    raise CharAlreadyExists(char.cp)

            if char.not_when:
                if not existing_not_when:
                    existing_char.not_when = script + '-' + char.not_when
                elif existing_not_when == char.not_when:
                    existing_char.not_when = script + '-' + existing_char.not_when
                    # add a merged rule
                    matching_script = re.sub(r'-{}$'.format(existing_not_when), '', existing_char.not_when)
                    merge_rules(lgr, matching_script, merged_lgr, ref_mapping, specific=existing_not_when)
                else:
                    raise CharAlreadyExists(char.cp)

            continue

        # add new cp in LGR
        when = None
        not_when = None
        if char.when:
            when = script + '-' + char.when
        if char.not_when:
            not_when = script + '-' + char.not_when

        new_ref = [ref_mapping.get(script, {}).get(x, x) for x in char.references]
        merged_lgr.add_cp(char.cp, comment=char.comment, ref=new_ref,
                          tag=list(new_tags),
                          when=when, not_when=not_when)
        for v in char.get_variants():
            when = None
            not_when = None
            if v.when:
                when = script + '-' + v.when
            if v.not_when:
                not_when = script + '-' + v.not_when

            new_ref = [r for r in map(lambda x: ref_mapping[script].get(x, x), v.references)]
            merged_lgr.add_variant(char.cp, v.cp, variant_type='blocked',
                                   comment=v.comment, ref=new_ref,
                                   when=when, not_when=not_when)

    # handle transitivity for variants that differ between scripts
    for var1_list, var2_list in new_variants:
        for v1 in var1_list:
            for v2 in var2_list:
                merged_lgr.add_variant(v1.cp, v2.cp, variant_type='blocked',
                                       comment='New variant for merge to keep transitivity')
                merged_lgr.add_variant(v2.cp, v1.cp, variant_type='blocked',
                                       comment='New variant for merge to keep transitivity')


def merge_lgr_set(lgr_set, name):
    """
    Merge LGRs from a set

    :param lgr_set: The list of LGRs in the set
    :param name: Merged LGR name
    :return: New LGR (merge of LGR set)
    """
    logger.debug("Merge %s", name)

    # order LGRs
    lgr_set.sort(key=lambda x: get_script(x).replace('und-', 'zzz'))

    # Ensure all unicode version are correct
    unicode_version = OrderedDict().fromkeys(lgr.metadata.unicode_version for lgr in lgr_set)
    if len(unicode_version) > 1:
        logger.warning("Different unicode version in set: %s", unicode_version.keys())

    ref_mapping = {}
    metadata = copy.deepcopy(merge_metadata(lgr_set))
    merged_lgr = LGR(name=name, metadata=metadata)
    previous_scripts = []
    for lgr in lgr_set:
        script = get_script(lgr)
        lgr.expand_ranges()

        merge_references(lgr, script, merged_lgr, ref_mapping)
        merge_chars(lgr, script, merged_lgr, ref_mapping, previous_scripts)
        merge_actions(lgr, script, merged_lgr, ref_mapping)
        merge_rules(lgr, script, merged_lgr, ref_mapping)
        merge_classes(lgr, script, merged_lgr, ref_mapping)
        previous_scripts.append(script)

    # XXX As the created merged_lgr is not a valid Python LGR object,
    # we have to serialize it/parse it to get a valid object.

    merged_lgr_xml = StringIO(serialize_lgr_xml(merged_lgr))

    lgr_parser = XMLParser(source=merged_lgr_xml, filename=name)

    return lgr_parser.parse_document()
