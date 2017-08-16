# -*- coding: utf-8 -*-
"""
diff.py - Compute (textual) diff of two LGRs.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.compare.utils import display_variant, VariantProperties

from lgr.utils import format_cp

logger = logging.getLogger(__name__)


def compare_sets(first, second, format_fct=str):
    """
    Utility function to compare two sets.

    :param first: First set.
    :param second: Second set.
    :param format_fct: Format function.
    :return: Text comparison.
    """
    only_first = list(first - second)
    only_second = list(second - first)
    common = list(first & second)

    if len(common) == 0:
        common = 'None'
    else:
        common = format_fct(common)

    return """Values only in first LGR: {}.
Values only in second LGR: {}.
Common values: {}.
""".format(format_fct(only_first),
           format_fct(only_second),
           common)


def compare_things(first, second, name, is_set=False, format_fct=unicode,
                   show_same=True):
    """
    Compare two 'things'.

    :param first: First object.
    :param second: Second object.
    :param is_set: If True, also compare objects as sets.
    :param format_fct: Format function.
    :param show_same: Show values even if they are identical.
    :return: Text comparison.
    """
    if first != second:
        if is_set:
            return """
{} values differ:
{}
""".format(name.capitalize(), compare_sets(first, second, format_fct))
        else:
            return """
{} values differ.
First LGR: '{}'.
Second LGR: '{}'.
""".format(name.capitalize(), format_fct(first), format_fct(second))

    else:
        if show_same:
            value = list(first) if is_set else first
            return """
Same {} value for both LGR: '{}'.""".format(name, format_fct(value))
        else:
            return """
Same {} value for both LGR.""".format(name)


def diff_version(first, second):
    """
    Diff two version objects.
    :param first: First version object.
    :param second: Other version object.
    :return: Text comparison.
    """
    output = "Compare Version"

    # Check that none of the object is None before processing
    if first is None:
        output += "\nFirst LGR has no version"
    if second is None:
        output += "\nSecond LGR has no version"

    if first is not None and second is not None:
        output += compare_things(first.value, second.value, "version")
        output += compare_things(first.comment, second.comment, "version comment")

    output += "\n\n"

    return output


def diff_description(first, second):
    """
    Diff two description objects.
    :param first: First object.
    :param second: Other object.
    :return: Text comparison.
    """
    output = "Compare Description"

    # Check that none of the object is None before processing
    if first is None:
        output += "\nFirst LGR has no description"
    if second is None:
        output += "\nSecond LGR has no description"

    if first is not None and second is not None:

        output += compare_things(first.description_type, second.description_type,
                                 "description type")
        output += compare_things(first.value, second.value, "description")

    output += "\n\n"
    return output


def diff_metadata(first, second, is_set=False):
    """
    Diff two metadata objects.

    :param first: The first metadata object.
    :param second: The other metadata object.
    :param is_set: Whether the metadata are compared for LGR sets
    :return: Text comparison.
    """
    if not is_set:
        output = "** Compare Metadata **\n\n"
    else:
        output = "** Compare Metadata on merged LGRs **\n\n"

    output += diff_version(first.version, second.version)
    output += diff_description(first.description, second.description)

    first_scope_set = set(first.scopes)
    second_scope_set = set(second.scopes)

    output += compare_things(first_scope_set, second_scope_set, "scopes", True,
                             lambda s: ", ".join(map(unicode, s)))

    first_lang_set = set(first.languages)
    second_lang_set = set(second.languages)

    output += compare_things(first_lang_set, second_lang_set, "languages", True)

    output += compare_things(first.date, second.date, "date")
    output += compare_things(first.validity_start, second.validity_start,
                             "validity start")
    output += compare_things(first.validity_end, second.validity_end,
                             "validity end")
    output += compare_things(first.unicode_version, second.unicode_version,
                             "unicode version")

    output += "\n\n"

    return output


def diff_reference_manager(first, second):
    """
    Diff two reference managers.

    :param first: The first object.
    :param second: The other object.
    :return: Text comparison.
    """
    first_ref = {r['value'] for r in first.values()}
    second_ref = {r['value'] for r in second.values()}

    return compare_things(first_ref, second_ref, 'references', True)


def diff_char(first, second):
    """
    Intersect two chars with same CP.

    :param first: The first object.
    :param second: The other object.
    :return: Text comparison.
    """
    output = ""

    output += compare_things(first.comment, second.comment, "comment")
    output += compare_things(first.tags, second.tags, "tags")

    # Must redefine this since __hash__ of Variant does not include comment
    variant_first = {VariantProperties(v.cp, v.type, v.when, v.not_when, v.comment) for v in first.get_variants()}
    variant_second = {VariantProperties(v.cp, v.type, v.when, v.not_when, v.comment) for v in second.get_variants()}

    output += compare_things(variant_first, variant_second, "variants", True,
                             lambda v: ", ".join(map(display_variant, v)))

    return output


def diff_actions(lgr1, lgr2):
    """
    Diff two action lists.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :return: Text comparison.
    """
    actions_1 = [a.disp for a in lgr1.actions]
    actions_2 = [a.disp for a in lgr2.actions]
    return compare_things(set(actions_1), set(actions_2), "actions", True)


def diff_rules(lgr1, lgr2):
    """
    Diff two rule lists.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :return: Text comparison.
    """
    return compare_things(set(lgr1.rules), set(lgr2.rules), "rules", True)


def diff_classes(lgr1, lgr2):
    """
    Diff two class lists.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :return: Text comparison.
    """
    return compare_things(set(lgr1.classes), set(lgr2.classes), "classes", True)


def diff_lgrs(lgr1, lgr2):
    """
    Compare 2 LGRs.

    Returns a text containing results of comparison

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :return: Text comparison.
    """
    output = ""

    lgr1.expand_ranges()
    lgr2.expand_ranges()

    output += diff_metadata(lgr1.metadata, lgr2.metadata)
    output += diff_reference_manager(lgr1.reference_manager,
                                     lgr2.reference_manager)

    output += """


