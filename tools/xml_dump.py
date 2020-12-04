#!/bin/env python
# -*- coding: utf-8 -*-
"""
xml_dump.py - Tool to parse a XML file and dump LGR on stdout
"""
from __future__ import unicode_literals

import io

from tools.utils import LgrToolArgParser


def main():
    from lgr.parser.xml_serializer import serialize_lgr_xml

    parser = LgrToolArgParser(description='Parse and dump a LGR XML file')
    parser.add_logging_args()
    parser.add_rng_arg()
    parser.add_argument('-o', '--output', metavar='OUTPUT',
                        help='Optional output file')
    parser.add_xml_meta()

    args = parser.parse_args()
    parser.setup_logger()

    lgr = parser.parse_lgr()
    if not lgr:
        return

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
