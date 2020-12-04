#!/bin/env python
# -*- coding: utf-8 -*-
"""
rfc4290_dump.py - Tool to parse a RFC4290 file and dump LGR on stdout
"""
from __future__ import unicode_literals

from tools.utils import LgrDumpTool


def main():
    from lgr.parser.rfc4290_parser import RFC4290Parser

    tool = LgrDumpTool(RFC4290Parser, description='Parse and dump a RFC4290 file')
    tool.run()


if __name__ == '__main__':
    main()
