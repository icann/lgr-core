#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_populate_variants.py - CLI tool to populate variants
"""
from __future__ import unicode_literals

import argparse
import logging
import sys

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_parser import XMLParser
from lgr.parser.xml_serializer import serialize_lgr_xml

logger = logging.getLogger("lgr_populate_variants")


def main():
    parser = argparse.ArgumentParser(description='LGR Populate Variants CLI')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries', required=True)
    parser.add_argument('-x', '--lgr-xml', metavar='LGR',
                        help='The LGR to populate',
                        required=True)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stderr, level=log_level)

    libpath, i18n_libpath, libver = args.libs.split('#')
    manager = UnicodeDataVersionManager()
    unidb = manager.register(None, libpath, i18n_libpath, libver)

    lgr_parser = XMLParser(args.lgr_xml)
    lgr_parser.unicode_database = unidb

    if args.rng is not None:
        validation_result = lgr_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation of LGR file %s: %s', args.lgr_xml, validation_result)

    lgr = lgr_parser.parse_document()
    if lgr is None:
        logger.error("Error while parsing LGR file %s", args.lgr_xml)
        logger.error("Please check compliance with RNG.")
        return

    lgr.populate_variants()
    print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))


if __name__ == '__main__':
    main()
