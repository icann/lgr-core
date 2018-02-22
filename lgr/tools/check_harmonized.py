#!/bin/env python2
# -*- coding: utf-8 -*-
"""
check_harmonized.py - Check if some LGRs are harmonized (variants cp are transitive and symmetric)
"""
from __future__ import unicode_literals

import logging
from cStringIO import StringIO

from lgr.utils import format_cp
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
                                              _check_harmonized_lgrs(lgrs, lgr))


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


def _check_harmonized_lgrs(lgrs, lgr):
    """
    Check if a LGR is harmonized with other LGRs

    :param lgrs: The other LGRs (can contain the LGR itself)
    :param lgr: The LGR to check
    :return: The check result
    """
    output = ''
    for other_lgr in lgrs:
        harmonized = True
        if other_lgr == lgr:
            continue

        output += '\n## Check harmonization with LGR {}\n'.format(other_lgr)
        output += '### Code points and variants\n'
        output += MD
        transitivity = {}
        for char in lgr.repertoire:
            out_cp, cp_harmonized, cp_transitivity = _check_harmonized_char(other_lgr, char)
            if not cp_harmonized:
                output += 'Code point {} ({}):\n{}'.format(char, format_cp(char.cp), out_cp)
                harmonized = False
            for transitive_cp, transitive_variants in cp_transitivity.items():
                transitivity.setdefault(transitive_cp, []).extend(transitive_variants)

        if len(transitivity) > 0:
            output += MD
            output += '### Transitivity considerations\n'
            output += MD
        for char, variants in transitivity.items():
            for existing_cp in lgr.repertoire:
                if char == existing_cp:
                    output += 'Code point {} ({}) would need variant(s) {}\n'.format(
                        char, format_cp(char.cp), ', '.join(['{} ({})'.format(v, format_cp(v.cp)) for v in variants]))
                    break
                else:
                    'Code point {} ({}) is not in LGR, transitivity could not be achieved\n'.format(char,
                                                                                                    format_cp(char.cp))
        if harmonized:
            output += 'LGRs are harmonized\n'

        output += MD

    return output


def _check_harmonized_char(other_lgr, char):
    """
    Check harmonization of a character in another LGR.

    :param other_lgr: The other LGR to check the code point with
    :param char: The code point to check
    :return: The check result, whether the cp is harmonized with the other LGR,
             required variants per code point for transitivity
    """
    output = ''
    harmonized = True
    transitivity = {}
    for other_char in other_lgr.repertoire:
        if char == other_char:
            break
    else:
        harmonized = False
        output += '  Not in LGR\n'
        return output, harmonized, transitivity

    not_in_other = set.difference(set(char.get_variants()), set(other_char.get_variants()))
    not_in_lgr = set.difference(set(other_char.get_variants()), set(char.get_variants()))
    if not_in_lgr or not_in_other:
        harmonized = False

    for v in not_in_lgr:
        output += '  Missing {}variant {} ({})\n'.format('reflexive ' if v.cp == char.cp else '',
                                                         v, format_cp(v.cp))

    for v in not_in_other:
        output += '  Additional {}variant {} ({})\n'.format('reflexive ' if v.cp == char.cp else '',
                                                            v, format_cp(v.cp))

    # remove reflexive variants for transitivity
    not_in_lgr = [v for v in not_in_lgr if v.cp != char.cp]
    not_in_other = [v for v in not_in_other if v.cp != char.cp]
    if not_in_lgr and not_in_other:
        # handle transitivity for variants that differ between scripts
        for v1 in not_in_lgr:
            transitivity[v1] = []
            for v2 in not_in_other:
                transitivity[v1].append(v2)
                transitivity.setdefault(v2, []).append(v1)

    return output, harmonized, transitivity
