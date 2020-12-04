#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_populate_variants.py - CLI tool to populate variants
"""
from __future__ import unicode_literals

import logging

from lgr.parser.xml_serializer import serialize_lgr_xml
from lgr.tools.utils import parse_lgr, LgrToolArgParser

logger = logging.getLogger("lgr_populate_variants")


def main():
    parser = LgrToolArgParser(description='LGR Populate Variants CLI')
    parser.add_common_args()
    parser.add_argument('-x', '--lgr-xml', metavar='LGR',
                        help='The LGR to populate', required=True)

    args = parser.parse_args()
    parser.setup_logger()

    lgr = parse_lgr(args.lgr_xml, args.rng, parser.get_unidb())
    if lgr is None:
        logger.error("Error while parsing LGR file %s", args.lgr_xml)
        logger.error("Please check compliance with RNG.")
        return

    lgr.populate_variants()
    print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))


if __name__ == '__main__':
    main()
