# -*- coding: utf-8 -*-
"""
heuristic_parser.py - Guess the right parser to use (either rfc3743, rfc4290 or lgr and act like it).
"""
import io
import logging

from lgr.parser.parser import LGRParser
from lgr.parser.rfc3743_parser import RFC3743Parser
from lgr.parser.rfc3743_parser import UNICODE_CODEPOINT_RE as RFC3743_REGEX
from lgr.parser.rfc4290_parser import RFC4290Parser
from lgr.parser.rfc4290_parser import UNICODE_CODEPOINT_RE as RFC4290_REGEX
from lgr.parser.xml_parser import XMLParser

logger = logging.getLogger(__name__)


class HeuristicParser(LGRParser):

    def __init__(self, source, filename=None):
        super().__init__(source, filename)
        self.lgr_parser = None

    def unicode_version(self):
        return self.lgr_parser.unicode_version()

    def validate_document(self, schema=None):
        if hasattr(self.source, "read"):
            self._find_parser(self.source)
        else:
            with io.open(self.source, 'r', encoding='utf-8') as rule_file:
                self._find_parser(rule_file)

        return self.lgr_parser.validate_document()

    def _find_parser(self, rule_file):
        if self.lgr_parser:
            return

        if self._is_lgr(rule_file.readline().decode('utf-8')):
            self.lgr_parser = XMLParser(rule_file, self.filename)
        else:
            self._check_rfc_format(rule_file)

        if not self.lgr_parser:
            # default to LGR XML parser
            self.lgr_parser = XMLParser(rule_file, self.filename)

        rule_file.seek(0)

    def _check_rfc_format(self, rule_file):
        for line in rule_file:
            line = line.decode('utf-8')
            if RFC3743_REGEX.match(line.strip()):
                self.lgr_parser = RFC3743Parser(io.StringIO(rule_file.read().decode('utf-8')), self.filename)
                break
            if RFC4290_REGEX.match(line.strip()):
                if ';' in line:
                    self.lgr_parser = RFC3743Parser(io.StringIO(rule_file.read().decode('utf-8')), self.filename)
                    break
                else:
                    self.lgr_parser = RFC4290Parser(io.StringIO(rule_file.read().decode('utf-8')), self.filename)
                    break

    def _parse_doc(self, rule_file):
        """
        Actual parsing of document.

        :param rule_file: Content of the rule, as a file-like object.
        """
        self._find_parser(rule_file)

        self._lgr = self.lgr_parser.parse_document()

    def _is_lgr(self, first_line):
        return '<?xml' in first_line or str(self.filename).endswith('.xml')
