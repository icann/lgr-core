#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_validate.py - CLI tool which validate a label and generate its variants.

This is a lightweight version of lgr_cli tool, only dedicated to validate
a label and generate its variants.
"""
from __future__ import unicode_literals

import io
import logging
from io import StringIO

from lgr.tools.diff_collisions import get_collisions
from lgr.tools.utils import write_output, merge_lgrs, read_labels, get_stdin
from lgr.utils import cp_to_ulabel
from tools.utils import LgrToolArgParser, parse_lgr

logger = logging.getLogger("lgr_validate")


def check_label(lgr, label, generate_variants=False, merged_lgr=None, set_labels=None):
    from lgr.utils import format_cp
    label_cp = tuple([ord(c) for c in label])

    write_output("\nLabel: %s [%s]" % (label, format_cp(label_cp)))

    (eligible, label_parts, label_invalid_parts, disp, _, _) = lgr.test_label_eligible(label_cp)
    write_output("\tEligible: %s" % eligible)
    write_output("\tDisposition: %s" % disp)

    if eligible:
        if merged_lgr and set_labels:
            write_output("Collisions:")
            if label in set_labels:
                write_output("Labels is in the LGR set labels")
            else:
                indexes = get_collisions(merged_lgr, set_labels + [label], quiet=True)
                if len(indexes) > 1:
                    # there should be one collision except if set labels are not checked
                    logger.error('More than one collision, please check your LGR set labels')
                    return
                elif len(indexes) > 0:
                    collisions = indexes[list(indexes.keys())[0]]
                    collision = None
                    collide_with = []
                    # retrieve label in collision list
                    for col in collisions:
                        if col['label'] == label:
                            collision = col
                        if col['label'] in set_labels:
                            collide_with.append(col)

                    if not collision:
                        # this should not happen except if set labels are not checked
                        logger.error('Cannot retrieve label in collisions, please check your LGR set labels')
                        return

                    if len(collide_with) != 1:
                        logger.error('Collision with more than one label in the LGR set labels,'
                                     'please check your LGR set labels')
                        return

                    write_output("Label collides with LGR set label '%s'" % collide_with[0]['label'])
                else:
                    write_output('\tNone')

        if generate_variants:
            write_output("Variants:")
            summary, labels = lgr.compute_label_disposition_summary(label_cp)
            for (variant_cp, var_disp, _, _, _) in labels:
                variant_u = cp_to_ulabel(variant_cp)
                write_output("\tVariant %s [%s]" % (variant_u, format_cp(variant_cp)))
                write_output("\t- Disposition: '%s'" % var_disp)
    else:
        write_output("- Valid code points from label: %s" % u' '.join(u"{:04X}".format(cp) for cp in label_parts))
        if label_invalid_parts:
            write_output("- Invalid code points from label: {}".format(
                ' '.join("{:04X} ({})".format(cp, "not in repertoire" if rules is None else ','.join(rules))
                         for cp, rules in label_invalid_parts)))


def main():
    parser = LgrToolArgParser(description='LGR Validate CLI')
    parser.add_common_args()
    parser.add_argument('-g', '--variants', action='store_true',
                        help='Generate variants')
    parser.add_argument('-x', '--lgr-xml', metavar='LGR_XML', action='append', required=True,
                        help='The LGR or LGR set if used multiple times')
    parser.add_argument('-s', '--lgr-script', metavar='LGR_SCRIPT',
                        help='If LGR is a set, the script used to validate input labels')
    parser.add_argument('-f', '--set-labels', metavar='SET_LABELS',
                        help='If LGR is a set, the file containing the label of the LGR set')

    args = parser.parse_args()
    parser.add_logging_args()

    unidb = parser.get_unidb()
    if len(args.lgr_xml) > 1:
        if not args.lgr_script:
            logger.error('For LGR set, lgr script is required')
            return

        if not args.set_labels:
            logger.error('For LGR set, LGR set labels file is required')
            return

        merged_lgr, lgr_set = merge_lgrs(args.lgr_xml, unidb=unidb)
        if not merged_lgr:
            logger.error('Error while creating the merged LGR')
            return

        with io.open(args.set_labels, 'r', encoding='utf-8') as set_labels_input:
            set_labels = StringIO(set_labels_input.read())

        script_lgr = None
        for lgr_s in lgr_set:
            try:
                if lgr_s.metadata.languages[0] == args.lgr_script:
                    if script_lgr:
                        logger.warning('Script %s is provided in more than one LGR of the set, '
                                       'will only evaluate with %s', args.lgr_script, lgr_s.name)
                    script_lgr = lgr_s
            except (AttributeError, IndexError):
                pass

        if not script_lgr:
            logger.error('Cannot find script %s in any of the LGR provided as input', args.lgr_script)
            return
    else:
        lgr = parse_lgr(args.lgr_mxml[0], args.rng, unidb)
        if lgr is None:
            logger.error("Error while parsing LGR file.")
            logger.error("Please check compliance with RNG.")
            return

    filtered_set_labels = []
    if len(args.lgr_xml) > 1:
        write_output("# The following labels from the set labels are invalid\n")
        for label, valid, error in read_labels(set_labels, script_lgr.unicode_database):
            if not valid:
                write_output("{}: {}\n".format(label, error))
            else:
                label_cp = tuple([ord(c) for c in label])
                if not script_lgr._test_preliminary_eligibility(label_cp)[0]:
                    write_output("%s: Not in LGR %s\n" % label, script_lgr)
                else:
                    filtered_set_labels.append(label)
        write_output("# End of filtered set labels\n\n")

    for label in get_stdin().read().splitlines():
        if len(args.lgr_xml) > 1:
            check_label(script_lgr, label, args.variants,
                        merged_lgr=merged_lgr, set_labels=filtered_set_labels)
        else:
            check_label(lgr, label, args.variants)


if __name__ == '__main__':
    main()
