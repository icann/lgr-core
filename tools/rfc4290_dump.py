#!/bin/env python2
# -*- coding: utf-8 -*-
"""
rfc4290_dump.py - Tool to parse a RFC4290 file and dump LGR on stdout
"""
from __future__ import unicode_literals
import sys
import argparse
import logging
import os
import io
from lxml import etree

def main():
    from lgr.parser.rfc4290_parser import RFC4290Parser
    from lgr.parser.xml_serializer import serialize_lgr_xml

    parser = argparse.ArgumentParser(description='Parse and dump a RFC4290 file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-o', '--output', metavar='OUTPUT',
                        help='Optional output file')
    parser.add_argument('file', metavar='FILE')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.INFO)

    rfc_parser = RFC4290Parser(args.file)
    lgr = rfc_parser.parse_document()

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
