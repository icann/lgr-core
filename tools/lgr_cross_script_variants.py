#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_cross_script_variants.py - CLI tool to generate the list of cross-script variants.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.cross_script_variants import cross_script_variants
from lgr.tools.utils import merge_lgrs, write_output, get_stdin, LgrToolArgParser

logger = logging.getLogger("lgr_cross_script_variants")


def main():
    parser = LgrToolArgParser(description='LGR Cross-script variants CLI')
    parser.add_logging_args()
    parser.add_libs_arg()
    parser.add_rng_arg()
    parser.add_argument('-s', '--lgr-set', metavar='LGR-SET', action='append',
                        help='LGR in the set (can be used multiple times)', required=True)

    args = parser.parse_args()
    parser.setup_logger()

    if len(args.lgr_set) == 1:
        logger.error("Please provide more than one LGR to make a set")
        return

    logger.info('Please wait, this can take some time...\n')

    merged_lgr, lgr_set = merge_lgrs(args.lgr_set, rng=args.rng, unidb=parser.get_unidb())
    if not merged_lgr:
        return

    for out in cross_script_variants(merged_lgr, get_stdin()):
        write_output(out)


if __name__ == '__main__':
    main()
