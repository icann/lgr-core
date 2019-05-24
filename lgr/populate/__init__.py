# -*- coding: utf-8 -*-
"""
__init__.py - Populate variants in an LGR
"""
from __future__ import unicode_literals

import logging

from lgr.exceptions import NotInLGR
from lgr.validate.symmetry import check_symmetry
from lgr.validate.transitivity import check_transitivity
from lgr.utils import format_cp

logger = logging.getLogger(__name__)


def populate_lgr(lgr):
    """
    Populate an LGR with missing variants, and fix symmetry and transitivity

    :param lgr: The LGR to be populated.
    :return: Result of checks and summary as a string
    """
    # not in LGR variants
    for a in lgr.repertoire:
        for b in a.get_variants():
            try:
                lgr.get_variants(b.cp)
            except NotInLGR:
                logger.info("Add missing code point '{}' in LGR as it is a variant of '{}'".format(
                    format_cp(b.cp), format_cp(a.cp)))
                lgr.add_cp(b.cp)
                # add current code point as variant for missing code point
                logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                         format_cp(b.cp)))
                lgr.add_variant(b.cp, a.cp, variant_type='blocked')

    # Need to ignore rules because me nay not be able to get rules symmetry
    while not check_symmetry(lgr, {'ignore_rules': True})[0] or not check_transitivity(lgr, None)[0]:
        # symmetry
        _add_symmetry(lgr)

        # transitivity
        _add_transitivity(lgr)

    # handle the case where all problems are solved except symmetry rules. Do it once as this can be solved in one
    # iteration after all other symmetry problems have been solved and we don't want loop as some may still not be
    # solved (e.g. symmetric variant already has a when (resp. not-when) rule not matching the variant when (resp.
    # not when) rule)
    if not check_symmetry(lgr, {'ignore_rules': False})[0]:
        _add_symmetry(lgr)


def _add_symmetry(lgr):
    for a in lgr.repertoire:
        for b in a.get_variants():
            # Variant is defined in repertoire
            # let's see if the original character is in its
            # variants
            reverse = []
            for v in lgr.get_variants(b.cp):
                if a.cp == v.cp:
                    reverse.append(v)

            if not reverse:
                logger.info("Add code point '{a}'{rule} as variant of '{b}' for symmetry".format(
                    a=format_cp(a.cp),
                    rule=' with when rule {}'.format(b.when) if b.when else
                         ' with not-when rule {}'.format(b.not_when) if b.not_when else '',
                    b=format_cp(b.cp)))
                # add when/not_when rules on along with new variant
                # new variant is blocked
                lgr.add_variant(b.cp, a.cp, variant_type='blocked', when=b.when, not_when=b.not_when)
                continue  # next steps will add rules if variant already existed

            # Variant is defined in repertoire and original character is in its variants,
            # let's see if variant and reverse variant have the same contextual rules
            when_rule = None
            not_when_rule = None
            for r in reverse:
                if r.when:
                    when_rule = r.when
                if r.not_when:
                    not_when_rule = r.not_when

            if b.when and when_rule and b.when != when_rule:
                logger.warning("Could not achieve rule symmetry for variant '{}' of code point '{}' as it already has "
                               "a when rule".format(format_cp(a.cp), format_cp(b.cp)))
            elif b.when and not when_rule:
                # if already a when rule, do do not update reverse
                #     => we may not be able to get symmetry if reverse.when != b.when
                if not_when_rule:
                    logger.info("Add code point '{}' as variant of '{}' for contextual rule when symmetry".format(
                        format_cp(a.cp), format_cp(b.cp)))
                    # need to add another variant as we cannot have both when and not-when on the same code point
                    lgr.add_variant(b.cp, a.cp, variant_type='blocked', when=b.when)
                else:
                    # there can only be one variant in reverse as max is 2 with when and not-when
                    r = reverse[0]
                    logger.info("Update variant '{}' of code point '{}' for contextual rule when symmetry".format(
                        format_cp(r.cp), format_cp(b.cp)))
                    # remove variant then replace it with the one with when rule
                    lgr.del_variant(b.cp, r.cp)
                    lgr.add_variant(b.cp, r.cp, variant_type=r.type, when=b.when, comment=r.comment,
                                    ref=r.references)

            if b.not_when and not_when_rule and b.not_when != not_when_rule:
                logger.warning("Could not achieve rule symmetry for variant '{}' of code point '{}' as it already has "
                               "a not-when rule".format(format_cp(a.cp), format_cp(b.cp)))
            elif b.not_when and not not_when_rule:
                # if already a not_when rule, do do not update reverse
                #     => we may not be able to get symmetry if reverse.not_when != b.not_when
                if when_rule:
                    logger.info("Add code point '{}' as variant of '{}' for contextual rule not-when symmetry".format(
                        format_cp(a.cp), format_cp(b.cp)))
                    # need to add another variant as we cannot have both when and not-when on the same code point
                    lgr.add_variant(b.cp, a.cp, variant_type='blocked', not_when=b.not_when)
                else:
                    # there can only be one variant in reverse as max is 2 with when and not-when
                    r = reverse[0]
                    logger.info("Update variant '{}' of code point '{}' for contextual rule not-when symmetry".format(
                        format_cp(r.cp), format_cp(b.cp)))
                    # remove variant then replace it with the one with not_when rule
                    lgr.del_variant(b.cp, r.cp)
                    lgr.add_variant(b.cp, r.cp, variant_type=r.type, not_when=b.not_when, comment=r.comment,
                                    ref=r.references)


def _add_transitivity(lgr):
    for a in lgr.repertoire:
        for b in a.get_variants():
            for c in [var for var in lgr.get_variants(b.cp) if var.cp != a.cp]:
                # Iterate through all second-level variants
                # which are not the original code point
                if c.cp not in [var.cp for var in a.get_variants()]:
                    logger.info("Add code point '{}' as variant of '{}' for transitivity with '{}'".format(
                        format_cp(c.cp), format_cp(a.cp), format_cp(b.cp)))
                    lgr.add_variant(a.cp, c.cp, variant_type='blocked')
