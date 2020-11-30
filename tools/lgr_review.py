#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_review.py - CLI tool to generate the idn review report.

Can parse an IDN table with the reference LGR.
"""
from __future__ import unicode_literals

import sys
import argparse
import logging

from lgr import wide_unichr

logger = logging.getLogger("lgr_review")

def main():
    parser = argparse.ArgumentParser(description='LGR Review')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Be quiet (no log)')
    parser.add_argument('-o', '--output-report-folder', help='Output folder where to generate and store the report', default='/tmp/lgr-review-report/')
    parser.add_argument('-l', '--lgr', nargs='+', help='IDN Tables Reference input', required=True)
    parser.add_argument('idn_table', nargs='+', metavar='IDN_TABLE')

    args = parser.parse_args()

    if len(args.lgr) != len(args.idn_table):
        print("The number of idn tables input {} is not the same as the number of reference lgr {}".format(len(args.lgr), len(args.idn_table)))

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    for i in range(len(args.lgr)):
        idn_table = args.idn_table[i]
        idn_parser = XMLParser(idn_table)
        lgr = lgr_parser.parse_document()

if __name__ == '__main__':
    main()
