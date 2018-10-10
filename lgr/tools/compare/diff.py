# -*- coding: utf-8 -*-
"""
diff.py - Compute (textual) diff of two LGRs.
"""
from __future__ import unicode_literals

from lgr import text_type
from lgr.tools.compare.utils import display_variant, VariantProperties
from lgr.utils import format_cp


def compare_sets(first, second, format_fct=text_type,
                 show_same=False):
    """
    Utility function to compare two sets.

    :param first: First set.
    :param second: Second set.
    :param format_fct: Format function.
    :param show_same: Show common repertoire code points.
    :return: Text comparison.
    """
    only_first = list(first - second)
    only_second = list(second - first)
    common = list(first & second)

    if len(common) == 0:
        common = 'None'
    else:
        common = format_fct(common)

    out = """Values only in first LGR: {}.
Values only in second LGR: {}.
""".format(format_fct(only_first),
           format_fct(only_second))
    if show_same:
        out += """
Common values: {}.
""".format(common)

    return out


def compare_things(first, second, name, is_set=False, format_fct=text_type,
                   show_same=False):
    """
    Compare two 'things'.

    :param first: First object.
    :param second: Second object.
    :param name: Name of the things to compare.
    :param is_set: If True, also compare objects as sets.
    :param format_fct: Format function.
    :param show_same: Show result even if they are identical.
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
{} values differ:
First LGR: '{}'.
Second LGR: '{}'.
""".format(name.capitalize(), format_fct(first), format_fct(second))

    else:
        if show_same:
            value = list(first) if is_set else first
            return """
Same {} value for both LGR: '{}'.""".format(name, format_fct(value))
        else:
            return ''


def diff_version(first, second, show_same=False):
    """
    Diff two version objects.
    :param first: First version object.
    :param second: Other version object.
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    output = ''

    # Check that none of the object is None before processing
    if first is None:
        output += "\nFirst LGR has no version"
    if second is None:
        output += "\nSecond LGR has no version"

    if first is not None and second is not None:
        output += compare_things(first.value, second.value, "version",
                                 show_same=show_same)
        output += compare_things(first.comment, second.comment, "version comment",
                                 show_same=show_same)

    if output:
        output = "Compare Version:" + output + "\n\n"

    return output


def diff_description(first, second, show_same=False):
    """
    Diff two description objects.
    :param first: First object.
    :param second: Other object.
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    output = ''

    # Check that none of the object is None before processing
    if first is None:
        output += "\nFirst LGR has no description"
    if second is None:
        output += "\nSecond LGR has no description"

    if first is not None and second is not None:

        output += compare_things(first.description_type, second.description_type,
                                 "description type",
                                 show_same=show_same)
        output += compare_things(first.value, second.value, "description",
                                 show_same=show_same)

    if output:
        output = "Compare Description:" + output + "\n\n"
    return output


def diff_metadata(first, second, is_set=False, show_same=False):
    """
    Diff two metadata objects.

    :param first: The first metadata object.
    :param second: The other metadata object.
    :param is_set: Whether the metadata are compared for LGR sets
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    output = ''
    output += diff_version(first.version, second.version,
                           show_same=show_same)
    output += diff_description(first.description, second.description,
                               show_same=show_same)

    first_scope_set = set(first.scopes)
    second_scope_set = set(second.scopes)

    output += compare_things(first_scope_set, second_scope_set, "scopes", True,
                             lambda s: ", ".join(map(text_type, s)),
                             show_same=show_same)

    first_lang_set = set(first.languages)
    second_lang_set = set(second.languages)

    output += compare_things(first_lang_set, second_lang_set, "languages", True,
                             show_same=show_same)

    output += compare_things(first.date, second.date, "date",
                             show_same=show_same)
    output += compare_things(first.validity_start, second.validity_start,
                             "validity start",
                             show_same=show_same)
    output += compare_things(first.validity_end, second.validity_end,
                             "validity end",
                             show_same=show_same)
    output += compare_things(first.unicode_version, second.unicode_version,
                             "unicode version",
                             show_same=show_same)

    if output:
        if not is_set:
            output = "** Compare Metadata **\n\n" + output
        else:
            output = "** Compare Metadata on merged LGRs **\n\n" + output

    return output


def diff_reference_manager(first, second, show_same=False):
    """
    Diff two reference managers.

    :param first: The first object.
    :param second: The other object.
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    first_ref = {r['value'] for r in first.values()}
    second_ref = {r['value'] for r in second.values()}

    return compare_things(first_ref, second_ref, 'references', True,
                          show_same=show_same)