** Compare repertoire **
"""

    first_cps = {c.cp for c in lgr1.repertoire}
    second_cps = {c.cp for c in lgr2.repertoire}

    output += compare_things(first_cps, second_cps, "repertoire", True,
                             format_fct=lambda c: " ".join(map(format_cp, c)),
                             show_same=False)

    output += """


** Compare common code points in repertoire **
"""

    for cp in set.intersection(first_cps, second_cps):
        char1 = lgr1.get_char(cp)
        char2 = lgr2.get_char(cp)

        output += """

Compare code point {}""".format(format_cp(cp))
        output += diff_char(char1, char2)

    output += """


** Compare WLE **
"""

    output += diff_actions(lgr1, lgr2)
    output += diff_rules(lgr1, lgr2)
    output += diff_classes(lgr1, lgr2)

    return output


def diff_lgr_sets(lgr1, lgr2, lgr_set_1, lgr_set_2):
    """
    Compare 2 LGR sets.

    Returns a text containing results of comparison

    :param lgr1: First LGR set.
    :param lgr2: Second LGR set.
    :param lgr_set_1: LGR included in the first LGR set.
    :param lgr_set_2: LGR included in the second LGR set.
    :return: Text comparison.
    """
    output = ""

    def get_scripts(lgr_set, lgr_set_name):
        out = ''
        lgr_scripts = {}
        for lgr in lgr_set:
            try:
                script = lgr.metadata.languages[0]
                if script in lgr_scripts:
                    out += "More than one LGR in set '{set}' match script '{script}'".format(set=lgr_set_name,
                                                                                             script=script)
                lgr_scripts.setdefault(script, []).append(lgr)
            except (AttributeError, IndexError):
                pass

        return lgr_scripts, out

    lgr_scripts_1, out = get_scripts(lgr_set_1, lgr1.name)
    output += out
    lgr_scripts_2, out = get_scripts(lgr_set_2, lgr2.name)
    output += out

    common_script = set(lgr_scripts_1.keys()) & set(lgr_scripts_2.keys())
    for script in set(lgr_scripts_1.keys()) - set(lgr_scripts_2.keys()):
        output += """
Script '{script}' is available in LGR set '{set1}' with LGR '{lgrs}' but not in LGR set '{set2}'.

    """.format(script=script, set1=lgr1.name, set2=lgr2.name,
               lgrs="', '".join([lgr.name for lgr in lgr_scripts_1[script]]))

    for script in set(lgr_scripts_2.keys()) - set(lgr_scripts_1.keys()):
        output += """
Script '{script}' is available in LGR set '{set2}' with LGR '{lgrs}' but not in LGR set '{set1}'.

    """.format(script=script, set1=lgr1.name, set2=lgr2.name,
               lgrs="', '".join([lgr.name for lgr in lgr_scripts_2[script]]))

    # As metadata can be edited, compare them on merged LGR
    output += diff_metadata(lgr1.metadata, lgr2.metadata, is_set=True)

    # compare LGR having the same script from each set
    for script in common_script:
        for l1 in lgr_scripts_1[script]:
            for l2 in lgr_scripts_2[script]:
                # for each script, compare LGRs
                output += """


### Compare LGRs for script {script}: {lgr1} - {lgr2} ###

""".format(script=script, lgr1=l1.name, lgr2=l2.name)
                output += diff_lgrs(l1, l2)

    return output
