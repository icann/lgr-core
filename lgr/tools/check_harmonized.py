#!/bin/env python2
# -*- coding: utf-8 -*-
"""
check_harmonized.py - Check if some LGRs are harmonized (variants cp are transitive and symmetric)
"""
from __future__ import unicode_literals

import logging
from cStringIO import StringIO

from lgr.utils import format_cp
from lgr.exceptions import NotInLGR
from lgr.validate.transitivity import check_transitivity
from lgr.validate.symmetry import check_symmetry

MD = "```\n"


def check_harmonized(lgrs):
    """
    Check LGR variants symmetry and transitivity and then check if LGRs are harmonized with each other

    :param lgrs: The LGRs to check
    :return: The check result
    """
    for lgr in lgrs:
        yield '\n# Check LGR {}\n{}{}'.format(lgr,
                                              _check_lgr_variants(lgr),
                                              _check_harmonized_with_lgrs(lgr, lgrs))


def _check_lgr_variants(lgr):
    """
    Check LGR variants for symmetry and transitivity

    :param lgr: The LGR to check
    :return: The check result
    """
    output = ''
    # Configure log system to redirect validation logs to local attribute
    log_output = StringIO()
    ch = logging.StreamHandler(log_output)
    ch.setLevel(logging.INFO)
    validation_logger = logging.getLogger('lgr.validate')
    # Configure module logger - since user may have disabled the 'lgr' logger,
    # reset its level
    validation_logger.addHandler(ch)
    validation_logger.setLevel('WARNING')
    check_symmetry(lgr, None)
    result = log_output.getvalue()
    if result:
        output = '\n## Check variants symmetry\n{md}{r}{md}'.format(r=result, md=MD)

    # reset log_output
    log_output.truncate(0)
    log_output.seek(0)  # for py3
    check_transitivity(lgr, None)
    result = log_output.getvalue()
    if result:
        output += '\n## Check variants transitivity\n{md}{r}{md}'.format(r=result, md=MD)

    return output


def _check_harmonized_with_lgrs(lgr, lgrs):
    """
    Ensure that `lgr` is harmonized with each of the LGR contained in `lgrs`.

    :param lgr: The LGR to consider.
    :param lgrs: List of other LGRs to check (`lgr` included).
    :return: Check result.
    """
    output = ''
    for other_lgr in lgrs:
        if lgr == other_lgr:
            continue
        output += _check_harmonized_two_lgrs(lgr, other_lgr)
    return output


def _check_harmonized_two_lgrs(first_lgr, second_lgr):
    """
    Check if a LGR is harmonized against another LGR.

    :param first_lgr: The first LGR to be used as a reference.
    :param second_lgr: The second LGR to check.
    :return: The check result
    """
    output = ''
    harmonized = True

    output += '\n## Check of harmonization with LGR {}\n'.format(second_lgr)
    output += '### Code points and variants\n'
    output += MD
    for char in first_lgr.repertoire:
        try:
            other_char = second_lgr.get_char(char.cp)
        except NotInLGR:
            # Do not consider code points not present on other LGRs
            continue
        check_result, cp_harmonized = _check_harmonized_char(char, other_char)
        if not cp_harmonized:
            output += 'Code point {} ({}):\n{}'.format(char, format_cp(char.cp), check_result)
            harmonized = False

    if harmonized:
        output += 'LGRs are harmonized\n'

    output += MD

    return output


def _check_harmonized_char(char, other_char):
    """
    Check harmonization of a two chars.

    :param char: The reference code point to check.
    :param other_char: The char to check against.
    :return: The check result, whether the char is harmonized with the other char.
    """
    output = ''
    harmonized = True

    not_in_other = set.difference(set(char.get_variants()), set(other_char.get_variants()))
    not_in_lgr = set.difference(set(other_char.get_variants()), set(char.get_variants()))
    if not_in_lgr or not_in_other:
        harmonized = False

    for v in not_in_lgr:
        output += '  Additional {}variant {} ({})\n'.format('reflexive ' if v.cp == char.cp else '',
                                                            v, format_cp(v.cp))

    for v in not_in_other:
        output += '  Missing {}variant {} ({})\n'.format('reflexive ' if v.cp == char.cp else '',
                                                         v, format_cp(v.cp))

    return output, harmonized
