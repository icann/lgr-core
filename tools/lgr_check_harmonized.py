#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_check_harmonized.py - CLI tool to check if LGRs are harmonized
"""
from __future__ import unicode_literals

import argparse
import logging
import sys

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_parser import XMLParser
from lgr.tools.utils import write_output
from lgr.tools.check_harmonized import check_harmonized

logger = logging.getLogger("lgr_check_harmonized")


def main():
    parser = argparse.ArgumentParser(description='LGR Check Harmonized CLI')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries', required=True)
    parser.add_argument('-x', '--lgr-xml', metavar='LGR', action='append',
                        help='The LGRs to check for harmonization (call it multiple times)',
                        required=True)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stderr, level=log_level)

    libpath, i18n_libpath, libver = args.libs.split('#')
    manager = UnicodeDataVersionManager()
    unidb = manager.register(None, libpath, i18n_libpath, libver)

    lgrs = []
    for lgr_file in args.lgr_xml:
        lgr_parser = XMLParser(lgr_file)
        lgr_parser.unicode_database = unidb

        if args.rng is not None:
            validation_result = lgr_parser.validate_document(args.rng)
            if validation_result is not None:
                logger.error('Errors for RNG validation of LGR file %s: %s',
                             lgr_file, validation_result)

        lgr = lgr_parser.parse_document()
        if lgr is None:
            logger.error("Error while parsing LGR file %s", lgr_file)
            logger.error("Please check compliance with RNG.")
            return

        lgrs.append(lgr)

    for out in check_harmonized(lgrs):
        write_output(out)


if __name__ == '__main__':
    main()
