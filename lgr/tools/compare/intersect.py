# -*- coding: utf-8 -*-
"""
intersect.py - Intersect two LGRs.
"""
from __future__ import unicode_literals

import copy
import logging
from datetime import date

from lgr.tools.compare.utils import compare_objects

from lgr.char import CharBase
from lgr.core import LGR
from lgr.metadata import Metadata, Version, Description, ReferenceManager
from lgr.utils import let_user_choose

logger = logging.getLogger(__name__)


def intersect_version(first, second):
    """
    Intersect two version objects.
    :param first: First version object to intersect with.
    :param second: Other version object to intersect with.
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


def intersect_description(first, second):
    """
    Intersect two description objects.
    :param first: First object to intersect with.
    :param second: Other object to intersect with.
    :return: New object.
    """
    # Check that none of the object is None before processing
    if first is None:
        return second
    if second is None:
        return first

    if first.description_type == second.description_type:
        # Same MIME types, can merge content
        value = let_user_choose(first.value, second.value)
        description_type = first.description_type
    else:
        # MIME types are different, set MIME type to text
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


def intersect_metadata(first, second):
    """
    Intersect two metadata.

    :param first: The first metadata object to intersect with.
    :param second: The other metadata object to intersect with.
    :return: A new metadata object.
    """
    output = Metadata()

    output.version = intersect_version(first.version, second.version)
    output.description = intersect_description(first.description,
                                               second.description)

    output.scopes = set.intersection(set(first.scopes), set(first.scopes))
    output.languages = set.intersection(set(first.languages),
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


def intersect_reference_manager(first, second):
    """
    Intersect two reference managers.

    :param first: The first object to intersect with.
    :param second: The other object to intersect with.
    :return: A new reference manager object.
    """
    first_ref = {r['value'] for r in first.values()}
    second_ref = {r['value'] for r in second.values()}

    output = ReferenceManager()

    for ref in set.intersection(first_ref, second_ref):
        output.add_reference(ref)

    return output


def intersect_char(lgr, first, second):
    """
    Intersect two chars with same CP.

    :param lgr: The produced LGR.
    :param first: The first object to intersect with.
    :param second: The other object to intersect with.
    """
    comment = let_user_choose(first.comment, second.comment)

    tags = list(set.intersection(set(first.tags), set(second.tags)))

    lgr.add_cp(first.cp, comment=comment, tag=tags)

    variant_first = {(v.cp, v.when, v.not_when) for v in first.get_variants()}
    variant_second = {(v.cp, v.when, v.not_when) for v in second.get_variants()}

    for v in set.intersection(variant_first, variant_second):
        lgr.add_variant(first.cp, v[0], when=v[1], not_when=v[2])


def intersect_actions(lgr1, lgr2):
    """
    Intersect two action lists.

    :param lgr1: First LGR to intersect with.
    :param lgr2: Second LGR to intersect with.
    :return: (list of actions, list of XML actions)
    """
    logger.debug("Intersection of actions")

    # Intersection of actions:
    # - keep same actions.

    actions = list(set.intersection(set(lgr1.actions), set(lgr2.actions)))
    actions_xml = [lgr1.actions_xml[lgr1.actions.index(a)] for a in actions]

    return actions, actions_xml


def intersect_rules(lgr1, lgr2):
    """
    Intersect two rule lists.

    :param lgr1: First LGR to intersect with.
    :param lgr2: Second LGR to intersect with.
    :return: (list of rules, list of XML rules)
    """
    logger.debug("Intersection of rules")

    # Intersection of rules:
    # - keep rules with same name in both LGRs.
    # - append both elements to final LGR (rename using _1 and _2).

    rules = []
    rules_xml = []

    for rule_name in frozenset(lgr1.rules) & frozenset(lgr2.rules):
        rule_1 = lgr1.rules_xml[lgr1.rules.index(rule_name)]
        rule_2 = lgr2.rules_xml[lgr2.rules.index(rule_name)]

        if rule_1 == rule_2:
            rules_xml.append(rule_1)
            rules.append(rule_name)
            continue

        rule_1 = rule_1.replace(rule_name, rule_name + '_1')
        rule_2 = rule_2.replace(rule_name, rule_name + '_2')

        rules_xml.append(rule_1)
        rules_xml.append(rule_2)

        rules.append(rule_name + '_1')
        rules.append(rule_name + '_2')

    return rules, rules_xml


def intersect_classes(lgr1, lgr2):
    """
    Intersect two class lists.

    :param lgr1: First LGR to intersect with.
    :param lgr2: Second LGR to intersect with.
    :return: (list of classes, list of XML classes)
    """
    logger.debug("Intersection of classes")

    # Intersection of classes:
    # - keep classes with same name in both LGRs.
    # - append both elements to final LGR (rename using _1 and _2).

    classes = []
    classes_xml = []
    for class_name in frozenset(lgr1.classes) & frozenset(lgr2.classes):
        class_1 = lgr1.classes_xml[lgr1.classes.index(class_name)]
        class_2 = lgr2.classes_xml[lgr2.classes.index(class_name)]

        if class_1 == class_2:
            classes_xml.append(class_1)
            classes.append(class_name)
            continue

        class_1 = class_1.replace(class_name, class_name + '_1')
        class_2 = class_2.replace(class_name, class_name + '_2')

        classes_xml.append(class_1)
        classes_xml.append(class_2)

        classes.append(class_name + '_1')
        classes.append(class_name + '_2')

    return classes, classes_xml


def intersect_lgrs(lgr1, lgr2):
    """
    Compute the intersection of 2 LGRs and returns a valid LGR.

    Note: Ranges have to be expanded before calling this function.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :return: New LGR: intersection of two inputs.
    """
    name = 'Intersection of %s and %s' % (lgr1.name, lgr2.name)

    lgr1.expand_ranges()
    lgr2.expand_ranges()

    # Note: We need to create a copy (copy.deepcopy) for some elements
    # otherwise they could reference the original objects.

    metadata = copy.deepcopy(intersect_metadata(lgr1.metadata, lgr2.metadata))
    lgr = LGR(name=name, metadata=metadata)

    # No need to copy references, they are new objects
    references = intersect_reference_manager(lgr1.reference_manager,
                                             lgr2.reference_manager)
    lgr.reference_manager = references

    first_cps = {c.cp for c in lgr1.repertoire}
    second_cps = {c.cp for c in lgr2.repertoire}

    # No need to copy char, they are new objects
    for cp in set.intersection(first_cps, second_cps):
        char1 = lgr1.get_char(cp)
        char2 = lgr2.get_char(cp)

        intersect_char(lgr, char1, char2)

    (actions, actions_xml) = intersect_actions(lgr1, lgr2)
    lgr.actions = copy.deepcopy(actions)
    lgr.actions_xml = actions_xml

    (rules, rules_xml) = intersect_rules(lgr1, lgr2)
    lgr.rules = copy.deepcopy(rules)
    lgr.rules_xml = rules_xml

    (classes, classes_xml) = intersect_classes(lgr1, lgr2)
    lgr.classes = copy.deepcopy(classes)
    lgr.classes_xml = classes_xml

    return lgr
