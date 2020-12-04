#!/bin/env python
# -*- coding: utf-8 -*-
"""
one_per_line_dump.py - Tool to parse a "one codepoint per line" file and dump LGR on stdout
"""
from __future__ import unicode_literals

import io

from tools.utils import LgrToolArgParser


def main():
    from lgr.parser.line_parser import LineParser
    from lgr.parser.xml_serializer import serialize_lgr_xml

    parser = LgrToolArgParser(description='Parse and dump a "one codepoint per line" file')
    parser.add_logging_args()
    parser.add_argument('-o', '--output', metavar='OUTPUT',
                        help='Optional output file')
    parser.add_argument('file', metavar='FILE')

    args = parser.parse_args()
    parser.setup_logger()

    parser = LineParser(args.file)
    lgr = parser.parse_document()

    if args.output is not None:
        xml = serialize_lgr_xml(lgr, pretty_print=True)
        with io.open(args.output, mode='wb') as output:
            output.write(xml)
    else:
        print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))


if __name__ == '__main__':
    main()
