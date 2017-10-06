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


def _generate_variants(merged_lgr, lgr_set, label):
    """
    Generate the variants of a label.

    :param merged_lgr: The merged LGR from the set.
    :param lgr_set: The list of LGRs in the set.
    :param label: The label to process, as an array of code points.
    :return: Generator of (variant, disp, scripts), with:
        - variant: The generated variant.
        - disp: Variant disposition. Note: not sure disp will be != from "blocked".
        - scripts: List of scripts used in the variants.
    """
    try:
        for variant, variant_disp, _, _, _ in merged_lgr.compute_label_disposition(label):
            scripts = set()
            for var_cp in variant:
                char = merged_lgr.get_char(var_cp)
                for lgr in lgr_set:
                    if char in lgr.repertoire:
                        scripts.add(get_script(lgr))
            if scripts:
                yield variant, variant_disp, scripts
    except LGRException as ex:
        yield label, ex, set()


def cross_script_variants(merged_lgr, lgr_set, unidb, labels_input):
    """
    Compute cross-script variants of labels.

    :param merged_lgr: The merged LGR from the set.
    :param lgr_set: The list of LGRs in the set.
    :param unidb: The unicode database to use.
    :param labels_input: The file containing the labels
    """
    for label, valid, error in read_labels(labels_input, unidb):
        if not valid:
            yield "Input label {}: {}\n".format(label, error)
        else:
            label_cp = tuple([ord(c) for c in label])
            yield "Input label {} ({})\n".format(format_cp(label_cp), label)
            # Check that label is eligible in the merged LGR
            result, _, _, _, _, _ = merged_lgr.test_label_eligible(label_cp)
            if not result:
                continue
            for variant, disp, scripts in _generate_variants(merged_lgr, lgr_set, label_cp):
                yield "\t- Variant {} ({}), disposition {}, from LGR: {}\n".format(format_cp(variant),
                                                                                   ''.join([unichr(c) for c in variant]),
                                                                                   disp,
                                                                                   ', '.join(scripts))