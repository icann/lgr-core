#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_index.py - Small CLI tool to compute indexes on a list of labels
"""
import io
import logging

from lgr.core import IndexComputationAlgorithm
from lgr.exceptions import NotInLGR
from lgr.tools.utils import write_output, LgrToolArgParser, read_labels
from lgr.utils import format_cp

logger = logging.getLogger("lgr_index")


def _index_algo_or_all(value):
    try:
        return [IndexComputationAlgorithm(value.replace('_', ' '))]
    except ValueError:
        pass

    if value.lower() == 'all':
        return list(IndexComputationAlgorithm)

    raise ValueError(f'Invalid index computation algorithm: {value}')


def display_label_index(args, lgr, label, valid, error):
    write_output('\n----------------------------------------------------\n')
    if not valid:
        write_output(f'{label}: {error}\n')
        return
    label_cp = tuple([ord(c) for c in label])
    write_output(f'Label {label} [{format_cp(label_cp)}]\n')
    try:
        label_partitions = lgr._generate_label_partitions(label_cp)
        write_output('Partitions:')
        for partition in label_partitions:
            write_output('\t' + ' '.join(f'{{{format_cp(char.cp)}}}' for char in partition))
        for algo in args.algorithm:
            label_index = lgr.generate_index_label(label_cp, max_recursion=5 if args.recursive else 0,
                                                   algo=algo)
            write_output(f"Index {algo.value} algo:\t{'\t' if algo == IndexComputationAlgorithm.DEFAULT else ''}{format_cp(label_index)}")
    except NotInLGR:
        logger.warning('Label %s is not in LGR', label)


def main():
    parser = LgrToolArgParser(description='LGR Collision')
    parser.add_common_args()
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='Compute recursive index')
    parser.add_argument('-L', '--labels', metavar='LABELS',
                        help='Filepath to the labels',
                        required=True)
    parser.add_argument('-a', '--algorithm',
                        type=_index_algo_or_all,
                        default=[IndexComputationAlgorithm.DEFAULT],
                        help='Index computation algorithm (default, shortest, lesser_chars, longest_sequences, all)')
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
            display_label_index(args, lgr, label, valid, error)


if __name__ == '__main__':
    main()
