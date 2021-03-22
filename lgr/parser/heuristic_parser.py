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

        first_line = rule_file.readline()
        is_str = True
        if not isinstance(first_line, str):
            is_str = False
            first_line = first_line.decode('utf-8')
        if self._is_lgr(first_line):
            self.lgr_parser = XMLParser(self.source, self.filename)
        else:
            self._check_rfc_format(rule_file, is_str)

        if not self.lgr_parser:
            # default to LGR XML parser
            self.lgr_parser = XMLParser(self.source, self.filename)

        if hasattr(rule_file, "seek"):
            rule_file.seek(0)

    def _check_rfc_format(self, rule_file, is_str):
        def get_source():
            # be careful, calling this reset the file, therefore the parsing loop should stop after it
            if not is_str:
                if hasattr(rule_file, "seek"):
                    rule_file.seek(0)
                return io.StringIO(rule_file.read().decode('utf-8'))
            if hasattr(self.source, "seek"):
                self.source.seek(0)
            return self.source

        match = False
        for line in rule_file:
            if not is_str:
                line = line.decode('utf-8')
            if RFC3743_REGEX.match(line) and not RFC4290_REGEX.match(line):
                self.lgr_parser = RFC3743Parser(get_source(), self.filename)
                break
            elif RFC4290_REGEX.match(line.strip()):
                match = True
                if ';' in line:
                    self.lgr_parser = RFC3743Parser(get_source(), self.filename)
                    break
                elif '|' in line:
                    self.lgr_parser = RFC4290Parser(get_source(), self.filename)
                    break

        if not self.lgr_parser and match:
            # we got through the whole file and we got matches with RFC formats but we did not get a way to
            # discriminate therefore select RFC4290
            # Note: this is because we accept RFC3743 without semicolon on code point line
            self.lgr_parser = RFC4290Parser(get_source(), self.filename)

    def _parse_doc(self, rule_file):
        """
        Actual parsing of document.

        :param rule_file: Content of the rule, as a file-like object.
        """
        self._find_parser(rule_file)

        self._lgr = self.lgr_parser.parse_document()

    def _is_lgr(self, first_line):
        return '<?xml' in first_line or '<lgr' in first_line or str(self.filename).endswith('.xml')
