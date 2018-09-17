# -*- coding: utf-8 -*-
"""
__init__.py - Definition some py2/3 compat stuff
"""
from __future__ import unicode_literals
import sys

if sys.version_info.major > 2:
    text_type = str
else:
    text_type = unicode

if sys.maxunicode > 65535:
    wide_unichr = chr if sys.version_info.major > 2 else unichr
else:
    def wide_unichr(ord):
        if ord > 0xffff:
            return (br'\U%08X' % ord).decode('unicode-escape')
        else:
            r_chr = chr if sys.version_info.major > 2 else unichr
            return r_chr(ord)
