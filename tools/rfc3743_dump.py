#!/bin/env python
# -*- coding: utf-8 -*-
"""
rfc3743_dump.py - Tool to parse a RFC3743 file and dump LGR on stdout
"""
from __future__ import unicode_literals
import sys
import argparse
import logging
import io


def main():
    from lgr.parser.rfc3743_parser import RFC3743Parser
    from lgr.parser.xml_serializer import serialize_lgr_xml

    parser = argparse.ArgumentParser(description='Parse and dump a RFC3743 file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-o', '--output', metavar='OUTPUT',
                        help='Optional output file')
    parser.add_argument('file', metavar='FILE')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.INFO)

    rfc_parser = RFC3743Parser(args.file)
    lgr = rfc_parser.parse_document()

    if args.output is not None:
        xml = serialize_lgr_xml(lgr, pretty_print=True)
        with io.open(args.output, mode='wb') as output:
            output.write(xml)
    else:
        print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))


if __name__ == '__main__':
    main()
