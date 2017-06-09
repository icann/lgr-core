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

from lgr.exceptions import LGRFormatException
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
    values = set()
    comments = set()
    for version in map(lambda x: x.metadata.version, lgr_set):
        if not version:
            continue
        if version.value:
            values.add(version.value)
        if version.comment:
            comments.add(version.comment)

    return Version('|'.join(values), '|'.join(comments))


def merge_description(lgr_set):
    """
    Merge description from LGR set.

    :param lgr_set: The LGRs in the set
    :return: The merged description object
    """
    # Check that none of the object is None before processing
    description_type = 'text/enriched'
    values = []
    for lgr in lgr_set:
        description = lgr.metadata.description
        script = get_script(lgr)
        if description:
            value = """
Script: '{script}' - MIME-type: '{type}':
{value}
""".format(script=script, type=description.description_type, value=description.value)
            values.append(value)

    return Description('----\n'.join(values), description_type)


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

    scopes = set()
    languages = set()
    for metadata in map(lambda x: x.metadata, lgr_set):
        scopes.update(set(metadata.scopes))
        languages.update(set(metadata.languages))
        output.validity_start = compare_objects(output.validity_start,
                                                metadata.validity_start,
                                                max)
        output.validity_end = compare_objects(output.validity_end,
                                              metadata.validity_end,
                                              min)

        output.unicode_version = compare_objects(output.unicode_version,
                                                 metadata.unicode_version,
                                                 max)

    output.scopes = list(scopes)
    output.languages = list(languages)

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
    ref_mapping.setdefault(script, {})
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


def merge_actions(lgr, script, merged_lgr):
    """
    Merge actions from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    """
    logger.debug("Merge actions")

    for idx in range(len(lgr.actions)):
        action = lgr.actions[idx]
        action_xml = lgr.actions_xml[idx]
        if action in DEFAULT_ACTIONS:
            continue
        action, action_xml = rename_action(action, action_xml, script)

        merged_lgr.actions.append(action)
        merged_lgr.actions_xml.append(action_xml)


