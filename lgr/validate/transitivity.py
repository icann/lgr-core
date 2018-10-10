# -*- coding: utf-8 -*-
"""
transitivity.py - Check for transitivity
"""
from __future__ import unicode_literals

import logging

from lgr.char import RangeChar
from lgr.utils import format_cp
from lgr.exceptions import NotInLGR

logger = logging.getLogger(__name__)


def check_transitivity(lgr, options):
    """
    Check that all variants are defined in a transitive way.

    If B is a variant of A and C a variant of B, then C must be a variant of A.

    We only check the presence of the code point in the variants, not that all
    properties are identical (type, when, not-when).

    Note: This test assumes the LGR is symmetric.

    :param LGR lgr: The LGR to check.
    :param options: Dictionary of options to the validation function - unused.
    :return True is LGR transitivity is achieved, False otherwise.
    """
    success = True
    logger.info("Testing transitivity")
    result = {
        'description': 'Testing transitivity',
        'repertoire': []
    }

    for a in lgr.repertoire:
        if isinstance(a, RangeChar):
            # Range have no variants
            continue

        a_variants = list(a.get_variants())  # get_variants() returns generator
        logger.debug("A: '%s'", format_cp(a.cp))
        for b in a_variants:
            logger.debug("A: '%s' - B: '%s'", format_cp(a.cp), format_cp(b.cp))
            try:
                variants = lgr.get_variants(b.cp)
            except NotInLGR:
                logger.error("Code point '%s' not in LGR", format_cp(b.cp))
                success = False
                continue
            # Variant is defined in repertoire
            # (we have checked for symmetry first)
            for c in [var for var in variants if var.cp != a.cp]:
                logger.debug("A: '%s' - B: '%s' - C: '%s'",
                             format_cp(a.cp),
                             format_cp(b.cp),
                             format_cp(c.cp))
                # Iterate through all second-level variants
                # which are not the original code point
                if c.cp not in [var.cp for var in a_variants]:
                    success = False
                    logger.warning("CP %s should have CP %s in its variants.",
                                   format_cp(a.cp),
                                   format_cp(c.cp))
                    lgr.notify_error("basic_transitivity")
                    result['repertoire'].append({
                        'char': a,
                        'variant': c
                    })
    logger.info("Transitivity test done")
    lgr.notify_tested("basic_transitivity")

    return success, result
