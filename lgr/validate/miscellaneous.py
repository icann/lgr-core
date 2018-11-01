# -*- coding: utf-8 -*-
"""
miscellaneous.py - Perform miscellaneous rfc7940 compliance checks
"""

import logging
import datetime

import lgr.char as lgr_char

logger = logging.getLogger(__name__)

STANDARD_DISPOSITIONS = set([
    "invalid",
    "blocked",
    "allocatable",
    "activated",
    "valid",
])

VALID_IDNA_PROPERTY_VALUES = set([
    "PVALID",
    "CONTEXTJ",
    "CONTEXTO",
])

def check_lgr_data(lgr):

    success = True
    # Check variant types
    for c in lgr.repertoire:
        if isinstance(c, lgr_char.RangeChar):
            # Range have no variants
            continue
        for v in c.get_variants():
            if v.type is not None:
                t = v.type
                if ' ' in t or t == '' or t[0] == '_':
                    logging.error("Bad variant type '%s'", t)
                    success = False
                    lgr.notify_error("data_variant_type")
        lgr.notify_tested("data_variant_type")

    # Check that all chars exist in the given Unicode version

    # First add all code points to the set "to_check"
    to_check = set()
    for c in lgr.repertoire:
        if isinstance(c, lgr_char.RangeChar):
            to_check.update(range(c.first_cp, c.last_cp + 1))
        else:
            to_check.update(c.cp)
            for v in c.get_variants():
                to_check.update(v.cp)

    # Check that all code points in to_check are valid in our Unicode version
    for cp in to_check:
        prop = lgr.unicode_database.get_idna_prop(cp)
        if prop not in VALID_IDNA_PROPERTY_VALUES:
            logging.error("Invalid codepoint '%04X': %s", cp, prop)
            success = False
            lgr.notify_error('codepoint_valid')
    lgr.notify_tested('codepoint_valid')

    # Check "ref" attribute:
    for c in lgr.repertoire:
        success = check_ref_ascending(lgr, c.references) and success
        for v in c.get_variants():
            success = check_ref_ascending(lgr, v.references) and success
    # TODO: there are other elements with a ref attribute.
    lgr.notify_tested('ref_attribute_ascending')
    return success

def check_ref_ascending(lgr, reflist):
    last = -1
    for n in reflist:
        if not re.match(r'\d+$', n):
            # Not clear how to order references that are not integers
            break
        if not int(n) > last:
            lgr.notify_error('ref_attribute_ascending')
            logging.warning("references not in ascending order: %d --> %d", last, int(n))
            return False
        last = int(n)
    return True

def check_lgr_rules(lgr):

    # Rules: dispositions

    success = True
    for action in lgr.actions:
        disp = action.disp
        if not disp in STANDARD_DISPOSITIONS:
            lgr.notify_error("standard_dispositions")
            success = False
            logging.error("Action element has non-standard disposition " + disp)
    lgr.notify_tested("standard_dispositions")
    return success

def check_miscellaneous(lgr, options):
    """
    Check the data and rules elements for RFC7940 compliance.

    :param LGR lgr: The LGR to check.
    :param options: Dictionary of options to the validation function - unused.
    :return True if compliant, False otherwise.
    """

    logger.info("Testing data and rules")
    result = {
        'description': 'Testing data and rules',
        'repertoire': []
    }

    success = check_lgr_rules(lgr) and check_lgr_data(lgr)

    logger.info("Miscellaneous test done")

    return success, result
