#!/bin/env python2
# -*- coding: utf-8 -*-
"""
one_per_line_dump.py - Tool to parse a "one codepoint per line" file and dump LGR on stdout
"""
from __future__ import unicode_literals
import sys
import argparse
import logging
import os
import io


def main():
    from lgr.parser.line_parser import LineParser
    from lgr.parser.xml_serializer import serialize_lgr_xml

    parser = argparse.ArgumentParser(description='Parse and dump a "one codepoint per line" file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-o', '--output', metavar='OUTPUT',
                        help='Optional output file')
    parser.add_argument('file', metavar='FILE')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.INFO)

    parser = LineParser(args.file)
    lgr = parser.parse_document()

    xml = serialize_lgr_xml(lgr, pretty_print=True)
    if args.output is not None:
        with io.open(args.output, mode='wb') as output:
            output.write(xml)
    else:
        print(xml)

if __name__ == '__main__':
    # XXX: Add LGR module to PYTHONPATH
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 '..'))
    main()
