# -*- coding: utf-8 -*-
"""
heuristic_parser.py - Guess the right parser to use (either rfc3743, rfc4290
or lgr and act like it).
"""
from __future__ import unicode_literals

import logging

from lgr.parser.parser import LGRParser
from lgr.parser.rfc3743_parser import RFC3743Parser, UNICODE_CODEPOINT_RE as \
  rfc3743_regex
from lgr.parser.rfc4290_parser import RFC4290Parser, UNICODE_CODEPOINT_RE as \
  rfc4290_regex
from lgr.parser.xml_parser import XMLParser

logger = logging.getLogger(__name__)


class HeuristicParser(LGRParser):

  def __init__(self, source, filename=None):
    super().__init__(source, filename)
    self.lgr_parser = None

  def unicode_version(self):
    return self.lgr_parser.unicode_version()

  def validate_document(self, schema):
    return self.lgr_parser.validate_document()

  def _parse_doc(self, rule_file):
    """
    Actual parsing of document.

    :param rule_file: Content of the rule, as a file-like object.
    """
    for line in rule_file:
      if self._is_lgr(line):
        self.lgr_parser = XMLParser(self.source)
      if rfc3743_regex.match(line.strip()):
        self.lgr_parser = RFC3743Parser(self.source)
      if rfc4290_regex.match(line.strip()):
        if ';' in line:
          self.lgr_parser = RFC3743Parser(self.source)
        else:
          self.lgr_parser = RFC4290Parser(self.source)
      if self.lgr_parser:
        self.lgr_parser.parse_document()
        return

  def _is_lgr(self, line):
    return line.startswith('<?xml version=') or str(self.filename).endswith(
        '.xml')
