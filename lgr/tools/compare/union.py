# -*- coding: utf-8 -*-
"""
union.py - Union two LGRs.
"""
from __future__ import unicode_literals

import copy
import logging
from datetime import date

from lgr.tools.compare.utils import VariantProperties, compare_objects

from lgr.char import CharBase
from lgr.core import LGR
from lgr.metadata import Metadata, Version, Description, ReferenceManager
from lgr.utils import let_user_choose

logger = logging.getLogger(__name__)


def union_version(first, second):
    """
    Union two version objects.
    :param first: First version object to union.
    :param second: Other version object to union.
    :return: New object.
    """
    # Check that none of the object is None before processing
    if first is None:
        return second
    if second is None:
        return first

    value = let_user_choose(first.value, second.value)
    comment = let_user_choose(first.comment, second.comment)

    return Version(value, comment)


def union_description(first, second):
    """
    Union two description objects.
    :param first: First object to union.
    :param second: Other object to union.
    :return: New object.
    """
    # Check that none of the object is None before processing
    if first is None:
        return second
    if second is None:
        return first

    description_type = 'text/enriched'
    value = """
Original MIME-type for first description: '{0}'.
{1}

----

Original MIME-type for second description: '{2}'.
{3}
""".format(first.description_type, first.value,
           second.description_type, second.value)

    return Description(value, description_type)


def union_metadata(first, second):
    """
    Union two metadata.

    :param first: The first metadata object to union.
    :param second: The other metadata object to union.
    :return: A new metadata object.
    """
    logger.debug("Union of metadata")

    output = Metadata()

    if first.version is not None:
        output.version = union_version(first.version, second.version)
    if first.description is not None:
        output.description = union_description(first.description,
                                               second.description)

    output.scopes = set.union(set(first.scopes), set(first.scopes))
    output.languages = set.union(set(first.languages),
                                 set(second.languages))

    output.date = date.today().isoformat()
    output.validity_start = compare_objects(first.validity_start,
                                            second.validity_start,
                                            max)
    output.validity_end = compare_objects(first.validity_end,
                                          second.validity_end,
                                          min)

    output.unicode_version = compare_objects(first.unicode_version,
                                             second.unicode_version,
                                             max)

    return output


def union_reference_manager(first, second):
    """
    Union two reference managers.

    :param first: The first object to union.
    :param second: The other object to union.
    :return: A new reference manager object.
    """
    first_ref = {r['value'] for r in first.values()}
    second_ref = {r['value'] for r in second.values()}

    output = ReferenceManager()

    for ref in set.union(first_ref, second_ref):
        output.add_reference(ref)

    return output


def union_char(lgr, first, second):
    """
    Union two chars with same CP.

    :param lgr: The produced LGR.
    :param first: The first object to union.
    :param second: The other object to union.
    """
    comment = let_user_choose(first.comment, second.comment)

    tags = set.union(set(first.tags), set(second.tags))

    lgr.add_cp(first.cp,comment=comment, tag=tags)

    for v in set.union(set(first.get_variants()), set(second.get_variants())):
        lgr.add_variant(first.cp, v.cp, variant_type=v.type,
                        when=v.when, not_when=v.not_when,
                        comment=v.comment)


def union_actions(lgr1, lgr2):
    """
    Union two action lists.

    :param lgr1: First LGR to union.
    :param lgr2: Second LGR to union.
    :return: (list of actions, list of XML actions)
    """
    logger.debug("Union of actions")

    # Union of actions:
    # Concat both action lists

    actions = list(set.union(set(lgr1.actions), set(lgr2.actions)))
    actions_xml = lgr1.actions_xml + lgr2.actions_xml

    return actions, actions_xml


def union_rules(lgr1, lgr2):
    """
    Union two rule lists.

    :param lgr1: First LGR to union.
    :param lgr2: Second LGR to union.
    :return: (list of rules, list of XML rules)
    """
    logger.debug("Union of rules")

    # Union of rules:
    # - Keep rules from both LGRs.
    # - If rule with same name in both LGRs:
    #   - Append both elements to final LGR (rename using _1 and _2).

    rules = []
    rules_xml = []

    rules_lgr1 = frozenset(lgr1.rules)
    rules_lgr2 = frozenset(lgr2.rules)

    # Compute intersection of rules
    for rule_name in rules_lgr1 & rules_lgr2:
        rule_1 = lgr1.rules_xml[lgr1.rules.index(rule_name)]
        rule_2 = lgr2.rules_xml[lgr2.rules.index(rule_name)]

        rule_1 = rule_1.replace(rule_name, rule_name + '_1')
        rule_2 = rule_2.replace(rule_name, rule_name + '_2')

        rules_xml.append(rule_1)
        rules_xml.append(rule_2)

        rules.append(rule_name + '_1')
        rules.append(rule_name + '_2')

    for rule_name in rules_lgr1 - rules_lgr2:
        rules_xml.append(lgr1.rules_xml[lgr1.rules.index(rule_name)])
        rules.append(rule_name)

    for rule_name in rules_lgr2 - rules_lgr1:
        rules_xml.append(lgr2.rules_xml[lgr2.rules.index(rule_name)])
        rules.append(rule_name)

    return rules, rules_xml


