#!/bin/env python
# -*- coding: utf-8 -*-
"""
xml_dump.py - Tool to parse a XML file and dump LGR on stdout
"""
from __future__ import unicode_literals
import sys
import argparse
import logging
import os
import io


def main():
    from lgr.parser.xml_parser import XMLParser
    from lgr.parser.xml_serializer import serialize_lgr_xml

    parser = argparse.ArgumentParser(description='Parse and dump a LGR XML file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-o', '--output', metavar='OUTPUT',
                        help='Optional output file')
    parser.add_argument('xml', metavar='XML')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.INFO)

    lgr_parser = XMLParser(args.xml)

    if args.rng is not None:
        validation_result = lgr_parser.validate_document(args.rng)
        if validation_result is not None:
            print(validation_result)
            return

    lgr = lgr_parser.parse_document()

    if args.verbose:
        for char in lgr.repertoire:
            print(char)

    if args.output is not None:
        xml = serialize_lgr_xml(lgr, pretty_print=True)
        with io.open(args.output, mode='wb') as output:
            output.write(xml)
    else:
        print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))


if __name__ == '__main__':
    main()