def diff_char(first, second, show_same=True):
    """
    Intersect two chars with same CP.

    :param first: The first object.
    :param second: The other object.
    :param show_same: Whether identical char should return something or not.
    :return: Text comparison.
    """
    output = ""

    # Must redefine this since __hash__ of Variant does not include comment
    variant_first = {VariantProperties(v.cp, v.type, v.when, v.not_when, v.comment) for v in first.get_variants()}
    variant_second = {VariantProperties(v.cp, v.type, v.when, v.not_when, v.comment) for v in second.get_variants()}

    if not show_same and \
                    first.comment == second.comment and first.tags == second.tags and variant_first == variant_second:
        return output

    output += compare_things(first.comment, second.comment, "comment",
                             show_same=show_same)
    output += compare_things(first.tags, second.tags, "tags",
                             show_same=show_same)

    output += compare_things(variant_first, variant_second, "variants", True,
                             lambda v: ", ".join(map(display_variant, v)),
                             show_same=show_same)

    return output


def diff_actions(lgr1, lgr2, show_same=False):
    """
    Diff two action lists.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    actions_1 = [a.disp for a in lgr1.actions]
    actions_2 = [a.disp for a in lgr2.actions]
    return compare_things(set(actions_1), set(actions_2), "actions", True,
                          show_same=show_same)


def diff_rules(lgr1, lgr2, show_same=False):
    """
    Diff two rule lists.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    return compare_things(set(lgr1.rules), set(lgr2.rules), "rules", True,
                          show_same=show_same)


def diff_classes(lgr1, lgr2, show_same=False):
    """
    Diff two class lists.

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :param show_same: Show result even if they are identical.
    :return: Text comparison.
    """
    return compare_things(set(lgr1.classes), set(lgr2.classes), "classes", True,
                          show_same=show_same)


def diff_lgrs(lgr1, lgr2, show_same=True):
    """
    Compare 2 LGRs.

    Returns a text containing results of comparison

    :param lgr1: First LGR.
    :param lgr2: Second LGR.
    :param show_same: Show result even if elements are identical..
    :return: Text comparison.
    """
    output = ""

    lgr1.expand_ranges()
    lgr2.expand_ranges()

    output += diff_metadata(lgr1.metadata, lgr2.metadata,
                            show_same=show_same)
    output += diff_reference_manager(lgr1.reference_manager,
                                     lgr2.reference_manager,
                                     show_same=show_same)

    output += """


** Compare repertoire **
"""

    first_cps = {c.cp for c in lgr1.repertoire}
    second_cps = {c.cp for c in lgr2.repertoire}

    output += compare_things(first_cps, second_cps, "repertoire", True,
                             format_fct=lambda c: " ".join(map(format_cp, c)),
                             show_same=show_same)

    output += """


** Compare common code points in repertoire **
"""

    identical = 0
    for cp in set.intersection(first_cps, second_cps):
        char1 = lgr1.get_char(cp)
        char2 = lgr2.get_char(cp)

        diff = diff_char(char1, char2, show_same=show_same)
        if not show_same and not diff:
            identical += 1
        else:
            output += """

    + Compare code point {}""".format(format_cp(cp))
            output += diff

    if not show_same and identical > 0:
        output += """
{} code points are identical""".format(identical)
    output += """

** Compare WLE **
"""

    output += diff_actions(lgr1, lgr2)
    output += diff_rules(lgr1, lgr2)
    output += diff_classes(lgr1, lgr2)

    return output


def diff_lgr_sets(lgr1, lgr2, lgr_set_1, lgr_set_2, show_same=True):
    """
    Compare 2 LGR sets.

    Returns a text containing results of comparison

    :param lgr1: First LGR set.
    :param lgr2: Second LGR set.
    :param lgr_set_1: LGR included in the first LGR set.
    :param lgr_set_2: LGR included in the second LGR set.
    :param show_same: Whether identical char should return something or not.
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
                output += diff_lgrs(l1, l2, show_same=show_same)

    return output
