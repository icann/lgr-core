# -*- coding: utf-8 -*-
"""
cross_script_variants.py - Generate a report on cross-script variants.
"""
from __future__ import unicode_literals

import logging

from lgr.utils import format_cp, cp_to_ulabel
from lgr.tools.utils import read_labels
from lgr.exceptions import LGRException

logger = logging.getLogger(__name__)


def _generate_variants(lgr, label):
    """
    Generate the variants of a label.

    :param lgr: The LGR to use for variant generation.
    :param label: The label to process, as an array of code points.
    :return: Generator of (variant, disp, scripts), with:
        - variant: The generated variant.
        - disp: Variant disposition.
        - script_mapping: Mapping of CP -> scripts
          (for scripts outside of the LGR).
    """
    unidb = lgr.unicode_database
    lgr_scripts = frozenset(lgr.metadata.get_scripts())
    if not lgr_scripts:
        logger.error("Cannot generate cross-scripts variants "
                     "for LGR without languages")
        raise Exception

    try:
        for variant, variant_disp, _, _, _ in lgr.compute_label_disposition(label, include_invalid=True):
            script_mapping = {}
            for var_cp in variant:
                char = lgr.get_char(var_cp)
                for cp in char.cp:
                    cp_script = unidb.get_script(cp, alpha4=True)
                    if cp_script not in lgr_scripts:
                        script_mapping[cp] = cp_script
            scripts = set([s for sc in script_mapping.values() for s in sc])
            if not scripts <= lgr_scripts:
                yield variant, variant_disp, script_mapping
    except LGRException as ex:
        yield label, ex, dict()


def cross_script_variants(lgr, labels_input):
    """
    Compute cross-script variants of labels.

    :param lgr: The LGR to use for variant generation.
    :param labels_input: The file containing the labels
    """
    if lgr.metadata is None:
        logger.error("Cannot generate cross-scripts variants "
                     "for LGR without metadata")
        raise Exception
    if lgr.unicode_database is None:
        logger.error("Cannot generate cross-scripts variants "
                     "for LGR without unicode database attached")
        raise Exception
    found = False
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if not valid:
            yield "Input label {}: {}\n".format(label, error)
        else:
            label_cp = tuple([ord(c) for c in label])
            result, _, _, _, _, _ = lgr.test_label_eligible(label_cp)
            if not result:
                continue
            label_displayed = False
            for variant, disp, script_mapping in _generate_variants(lgr, label_cp):
                if not label_displayed:
                    # Only display input label if it has x-variants
                    yield "Input label {} ({}) has cross-script variants:\n".format(format_cp(label_cp),
                                                                                    label)
                    label_displayed = True
                    found = True
                yield "\t- Cross-variant {} ({}), disposition {}:\n".format(format_cp(variant), cp_to_ulabel(variant),
                                                                            disp)
                yield '\t\t+ ' + '\t\t+ '.join(["{} ({}): {}\n".format(format_cp(c), cp_to_ulabel(c), s) for c, s in script_mapping.items()])

    if not found:
        yield 'No cross-script variants for input!'
