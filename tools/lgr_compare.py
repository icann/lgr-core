#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_compare.py - CLI tool to compare 2 LGRs
"""
from __future__ import unicode_literals

import logging

from lgr.parser.xml_serializer import serialize_lgr_xml
from lgr.tools.compare import diff_lgrs, diff_lgr_sets
from lgr.tools.compare import intersect_lgrs
from lgr.tools.compare import union_lgrs
from lgr.tools.utils import merge_lgrs
from tools.utils import LgrToolArgParser, parse_lgr

logger = logging.getLogger("lgr_compare")


def main():
    parser = LgrToolArgParser(description='LGR Compare CLI')
    parser.add_logging_args()
    parser.add_rng_arg()
    parser.add_argument('-1', '--first', metavar='LGR1', action='append',
                        help='First LGR or LGR set if used multiple times',
                        required=True)
    parser.add_argument('-2', '--second', metavar='LGR2', action='append',
                        help='Second LGR or LGR set if used multiple times',
                        required=True)
    parser.add_argument('action', metavar="ACTION",
                        help='Compare action (INTERSECT, UNION, DIFF)',
                        choices=['INTERSECT', 'UNION', 'DIFF'])
    parser.add_argument('-g', '--generate', action='store_true',
                        help='Generate a full dump (with identical elements as well)')
    parser.add_argument('-n1', '--name-first', metavar='NAME1', help="Merged LGR 1 name")
    parser.add_argument('-n2', '--name-second', metavar='NAME2', help="Merged LGR 2 name")

    args = parser.parse_args()
    parser.setup_logger()

    if (len(args.first) == 1 and len(args.second) > 1) or (len(args.second) == 1 and len(args.first) > 1):
        logger.error("Cannot compare LGR with LGR sets")
        return

    logger.info('Please wait, this can take some time...\n')

    if len(args.first) > 1:
        if args.action in ['INTERSECT', 'UNION']:
            logger.error('Cannot perform intersection or union with LGR sets')
            return

        merged_lgr_1, lgr_set_1 = merge_lgrs(args.first, name=args.name_first, rng=args.rng)
        if not merged_lgr_1:
            return

        merged_lgr_2, lgr_set_2 = merge_lgrs(args.second, name=args.name_second, rng=args.rng)
        if not merged_lgr_2:
            return

        print(diff_lgr_sets(merged_lgr_1, merged_lgr_2, lgr_set_1, lgr_set_2))
    else:
        lgr1 = parse_lgr(args.first[0], args.rng)
        lgr2 = parse_lgr(args.second[0], args.rng)
        if lgr1 is None:
            logger.error("Error while parsing first LGR file.")
            logger.error("Please check compliance with RNG.")
            return
        if lgr2 is None:
            logger.error("Error while parsing second LGR file.")
            logger.error("Please check compliance with RNG.")
            return

        if args.action in ['INTERSECT', 'UNION']:
            if args.action == 'INTERSECT':
                lgr = intersect_lgrs(lgr1, lgr2)
            elif args.action == 'UNION':
                lgr = union_lgrs(lgr1, lgr2)

            print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))
        elif args.action == 'DIFF':
            print(diff_lgrs(lgr1, lgr2, show_same=args.generate))


if __name__ == '__main__':
    main()
