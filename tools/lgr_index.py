#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_index.py - Small CLI tool to compute indexes on a list of labels
"""
import io
import logging

from lgr.exceptions import NotInLGR
from lgr.tools.utils import write_output, LgrToolArgParser, read_labels
from lgr.utils import format_cp

logger = logging.getLogger("lgr_index")


def main():
    parser = LgrToolArgParser(description='LGR Collision')
    parser.add_common_args()
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='Compute recursive index')
    parser.add_argument('-L', '--labels', metavar='LABELS',
                        help='Filepath to the labels',
                        required=True)
    parser.add_xml_meta(help='Reference LGR for index computation')

    args = parser.parse_args()

    parser.setup_logger()

    lgr = parser.parse_lgr()
    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    with io.open(args.labels, 'r', encoding='utf-8') as labels_input:
        for __, label, valid, error in read_labels(labels_input, lgr.unicode_database):
            write_output('\n----------------------------------------------------\n')
            if not valid:
                write_output(f'{label}: {error}\n')
                continue
            label_cp = tuple([ord(c) for c in label])
            write_output(f'Label {label} [{format_cp(label_cp)}]\n')
            try:
                label_partitions =  lgr._generate_label_partitions(label_cp)
                write_output('Partitions:')
                for partition in label_partitions:
                    write_output('\t' + ' '.join(f'{{{format_cp(char.cp)}}}' for char in partition))
                label_index = lgr.generate_index_label(label_cp, max_recursion=5 if args.recursive else 0)
                write_output(f"Index: {format_cp(label_index)}")
            except NotInLGR:
                logger.warning('Label %s is not in LGR', label)
                continue


if __name__ == '__main__':
    main()
