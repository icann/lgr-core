# -*- coding: utf-8 -*-
"""
symmetry.py - Check for symmetry
"""
from __future__ import unicode_literals

import logging

from lgr.char import RangeChar
from lgr.utils import format_cp

logger = logging.getLogger(__name__)


def check_symmetry(lgr, options):
    """
    Check that all variants are defined in a symmetric way.

    If B is a variant of A, then A must be a variant of B.

    We only check the presence of the code point in the variants, not that all
    properties are identical (type, when, not-when).

    :param lgr: The LGR to be tested.
    :param options: Dictionary of options to the validation function - unused.
    :return True is LGR symmetry is achieved, False otherwise.
    """
    logger.info("Testing symmetry")

    success = True
    result = {
        'description': 'Testing symmetry',
        'repertoire': []
    }
    for a in lgr.repertoire:
        if isinstance(a, RangeChar):
            # Range have no variants
            continue

        for b in a.get_variants():
            if b.cp not in lgr.repertoire:
                # Variant is not defined in repertoire
                logger.warning('CP %s: Variant %s is not in repertoire.',
                               format_cp(a.cp), format_cp(b.cp))
                lgr.notify_error('basic_symmetry')
                result['repertoire'].append({
                    'char': a,
                    'variant': b,
                    'type': 'not-in-repertoire'
                })
                success = False
                continue

            # Variant is defined in repertoire,
            # let's see if the original character is in its
            # variants
            if a.cp not in [var.cp for var in lgr.get_variants(b.cp)]:
                success = False
                logger.warning('CP %s should have CP %s in its variants.',
                               format_cp(b.cp), format_cp(a.cp))
                lgr.notify_error('basic_symmetry')
                result['repertoire'].append({
                    'char': b,
                    'variant': a,
                    'type': 'missing'
                })
                continue

            # Now let's check if the reverse mappings agree in their
            # "when" or "not-when" attributes
            for c in lgr.get_variants(b.cp):
                if c.cp == a.cp:
                    if c.when == b.when and c.not_when == b.not_when:
                        break
            else:
                success = False
                lgr.notify_error('strict_symmetry')
                logger.warning('CP %s should have CP %s in its strict variants.',
                               format_cp(b.cp), format_cp(a.cp))
                result['repertoire'].append({
                    'char': b,
                    'variant': a,
                    'type': 'missing'
                })
    logger.info("Symmetry test done")
    lgr.notify_tested('basic_symmetry')
    lgr.notify_tested('strict_symmetry')

    return success, result
