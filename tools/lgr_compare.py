#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_compare.py - CLI tool to compare 2 LGRs
"""
from __future__ import unicode_literals

import argparse
import logging
import sys

from lgr.tools.compare import diff_lgrs
from lgr.tools.compare import intersect_lgrs
from lgr.tools.compare import union_lgrs

from lgr.parser.xml_parser import XMLParser
from lgr.parser.xml_serializer import serialize_lgr_xml

logger = logging.getLogger("lgr_compare")


def main():
    parser = argparse.ArgumentParser(description='LGR Compare CLI')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-1', '--first', metavar='LGR1',
                        help='First LGR',
                        required=True)
    parser.add_argument('-2', '--second', metavar='LGR2',
                        help='Second LGR',
                        required=True)
    parser.add_argument('action', metavar="ACTION",
                        help='Compare action (INTERSECT, UNION, DIFF)',
                        choices=['INTERSECT', 'UNION', 'DIFF'])

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stderr, level=log_level)

    lgr1_parser = XMLParser(args.first)
    lgr2_parser = XMLParser(args.second)

    if args.rng is not None:
        validation_result = lgr1_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation of first LGR: %s',
                         validation_result)
        validation_result = lgr2_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation of second LGR: %s',
                         validation_result)

    lgr1 = lgr1_parser.parse_document()
    if lgr1 is None:
        logger.error("Error while parsing first LGR file.")
        logger.error("Please check compliance with RNG.")
        return
    lgr2 = lgr2_parser.parse_document()
    if lgr2 is None:
        logger.error("Error while parsing second LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    if args.action in ['INTERSECT', 'UNION']:
        if args.action == 'INTERSECT':
            lgr = intersect_lgrs(lgr1, lgr2)
        elif args.action == 'UNION':
            lgr = union_lgrs(lgr1, lgr2)

        print(serialize_lgr_xml(lgr, pretty_print=True))
    elif args.action == 'DIFF':
        print(diff_lgrs(lgr1, lgr2))

if __name__ == '__main__':
    main()
