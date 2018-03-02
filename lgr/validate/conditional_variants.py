# -*- coding: utf-8 -*-
"""
conditional_variants.py - Check that values of "when"/"not-when" attributes
                          of variants is a parameterized context rule.
"""
from __future__ import unicode_literals

import logging

from lgr.char import RangeChar
from lgr.utils import format_cp

logger = logging.getLogger(__name__)


def check_conditional_variants(lgr, options):
    """
    Check that all variants "when"/"not-when" values
    are parameterized context rule.

    :param LGR lgr: The LGR to check.
    :param options: Dictionary of options to the validation function - unused.
    """
    logger.info("Testing conditional variants")
    success = True
    result = {
        'description': 'Testing conditional variants',
        'repertoire': []
    }
    for char in lgr.repertoire:
        if isinstance(char, RangeChar):
            # Range have no variants
            continue
        for var in char.get_variants():
            when = var.when
            not_when = var.not_when

            if when is not None and when not in lgr.rules:
                logger.warning("CP %s: Variant '%s' \"when\" attribute "
                               "'%s' is not an existing rule name.",
                               format_cp(char.cp), format_cp(var.cp),
                               when)
                success = False
                result['repertoire'].append({
                    'char': char,
                    'variant': var,
                    'rule_type': 'when',
                    'rule': when
                })
            if not_when is not None and not_when not in lgr.rules:
                logger.warning("CP %s: Variant '%s' \"not-when\" attribute "
                               "'%s' is not an existing rule name.",
                               format_cp(char.cp), format_cp(var.cp),
                               not_when)
                success = False
                result['repertoire'].append({
                    'char': char,
                    'variant': var,
                    'rule_type': 'not-when',
                    'rule': not_when
                })

    logger.info("Conditional variants test done")

    return success, result
