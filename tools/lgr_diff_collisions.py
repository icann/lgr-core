#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_diff_collisions.py - CLI tool to make the diff on a list of labels
                         confronted to 2 LGR and/or to test a set of labels for
                         collisions in one or both LGR
"""
from __future__ import unicode_literals

import io
import logging

from lgr.tools.diff_collisions import diff, collision
from lgr.tools.utils import write_output
from tools.utils import LgrToolArgParser, parse_lgr

logger = logging.getLogger("lgr_diff_collision")


def main():
    parser = LgrToolArgParser(description='LGR diff and collision CLI')
    parser.add_common_args()
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
    parser.add_argument('-n', '--no-rules', action='store_true',
                        help='Do not print rules as it may be very very '
                             'verbose (None will be printed instead)')

    args = parser.parse_args()
    parser.setup_logger()

    unidb = parser.get_unidb()

    lgr1 = parse_lgr(args.first, args.rng, unidb)
    lgr2 = None
    if args.second is not None:
        lgr2 = parse_lgr(args.second, args.rng, unidb)
    else:
        write_output("No second LGR, will only output collisions")

    if lgr1 is None:
        logger.error("Error while parsing first LGR file.")
        logger.error("Please check compliance with RNG.")
        return
    if args.second is not None and lgr2 is None:
        logger.error("Error while parsing second LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    logger.warning('Please wait, this can take some time...\n')

    with io.open(args.set, 'r', encoding='utf-8') as label_input:
        if lgr2:
            for out in diff(lgr1, lgr2, label_input, True, args.generate,
                            args.no_rules):
                write_output(out)
        else:
            for out in collision(lgr1, label_input, None, args.generate, args.no_rules):
                write_output(out)


if __name__ == '__main__':
    main()
