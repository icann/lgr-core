# -*- coding: utf-8 -*-
"""
line_parser.py - Parse a simple "one code point per line" file.
"""
from __future__ import unicode_literals
import logging
import io
import re

from lgr.exceptions import LGRException
from lgr.utils import format_cp
from lgr.parser.parser import LGRParser


logger = logging.getLogger(__name__)

UNICODE_CODEPOINT_RE = re.compile(r'U\+([0-9a-fA-F]{4,6})')


class LineParser(LGRParser):

    def unicode_version(self):
        # No Unicode version defined for now
        return ""

    def validate_document(self, schema=None):
        # No validation for now
        return True

    def _parse_doc(self, rule_file):
        """
        Actual parsing of document.

        :param rule_file: Content of the rule, as a file-like object.
        """
        line_num = 0
        for line in rule_file:
            line_num += 1

            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue

            codepoints = []
            for cp in UNICODE_CODEPOINT_RE.finditer(line):
                try:
                    codepoints.append(int(cp.group(1), 16))
                except ValueError:
                    logger.error("Invalid code point '%s' at line %d",
                                 cp, line_num)

            try:
                self._lgr.add_cp(codepoints)
            except LGRException as exc:
                logger.error("Cannot add code point '%s' at line %d: %s",
                             format_cp(codepoints),
                             line_num,
                             exc)
