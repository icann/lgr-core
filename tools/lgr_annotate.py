#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_annotate.py - Annotate a set of labels with disposition.

Take a LGR and a label list in a file, output label list with disposition.
"""
from __future__ import unicode_literals

import sys
import argparse
import logging
import io

from munidata import UnicodeDataVersionManager

from lgr.parser.xml_parser import XMLParser

logger = logging.getLogger("lgr_annotate")


def main():
    parser = argparse.ArgumentParser(description='LGR Collision CLI')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries', required=True)
    parser.add_argument('-s', '--set', metavar='SET_FILE',
                        help='Filepath to the set of reference labels',
                        required=True)
    parser.add_argument('-o', '--output', metavar='OUTPUT_FILE',
                        help='Filepath to output the annotated labels',
                        required=True)
    parser.add_argument('xml', metavar='XML')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)

    libpath, i18n_libpath, libver = args.libs.split('#')
    manager = UnicodeDataVersionManager()
    unidb = manager.register(None, libpath, i18n_libpath, libver)

    lgr_parser = XMLParser(args.xml)
    lgr_parser.unicode_database = unidb

    lgr = lgr_parser.parse_document()
    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    # Compute index label
    with io.open(args.set, 'r', encoding='utf-8') as label_input:
        with io.open(args.output, 'w', encoding='utf-8') as label_output:
            for label in label_input.readlines():
                label = label.strip()
                label_output.write(label)
                if label.startswith('#') or label == '':
                    label_output.write('\n')
                    continue
                label_cp = tuple([ord(c) for c in label])
                disp = lgr.test_label_eligible(label_cp)[3]
                label_output.write(": %s" % (disp))
                label_output.write('\n')


if __name__ == '__main__':
    main()
