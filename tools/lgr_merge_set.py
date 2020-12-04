#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_merge_set.py - CLI tool merge a set of LGRs
"""
from __future__ import unicode_literals

import logging

from lgr.parser.xml_serializer import serialize_lgr_xml
from lgr.tools.utils import merge_lgrs
from tools.utils import LgrToolArgParser

logger = logging.getLogger("lgr_merge_set")


def main():
    parser = LgrToolArgParser(description='LGR diff and collision CLI')
    parser.add_logging_args()
    parser.add_libs_arg(required=False)
    parser.add_rng_arg()
    parser.add_argument('-n', '--name', metavar='NAME', help="Merged LGR name")
    parser.add_argument('-s', '--lgr-set', metavar='LGR-SET', action='append',
                        help='LGR in the set (can be used multiple times)', required=True)

    args = parser.parse_args()

    parser.setup_logger()

    if len(args.lgr_set) == 1:
        logger.error("Please provide more than one LGR to make a set")
        return

    logger.warning('Please wait, this can take some time...\n')

    merged_lgr, _ = merge_lgrs(args.lgr_set, name=args.name, rng=args.rng, unidb=parser.get_unidb())
    if not merged_lgr:
        return
    print(serialize_lgr_xml(merged_lgr, pretty_print=True))


if __name__ == '__main__':
    main()
