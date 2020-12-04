#!/bin/env python
# -*- coding: utf-8 -*-
"""
one_per_line_dump.py - Tool to parse a "one codepoint per line" file and dump LGR on stdout
"""
from __future__ import unicode_literals

from lgr.tools.utils import LgrDumpTool


def main():
    from lgr.parser.line_parser import LineParser

    tool = LgrDumpTool(LineParser, description='Parse and dump a "one codepoint per line" file')
    tool.run()


if __name__ == '__main__':
    main()
