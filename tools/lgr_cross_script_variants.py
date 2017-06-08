#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_cross_script_variants.py - CLI tool to generate the list of cross-script variants.
"""
from __future__ import unicode_literals

import sys
import argparse
import logging
import codecs

from munidata import UnicodeDataVersionManager

from lgr.utils import format_cp
from lgr.tools.utils import write_output, merge_lgrs, read_labels
from lgr.tools.cross_script_variants import cross_script_variants

logger = logging.getLogger("lgr_cross_script_variants")


def main():
    parser = argparse.ArgumentParser(description='LGR Cross-script variants CLI')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    parser.add_argument('-l', '--libs', metavar='LIBS', help='ICU libraries', required=True)
    parser.add_argument('-r', '--rng', metavar='RNG', help='RelaxNG XML schema')
    parser.add_argument('-s', '--lgr-set', metavar='LGR-SET', action='append',
                        help='LGR in the set (can be used multiple times)', required=True)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    libpath, i18n_libpath, libver = args.libs.split('#')
    manager = UnicodeDataVersionManager()
    unidb = manager.register(None, libpath, i18n_libpath, libver)

    if len(args.lgr_set) == 1:
        logger.error("Please provide more than one LGR to make a set")
        return

    logger.info('Please wait, this can take some time...\n')

    merged_lgr, lgr_set = merge_lgrs(args.lgr_set, rng=args.rng, unidb=unidb)
    if not merged_lgr:
        return
    label_input = codecs.getreader('utf8')(sys.stdin)

    for label_cp in read_labels(label_input, unidb):
        write_output("Input label {} ({})".format(format_cp(label_cp), ''.join([unichr(c) for c in label_cp])))
        for script, variants in cross_script_variants(lgr_set, label_cp):
            write_output("- Script {}".format(script))
            for var, disp in variants:
                write_output("\t- Variant {} ({}), disposition {}".format(format_cp(var),
                                                                          ''.join([unichr(c) for c in var]),
                                                                          disp))

if __name__ == '__main__':
    main()
