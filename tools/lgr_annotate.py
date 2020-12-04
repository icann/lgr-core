#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_annotate.py - Annotate a set of labels with disposition.

Take a LGR and a label list in a file, output label list with disposition.
"""
from __future__ import unicode_literals

import io
import logging

from lgr.tools.annotate import annotate, lgr_set_annotate
from lgr.tools.utils import merge_lgrs
from tools.utils import LgrToolArgParser, parse_lgr

logger = logging.getLogger("lgr_annotate")


def add_xml_set_args(parser):


def main():
    parser = LgrToolArgParser(description='LGR Annotate CLI')
    parser.add_common_args()
    parser.add_argument('-o', '--output', metavar='OUTPUT_FILE',
                        help='File path to output the annotated labels',
                        required=True)
    parser.add_argument('-x', '--lgr-xml', metavar='LGR_XML', action='append', required=True,
                        help='The LGR or LGR set if used multiple times')
    parser.add_argument('-s', '--lgr-script', metavar='LGR_SCRIPT',
                        help='If LGR is a set, the script used to validate input labels')
    parser.add_argument('-f', '--set-labels', metavar='SET_LABELS',
                        help='If LGR is a set, the file containing the label of the LGR set')
    parser.add_argument('labels', metavar='LABELS', help='File path to the reference labels to annotate')

    args = parser.parse_args()
    parser.setup_logger()

    unidb = parser.get_unidb()
    if len(args.lgr_xml) > 1:
        if not args.lgr_script:
            logger.error('For LGR set, lgr script is required')
            return

        merged_lgr, lgr_set = merge_lgrs(args.lgr_xml,
                                         rng=args.rng,
                                         unidb=unidb)
        if not merged_lgr:
            logger.error('Error while creating the merged LGR')
            return

        set_labels = io.StringIO()
        if args.set_labels:
            with io.open(args.set_labels, 'r', encoding='utf-8') as set_labels_input:
                set_labels = io.StringIO(set_labels_input.read())

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

    # Compute index label
    with io.open(args.labels, 'r', encoding='utf-8') as labels_input:
        with io.open(args.output, 'w', encoding='utf-8') as labels_output:
            if len(args.lgr_xml) > 1:
                for out in lgr_set_annotate(merged_lgr, script_lgr, set_labels, labels_input):
                    labels_output.write(out)
            else:
                for out in annotate(lgr, labels_input):
                    labels_output.write(out)


if __name__ == '__main__':
    main()
