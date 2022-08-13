# -*- coding: utf-8 -*-
"""
rfc4290_parser.py - Parse a RFC4290 compliant file.
"""
from __future__ import unicode_literals

import logging
import os
import re

from lgr.exceptions import LGRException
from lgr.parser.parser import LGRParser
from lgr.utils import format_cp

logger = logging.getLogger(__name__)

UNICODE_CODEPOINT_RE = re.compile(r'U\+([0-9a-fA-F]{4,6})')


class RFC4290Parser(LGRParser):
    def unicode_version(self):
        # No Unicode version defined in file
        return ""

    def validate_document(self, schema=None):
        # No validation of document done for now
        return True

    def parse_document(self):
        if not self.filename and isinstance(self.source, str):
            self.filename = os.path.basename(self.source)

        return super().parse_document()

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
            if UNICODE_CODEPOINT_RE.match(line) is None:
                # Line is not starting with a valid unicode code point, skip
                continue

            # Remove comments and split base character from variant(s)
            char_variant = line.split('#')[0].split('|')
            char = char_variant[0]

            try:
                codepoints = parse_char(char)
                self._lgr.add_cp(codepoints, force=self.force)
            except ValueError:
                logger.error("Invalid character '%s' at line %d", char,
                             line_num)
            except LGRException as exc:
                logger.error("Cannot add code point '%s' at line %d: %s",
                             format_cp(codepoints),
                             line_num,
                             exc)

            # Handle variants, if any
            if len(char_variant) > 1:
                variants = char_variant[1].split(':')

                for var in variants:
                    try:
                        var_codepoints = parse_char(var)
                        self._lgr.add_variant(codepoints, var_codepoints, force=self.force)
                    except ValueError:
                        logger.error("Invalid variant '%s' at line %d", var,
                                     line_num)
                    except LGRException as exc:
                        logger.error("Cannot add variant '%s' to code point '%s' at line %d: %s",
                                     format_cp(var_codepoints),
                                     format_cp(codepoints),
                                     line_num,
                                     exc)


def parse_char(char):
    """
    Parse a char definition.

    For example, U+1234-U+5678 will return [0x1234, 0x5678].

    :param str char: Input char in the "U+" notation.
    :return list[int]: List of code point as int
    :raises ValueError if one of the code point is not a valid Unicode code point.
    """
    codepoints = []
    chars = char.split('-')
    for c in chars:
        codepoint_re = UNICODE_CODEPOINT_RE.match(c)
        if codepoint_re is not None:
            codepoints.append(int(codepoint_re.group(1), 16))
        else:
            raise ValueError(c)

    return codepoints
