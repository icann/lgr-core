# -*- coding: utf-8 -*-
"""
cross_script_variants.py - Generate a report on cross-script variants.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.merge_set import get_script

logger = logging.getLogger(__name__)


def cross_script_variants(lgr_set, label):
    """
    Generate the report of all variants for a given label.

    :param lgr_set: The LGR set used to generate variants.
    :param label: The label (must be eligible).
    :return: (script, generator<(variant, disp)>)
    """

    def _return_variants(lgr, label):
        """
        Utility function to return properly formatted list of variants.
        """
        for variant, variant_disp, _, _, _ in lgr.compute_label_disposition(label):
            yield variant, variant_disp

    for lgr in lgr_set:
        # Check that label is eligible in the Element LGR
        if not lgr.test_label_eligible(label):
            continue

        yield get_script(lgr), _return_variants(lgr, label)
