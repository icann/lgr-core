#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_diff_collisions.py - CLI tool to make the diff on a list of labels
                         confronted to 2 LGR and/or to test a set of labels for
                         collisions in one or both LGR
"""
from __future__ import unicode_literals

import sys
import argparse
import logging
import io

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_parser import XMLParser

from lgr.tools.diff_collisions import diff, collision

logger = logging.getLogger("lgr_diff_collision")



def write_output(s):
    print(s.encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='LGR diff and collision CLI')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries', required=True)
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-1', '--first', metavar='LGR1',
                        help='First LGR',
                        required=True)
    parser.add_argument('-2', '--second', metavar='LGR2',
                        help='Second LGR',
                        required=False)
    parser.add_argument('-s', '--set', metavar='SET_FILE',
                        help='Filepath to the set of reference labels',
                        required=True)
    parser.add_argument('-g', '--generate', action='store_true',
                        help='Generate a full dump')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Do not print rules as it may be very very '
                        'verbose (None will be printed instead)')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    libpath, i18n_libpath, libver = args.libs.split('#')
    manager = UnicodeDataVersionManager()
    unidb = manager.register(None, libpath, i18n_libpath, libver)

    lgr1_parser = XMLParser(args.first)
    lgr1_parser.unicode_database = unidb
    if args.second is not None:
        lgr2_parser = XMLParser(args.second)
        lgr2_parser.unicode_database = unidb
    else:
        write_output("No second LGR, will only output collisions")

    if args.rng is not None:
        validation_result = lgr1_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation of first LGR: %s',
                         validation_result)
        if args.second is not None:
            validation_result = lgr2_parser.validate_document(args.rng)
            if validation_result is not None:
                logger.error('Errors for RNG validation of second LGR: %s',
                             validation_result)

    lgr1 = lgr1_parser.parse_document()
    if lgr1 is None:
        logger.error("Error while parsing first LGR file.")
        logger.error("Please check compliance with RNG.")
        return
    if args.second is not None:
        lgr2 = lgr2_parser.parse_document()
        if lgr2 is None:
            logger.error("Error while parsing second LGR file.")
            logger.error("Please check compliance with RNG.")
            return

    write_output('Please wait, this can take some time...\n')

    with io.open(args.set, 'r', encoding='utf-8') as label_input:
        if args.second is not None:
            for out in diff(lgr1, lgr2, label_input, True, args.generate,
                            args.quiet):
                write_output(out)
        else:
            for out in collision(lgr1, label_input, args.generate, args.quiet):
                write_output(out)


if __name__ == '__main__':
    main()


