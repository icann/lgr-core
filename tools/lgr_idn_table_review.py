#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_review.py - CLI tool to generate the idn review report.

Can review IDN tables with reference LGRs.
"""
from __future__ import unicode_literals

import logging
import sys
from datetime import date

from lgr.tools.idn_review.review import review_lgr
from lgr.tools.utils import LgrToolArgParser, parse_lgr
from munidata.database import UnicodeDatabase

logger = logging.getLogger(__name__)


def main():
    parser = LgrToolArgParser(description='LGR IDN Table review')
    parser.add_common_args()
    parser.add_argument('-o', '--output', help='Output folder where to generate and store the report',
                        default='/tmp/lgr-idn-table-review-report/' + str(date.today()))
    parser.add_argument('-t', '--idn-table', nargs='+', help='The IDN tables to review', required=True)
    parser.add_argument('-x', '--reference-lgr', nargs='+', help='The reference LGR used to review IDN tables',
                        required=True)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    unidb: UnicodeDatabase = parser.get_unidb()

    reference_lgrs = []
    for reference_lgr_file in set(args.reference_lgr):
        ref_lgr = parse_lgr(reference_lgr_file, args.rng, unidb)
        if not ref_lgr:
            logger.error("Cannot parse LGR file %s, skip it", reference_lgr_file)
        reference_lgrs.append(ref_lgr)

    idn_tables = []
    for idn_table in set(args.idn_table):
        # XXX for now only handle LGR format, may add the algorithm to detect and convert from RFC
        lgr = parse_lgr(idn_table, args.rng, unidb)
        if not lgr:
            logger.error("Cannot parse LGR file %s, skip it", idn_table)
        idn_tables.append(lgr)

    for idn_table in idn_tables:
        for reference_lgr in reference_lgrs:
            review_lgr(idn_table, reference_lgr)


if __name__ == '__main__':
    main()
