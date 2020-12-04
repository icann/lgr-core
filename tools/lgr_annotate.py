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
from lgr.tools.utils import LgrSetToolArgParser

logger = logging.getLogger("lgr_annotate")


def main():
    parser = LgrSetToolArgParser(description='LGR Annotate CLI')
    parser.add_common_args()
    parser.add_argument('-o', '--output', metavar='OUTPUT_FILE',
                        help='File path to output the annotated labels',
                        required=True)
    parser.add_xml_set_args()
    parser.add_argument('labels', metavar='LABELS', help='File path to the reference labels to annotate')

    args = parser.parse_args()
    parser.setup_logger()

    if not parser.process_set(True):
        return

    # Compute index label
    with io.open(args.labels, 'r', encoding='utf-8') as labels_input:
        with io.open(args.output, 'w', encoding='utf-8') as labels_output:
            if len(args.lgr_xml) > 1:
                for out in lgr_set_annotate(parser.merged_lgr, parser.script_lgr, parser.set_labels, labels_input):
                    labels_output.write(out)
            else:
                for out in annotate(parser.lgr, labels_input):
                    labels_output.write(out)


if __name__ == '__main__':
    main()
