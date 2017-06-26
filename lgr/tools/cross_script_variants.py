# -*- coding: utf-8 -*-
"""
cross_script_variants.py - Generate a report on cross-script variants.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.merge_set import get_script
from lgr.utils import format_cp
from lgr.tools.utils import read_labels
from lgr.exceptions import LGRException

logger = logging.getLogger(__name__)


def get_variants(lgr_set, label):
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
        try:
            for variant, variant_disp, _, _, _ in lgr.compute_label_disposition(label):
                yield variant, variant_disp
        except LGRException as ex:
            yield label, ex

    for lgr in lgr_set:
        # Check that label is eligible in the Element LGR
        result, _, _, _, _, _ = lgr.test_label_eligible(label)
        if not result:
            continue

        yield get_script(lgr), _return_variants(lgr, label)


def cross_script_variants(lgr_set, unidb, labels_input):
    """
    Compute cross-script variants of labels.

    :param lgr_set: The list of LGRs in the set.
    :param unidb: The unicode database to use.
    :param labels_input: The file containing the labels
    """
    for label in read_labels(labels_input, unidb):
        label_cp = tuple([ord(c) for c in label])
        yield "Input label {} ({})\n".format(format_cp(label_cp), label)
        for script, variants in get_variants(lgr_set, label_cp):
            yield "- Script {}\n".format(script)
            for var, disp in variants:
                yield "\t- Variant {} ({}), disposition {}\n".format(format_cp(var),
                                                                     ''.join([unichr(c) for c in var]),
                                                                     disp)
