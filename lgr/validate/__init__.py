# -*- coding: utf-8 -*-
"""
__init__.py - Definition of various checks/validation of an LGR.
"""
from __future__ import unicode_literals

import logging

from lgr.exceptions import LGRException
from lgr.validate.xml_validity import check_xml_validity
from lgr.validate.symmetry import check_symmetry
from lgr.validate.lgr_stats import compute_stats
from lgr.validate.rebuild_lgr import rebuild_lgr
from lgr.validate.transitivity import check_transitivity
from lgr.validate.conditional_variants import check_conditional_variants

CHECKS = [
    check_xml_validity,
    check_symmetry,
    check_transitivity,
    check_conditional_variants,
    rebuild_lgr,
    compute_stats
]

logger = logging.getLogger(__name__)


def validate_lgr(lgr, options):
    """
    Run a list of defined validation and checks on a LGR.

    The options argument is a dictionary which will be passed as a parameter
    to all check functions. It's up to each of these functions to determine
    which parameter they will be using, and to gracefully handle
    the presence or absence of the parameter in the dictionary.

    :param lgr: The LGR to be validated.
    :param options: Dictionary of options to the validation function.
    :return: Result of checks and summary as a list of (check function name, check results).
    """
    result = []

    for check_function in CHECKS:
        try:
            valid, func_result = check_function(lgr, options)
            result.append((check_function.__name__, func_result))
        except LGRException as exc:
            logger.error("Error while validating LGR '%s': %s",
                         lgr, exc)
            result.append((check_function.__name__, exc))

    return result
