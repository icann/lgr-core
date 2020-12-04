#!/bin/env python
# -*- coding: utf-8 -*-
"""
rfc3743_dump.py - Tool to parse a RFC3743 file and dump LGR on stdout
"""
from __future__ import unicode_literals

from tools.utils import LgrDumpTool


def main():
    from lgr.parser.rfc3743_parser import RFC3743Parser

    tool = LgrDumpTool(RFC3743Parser, description='Parse and dump a RFC3743 file')
    tool.run()


if __name__ == '__main__':
    main()
