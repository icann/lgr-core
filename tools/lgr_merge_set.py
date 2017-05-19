#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_diff_collisions.py - CLI tool to make the diff on a list of labels
                         confronted to 2 LGR and/or to test a set of labels for
                         collisions in one or both LGR
"""
from __future__ import unicode_literals

import sys
import argparse
import logging

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_serializer import serialize_lgr_xml
from lgr.parser.xml_parser import XMLParser

from lgr.tools.merge_set import merge_lgr_set

logger = logging.getLogger("lgr_merge_set")


def write_output(s):
    print(s.encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='LGR diff and collision CLI')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    parser.add_argument('-l', '--libs', metavar='LIBS', help='ICU libraries', required=True)
    parser.add_argument('-r', '--rng', metavar='RNG', help='RelaxNG XML schema')
    parser.add_argument('-n', '--name', metavar='NAME', help="Merged LGR name")
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

    lgr_set = []
    for lgr_file in args.lgr_set:
        lgr_parser = XMLParser(lgr_file)
        lgr_parser.unicode_database = unidb

        if args.rng is not None:
            validation_result = lgr_parser.validate_document(args.rng)
            if validation_result is not None:
                logger.error('Errors for RNG validation of LGR %s: %s',
                             lgr_file, validation_result)

        lgr = lgr_parser.parse_document()
        if lgr is None:
            logger.error("Error while parsing LGR file %s." % lgr_file)
            logger.error("Please check compliance with RNG.")
            return

        lgr_set.append(lgr)

    write_output('Please wait, this can take some time...\n')

    name = 'merged-lgr-set'
    if args.name:
        name = args.name
    merged_lgr = merge_lgr_set(lgr_set, name)
    write_output(serialize_lgr_xml(merged_lgr, pretty_print=True))

if __name__ == '__main__':
    main()
