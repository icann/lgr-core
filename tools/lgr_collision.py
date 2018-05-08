#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_collision.py - Small CLI tool to test collisions of labels.
"""
from __future__ import unicode_literals

import sys
import argparse
import logging
import io

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_parser import XMLParser
from lgr.exceptions import NotInLGR
from lgr.utils import format_cp, cp_to_ulabel
from lgr.tools.utils import write_output, get_stdin

logger = logging.getLogger("lgr_collision")


def compute_label_index(lgr, label):
    return lgr.generate_index_label(label)


def find_variants_to_block(lgr, label_ref, label):
    var_ref = [var for (var, _, _) in lgr._generate_label_variants(label_ref)]

    for (variant_cp, disp, _, disp_set, _) in lgr.compute_label_disposition(label):
        if variant_cp in var_ref:
            variant_u = cp_to_ulabel(variant_cp)
            write_output("Variant '%s' [%s] with disposition set '%s' "
                         "should be blocked (current disposition :%s)" % (variant_u, format_cp(variant_cp), disp_set, disp))


def main():
    parser = argparse.ArgumentParser(description='LGR Collision')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-g', '--generate', action='store_true',
                        help='Generate variants')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries', required=True)
    parser.add_argument('-s', '--set', metavar='SET FILE',
                        help='Filepath to the set of reference labels',
                        required=True)
    parser.add_argument('xml', metavar='XML')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    lgr_parser = XMLParser(args.xml)

    libpath, i18n_libpath, libver = args.libs.split('#')
    manager = UnicodeDataVersionManager()
    unidb = manager.register(None, libpath, i18n_libpath, libver)

    lgr_parser.unicode_database = unidb

    lgr = lgr_parser.parse_document()
    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    ref_label_indexes = {}

    # Compute index label for set or reference labels
    with io.open(args.set, 'r', encoding='utf-8') as ref_set:
        for ref_label in ref_set:
            label_cp = tuple([ord(c) for c in ref_label.strip()])
            try:
                label_index = compute_label_index(lgr, label_cp)
            except NotInLGR:
                continue
            ref_label_indexes[label_index] = label_cp

    # Deal with input
    for label in get_stdin().read().splitlines():
        write_output("Check label '%s'" % label)
        label_cp = tuple([ord(c) for c in label])
        label_disp = format_cp(label_cp)
        label_index = compute_label_index(lgr, label_cp)

        if label_index in ref_label_indexes:
            ref_label_cp = ref_label_indexes[label_index]
            ref_label_disp = format_cp(ref_label_cp)
            ref_label_u = cp_to_ulabel(ref_label_cp)

            write_output("Collision for label '%s' [%s] with '%s' [%s]" % (label, label_disp, ref_label_u, ref_label_disp))
            if args.generate:
                find_variants_to_block(lgr, ref_label_cp, label_cp)
        else:
            write_output("No collision for label %s [%s]" % (label, label_disp))


if __name__ == '__main__':
    main()