def union_classes(lgr1, lgr2):
    """
    Union two class lists.

    :param lgr1: First LGR to union.
    :param lgr2: Second LGR to union.
    :return: (list of classes, list of XML classes)
    """
    logger.debug("Union of classes")

    # Union of classes:
    # - Keep classes from both LGRs.
    # - If class with same name in both LGRs:
    #   - Append both elements to final LGR (rename using _1 and _2).

    classes = []
    classes_xml = []

    classes_lgr1 = frozenset(lgr1.classes)
    classes_lgr2 = frozenset(lgr2.classes)

    # Compute intersection of classes
    for class_name in classes_lgr1 & classes_lgr2:
        class_1 = lgr1.classes_xml[lgr1.classes.index(class_name)]
        class_2 = lgr2.classes_xml[lgr2.classes.index(class_name)]

        class_1 = class_1.replace(class_name, class_name + '_1')
        class_2 = class_2.replace(class_name, class_name + '_2')

        classes_xml.append(class_1)
        classes_xml.append(class_2)

        classes.append(class_name + '_1')
        classes.append(class_name + '_2')

    # Append all other classes
    for class_name in classes_lgr1 - classes_lgr2:
        classes_xml.append(lgr1.classes_xml[lgr1.classes.index(class_name)])
        classes.append(class_name)

    for class_name in classes_lgr2 - classes_lgr1:
        classes_xml.append(lgr2.classes_xml[lgr2.classes.index(class_name)])
        classes.append(class_name)

    return classes, classes_xml


def union_lgrs(lgr1, lgr2):
    """
    Compute the union of 2 LGRs and returns a valid LGR.

    Note: Ranges have to be expanded before calling this function.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :return: New LGR: union of two inputs.
    """
    name = 'Union of %s and %s' % (lgr1.name, lgr2.name)

    logger.debug("Union of %s", name)

    lgr1.expand_ranges()
    lgr2.expand_ranges()

    # Note: We need to create a copy (copy.deepcopy) for some elements
    # otherwise they could reference the original objects.

    metadata = copy.deepcopy(union_metadata(lgr1.metadata, lgr2.metadata))
    lgr = LGR(name=name, metadata=metadata)

    # No need to copy references, they are new objects
    references = union_reference_manager(lgr1.reference_manager,
                                         lgr2.reference_manager)
    lgr.reference_manager = references

    first_cps = {c.cp for c in lgr1.repertoire}
    second_cps = {c.cp for c in lgr2.repertoire}


    # No need to copy char, they are new objects

    # Compute union of all common code points
    for cp in set.intersection(first_cps, second_cps):
        char1 = lgr1.get_char(cp)
        char2 = lgr2.get_char(cp)

        union_char(lgr, char1, char2)

    # Append all other code points
    for cp in set.difference(first_cps, second_cps):
        char = lgr1.get_char(cp)

        lgr.add_cp(char.cp,
                   comment=char.comment,
                   #ref=char.references,
                   tag=char.tags,
                   when=char.when, not_when=char.not_when)

    for cp in set.difference(second_cps, first_cps):
        char = lgr2.get_char(cp)

        lgr.add_cp(char.cp,
                   comment=char.comment,
                   #ref=char.references,
                   tag=char.tags,
                   when=char.when, not_when=char.not_when)

    (actions, actions_xml) = union_actions(lgr1, lgr2)
    lgr.actions = copy.deepcopy(actions)
    lgr.actions_xml = actions_xml

    (rules, rules_xml) = union_rules(lgr1, lgr2)
    lgr.rules = copy.deepcopy(rules)
    lgr.rules_xml = rules_xml

    (classes, classes_xml) = union_classes(lgr1, lgr2)
    lgr.classes = copy.deepcopy(classes)
    lgr.classes_xml = classes_xml

    return lgr
