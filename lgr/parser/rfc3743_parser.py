# -*- coding: utf-8 -*-
"""
rfc3743_parser.py - 
"""
from __future__ import unicode_literals
import logging
import os
import io
import re

from lgr.core import LGR
from lgr.metadata import Version
from lgr.exceptions import LGRException
from lgr.utils import format_cp
from lgr.parser.parser import LGRParser


logger = logging.getLogger(__name__)

REFERENCE_RE = re.compile(r'Reference\s+(?P<ref_id>\d)\s+(?P<value>[^#]+)\s*(?:#\s*(?P<comment>.*))?')
VERSION_RE = re.compile(r'Version\s+(?P<version_no>\d)\s+(?P<date>\d{8})\s*(?:#\s*(?P<comment>.*))?')

# RFC3743 defines a code point without the "U+" notation,
# however some files use the "U+" prefix.
# Try to support both.
UNICODE_CODEPOINT_RE = re.compile(r'(?:U\+)?(?P<codepoint>[0-9a-fA-F]{4,6})(\((?P<references>\d(,\d)*)\))?')


class RFC3743Parser(LGRParser):

    def unicode_version(self):
        # No Unicode version defined in file
        return ""

    def validate_document(self, schema=None):
        # No validation of document done for now
        return ""

    def parse_document(self):
        if not self.filename and isinstance(self.source, str):
            self.filename = os.path.basename(self.source)

        self._lgr = LGR(name=self.filename)

        logger.debug('Start parsing of file: %s', self.filename)

        if hasattr(self.source, "read"):
            self._parse_doc(self.source)
        else:
            with io.open(self.source, 'r', encoding='utf-8') as rule_file:
                self._parse_doc(rule_file)

        return self._lgr

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

            reference = REFERENCE_RE.match(line)
            if reference is not None:
                ref_id = reference.group('ref_id')
                value = reference.group('value')
                comment = reference.group('comment')
                try:
                    self._lgr.add_reference(value, ref_id=ref_id,
                                            comment=comment)
                except LGRException:
                    logger.error("Invalid reference '%s' on line %d",
                                 line, line_num)
                continue

            version = VERSION_RE.match(line)
            if version is not None:
                version_no = version.group('version_no')
                date = version.group('date')
                comment = version.group('comment')

                try:
                    self._lgr.metadata.version = Version(version_no,
                                                        comment=comment)
                    self._lgr.metadata.date = date
                except LGRException:
                    logger.error("Invalid version '%s' on line %d",
                                 line, line_num)
                continue

            if UNICODE_CODEPOINT_RE.match(line) is None:
                logger.debug("Skipping non-parsable line %d:\n%s",
                             line_num, line)
                # Line is not starting with a valid unicode code point, skip
                continue

            # Split base character from variant(s)
            char_variant = line.split(';')
            char = char_variant[0]

            try:
                [(codepoints, references)] = parse_char(char)
                self._lgr.add_cp(codepoints, ref=references)
            except ValueError:
                logger.error("Invalid character '%s' at line %d", char, line_num)
            except LGRException as exc:
                logger.error("Cannot add code point '%s' at line %d: %s",
                             format_cp(codepoints),
                             line_num,
                             exc)

            if len(char_variant) > 1:
                preferred_variants = char_variant[1].strip()
                if len(preferred_variants) > 0 and preferred_variants[0] != '#':
                    # From RFC7940, Section 7.3. Recommended Disposition Values:
                    # activated  The resulting string should be activated for use.  (This
                    # is the same as a Preferred Variant [RFC3743].)
                    var_type = "activated"
                    self.insert_variant(line_num,
                                        codepoints,
                                        preferred_variants,
                                        var_type)

            if len(char_variant) > 2:
                variants = char_variant[2].strip()
                if len(variants) > 0 and variants[0] != '#':
                    self.insert_variant(line_num, codepoints, variants)

    def insert_variant(self, line_num, codepoints, var, var_type=None):
        try:
            variants = parse_char(var)
        except ValueError:
            logger.error("Invalid variant '%s' at line %d", var, line_num)
            return

        for (var_codepoints, references) in variants:
            try:
                self._lgr.add_variant(codepoints, var_codepoints,
                                      ref=references, variant_type=var_type)
            except LGRException as exc:
                logger.error("Cannot add variant '%s' to code point '%s' at line %d: %s",
                             format_cp(var_codepoints),
                             format_cp(codepoints),
                             line_num,
                             exc)


def parse_char(char):
    """
    Parse a RFC3743 PreferredVariant/CharacterVariant definition.

    For example:
    1234(1,2),5678(0) -> [([0x1234], [1,2]),([0x5678], [0])]

    :param str char: Input char in the "U+" notation.
    :return list[(list[int], list[str])]: List of tuple (code point as a list of int,
                                                         list of associated references).
    :raises ValueError if one of the code point is not a valid Unicode code point.
    """
    codepoints = []
    for match in UNICODE_CODEPOINT_RE.finditer(char):
        codepoint = int(match.group('codepoint'), 16)
        references = match.group('references')

        ref_list = []
        if references is not None:
            ref_list = references.split(',')

        codepoints.append(([codepoint], ref_list))

    return codepoints
