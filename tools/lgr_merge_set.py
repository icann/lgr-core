#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_merge_set.py - CLI tool merge a set of LGRs
"""
from __future__ import unicode_literals

import sys
import argparse
import logging

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_serializer import serialize_lgr_xml

from lgr.tools.utils import merge_lgrs

logger = logging.getLogger("lgr_merge_set")


def main():
    parser = argparse.ArgumentParser(description='LGR diff and collision CLI')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    parser.add_argument('-l', '--libs', metavar='LIBS', help='ICU libraries')
    parser.add_argument('-r', '--rng', metavar='RNG', help='RelaxNG XML schema')
    parser.add_argument('-n', '--name', metavar='NAME', help="Merged LGR name")
    parser.add_argument('-s', '--lgr-set', metavar='LGR-SET', action='append',
                        help='LGR in the set (can be used multiple times)', required=True)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    unidb = None
    if args.libs:
        libpath, i18n_libpath, libver = args.libs.split('#')
        manager = UnicodeDataVersionManager()
        unidb = manager.register(None, libpath, i18n_libpath, libver)

    if len(args.lgr_set) == 1:
        logger.error("Please provide more than one LGR to make a set")
        return

    logger.warning('Please wait, this can take some time...\n')

    merged_lgr, _ = merge_lgrs(args.lgr_set, name=args.name, rng=args.rng, unidb=unidb)
    if not merged_lgr:
        return
    print(serialize_lgr_xml(merged_lgr, pretty_print=True))


if __name__ == '__main__':
    main()