def rename_rule(rule, rule_xml, script):
    """
    Prefix rule name or reference with script

    :param rule: The rule 
    :param rule_xml: The rule XML
    :param script:  The LGR script
    :return: Updated rule, updated rule XML
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


def merge_rules(lgr, script, merged_lgr):
    """
    Merge rules from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :return: (list of rules name, list of XML rules)
    """
    logger.debug("Merge rules")

    for rule in lgr.rules_lookup.values():
        rule_xml = lgr.rules_xml[lgr.rules.index(rule.name)]
        rule_name, rule_xml = rename_rule(rule, rule_xml, script)
        if rule_name in merged_lgr.rules:
            # MSR-2
            continue
        merged_lgr.rules.append(rule_name)
        merged_lgr.rules_xml.append(rule_xml)


def rename_class(classe, class_xml, script):
    """
    Prefix class name or reference with script

    :param classe: The class 
    :param class_xml: The class XML
    :param script:  The LGR script
    :return: Updated class, updated class XML
    """
    new_class_name = script + '-' + classe.name

    class_xml = re.sub(r'name="([^:"]+)"', r'name="{}-\1"'.format(script), class_xml)
    class_xml = re.sub(r'by-ref="([^"]+)"', r'by-ref="{}-\1"'.format(script), class_xml)
    # ignore tags containing ':'
    class_xml = re.sub(r'from-tag="([^:"]+)"', r'from-tag="{}-\1"'.format(script), class_xml)

    return new_class_name, class_xml


def merge_classes(lgr, script, merged_lgr):
    """
    Merge classes from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :return: (list of classes name, list of XML classes)
    """
    logger.debug("Merge classes")

    for class_name, classe in lgr.classes_lookup.items():
        if class_name not in lgr.classes:
            # fake classes from tags
            continue
        class_xml = lgr.classes_xml[lgr.classes.index(classe.name)]
        class_name, class_xml = rename_class(classe, class_xml, script)
        merged_lgr.classes.append(class_name)
        merged_lgr.classes_xml.append(class_xml)


def merge_chars(lgr, script, merged_lgr, ref_mapping):
    """
    Merge chars from LGR set.

    :param lgr: A LGR from the set
    :param script: The LGR script
    :param merged_lgr: The merged LGR
    :param ref_mapping: The reference mapping from base LGR to new LGR
    """
    new_variants = []
    merged_codepoints = set([cp for cp in merged_lgr.repertoire])
    for cp in lgr.repertoire:
        if len(cp.cp) == 1 and lgr.unicode_database is not None:
            script_extensions = lgr.unicode_database.get_script_extensions(cp.cp[0])
        else:
            script_extensions = []
        new_tags = set(script + '-' + x if ':' not in x else x for x in cp.tags) | set(script_extensions)
        existing_cp = None
        if not cp.when and not cp.not_when:
            # when and not-when are renamed per script, cannot get same cp
            # TODO won't work if there is twice the same script but we will also have already exists errors
            for merged_cp in merged_codepoints:
                if merged_cp == cp:
                    # Note that we actually want the object from merged_codepoints, that contains additional information
                    # not present on cp, even if Char.__hash__() lets think so.
                    # For example, cannot use:
                    # if cp in merged_codepoints:
                    #   existing_cp = cp
                    existing_cp = merged_cp
                    break
        if existing_cp:
            # same cp already in LGR
            existing_cp.comment = let_user_choose(existing_cp.comment, cp.comment)
            existing_cp.tags = list(set.union(set(existing_cp.tags), set(new_tags)))
            existing_cp.references = set.union(set(existing_cp.references), set(cp.references))

            # if 2 scripts have different variants on a character, we need to add the variants for script 1 as
            # variant on script 2 to keep transitivity (e.g. b is variant of a in script 1, c is variant of a in
            # script 2, we need to set b as c variant and conversely). We do that after processing all code points
            # as the code point for the new variant may not be in the merged LGR in the current iteration.
            new_v1 = set.difference(set(cp.get_variants()), set(existing_cp.get_variants()))
            new_v2 = set.difference(set(existing_cp.get_variants()), set(cp.get_variants()))
            # remove cp itself to avoid error with reflexive variants
            for v in new_v1:
                if v.cp == existing_cp.cp:
                    new_v1.remove(v)
                    break
            for v in new_v2:
                if v.cp == existing_cp.cp:
                    new_v2.remove(v)
                    break
            if new_v1 and new_v2:
                new_variants.append((new_v1, new_v2))

            # add new variants to current code point
            # do not keep new_v1 as reflexive variant may have been removed
            for v in set.difference(set(cp.get_variants()), set(existing_cp.get_variants())):
                new_ref = [ref_mapping[script].get(x, x) for x in v.references]
                new_when = None
                new_not_when = None
                if v.when:
                    new_when = script + '-' + v.when
                if v.not_when:
                    new_not_when = script + '-' + v.not_when
                merged_lgr.add_variant(existing_cp.cp, v.cp, variant_type='blocked',
                                       when=new_when, not_when=new_not_when,
                                       comment=v.comment, ref=new_ref)

            # existing variants comment or references are note updated as it is not really important
            continue

        # add new cp in LGR
        when = None
        not_when = None
        if cp.when:
            when = script + '-' + cp.when
        if cp.not_when:
            not_when = script + '-' + cp.not_when

        new_ref = [r for r in map(lambda x: ref_mapping[script].get(x, x), cp.references)]
        merged_lgr.add_cp(cp.cp, comment=cp.comment, ref=new_ref,
                          tag=list(new_tags),
                          when=when, not_when=not_when)
        for v in cp.get_variants():
            when = None
            not_when = None
            if v.when:
                when = script + '-' + v.when
            if v.not_when:
                not_when = script + '-' + v.not_when

            new_ref = [r for r in map(lambda x: ref_mapping[script].get(x, x), v.references)]
            merged_lgr.add_variant(cp.cp, v.cp, variant_type='blocked',
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

    ref_mapping = {}
    metadata = copy.deepcopy(merge_metadata(lgr_set))
    merged_lgr = LGR(name=name, metadata=metadata)
    for lgr in lgr_set:
        script = get_script(lgr)
        lgr.expand_ranges()

        merge_references(lgr, script, merged_lgr, ref_mapping)
        merge_chars(lgr, script, merged_lgr, ref_mapping)
        merge_actions(lgr, script, merged_lgr)
        merge_rules(lgr, script, merged_lgr)
        merge_classes(lgr, script, merged_lgr)

    # XXX As the created merged_lgr is not a valid Python LGR object,
    # we have to serialize it/parse it to get a valid object.

    merged_lgr_xml = StringIO(serialize_lgr_xml(merged_lgr))

    lgr_parser = XMLParser(source=merged_lgr_xml, filename=name)

    return lgr_parser.parse_document()
