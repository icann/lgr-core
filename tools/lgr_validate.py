#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_validate.py - CLI tool which validate a label and generate its variants.

This is a lightweight version of lgr_cli tool, only dedicated to validate
a label and generate its variants.
"""
from __future__ import unicode_literals

import sys
import codecs
import argparse
import logging

from lgr.parser.xml_parser import XMLParser
from munidata import UnicodeDataVersionManager

logger = logging.getLogger("lgr_validate")


def write_output(s):
    print(s.encode('utf-8'))


def check_label(lgr, label, generate_variants=False):
    from lgr.utils import format_cp
    label_cp = tuple([ord(c) for c in label])

    write_output("Label: %s [%s]" % (label, format_cp(label_cp)))

    (eligible, label_part, not_in_lgr, disp, _, _) = lgr.test_label_eligible(label_cp)
    write_output("- Eligible: %s" % eligible)
    write_output("- Disposition: %s" % disp)

    if eligible:
        if generate_variants:
            summary, labels = lgr.compute_label_disposition_summary(label_cp)
            for (variant_cp, var_disp, _, _, _) in labels:
                variant_u = ''.join([unichr(c) for c in variant_cp])
                write_output("\tVariant %s [%s]" % (variant_u, format_cp(variant_cp)))
                write_output("\t- Disposition: '%s'" % var_disp)
    else:
        write_output("- Valid code points from label: %s" % u' '.join(u"{:04X}".format(cp) for cp in label_part))
        write_output("- Invalid code points from label: %s" % u' '.join(u"{:04X}".format(cp) for cp in not_in_lgr))


def main():
    parser = argparse.ArgumentParser(description='LGR CLI')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries')
    parser.add_argument('-v', '--variants', action='store_true',
                        help='Generate variants')
    parser.add_argument('xml', metavar='XML')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    lgr_parser = XMLParser(args.xml)

    unidb = None
    if args.libs is not None:
        libpath, i18n_libpath, libver = args.libs.split('#')
        manager = UnicodeDataVersionManager()
        unidb = manager.register(None, libpath, i18n_libpath, libver)

    if args.rng is not None:
        validation_result = lgr_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation: %s', validation_result)

    if unidb is not None:
        lgr_parser.unicode_database = unidb

    lgr = lgr_parser.parse_document()
    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    label_input = codecs.getreader('utf8')(sys.stdin)

    for label in label_input.read().splitlines():
        check_label(lgr, label, args.variants)

if __name__ == '__main__':
    main()
