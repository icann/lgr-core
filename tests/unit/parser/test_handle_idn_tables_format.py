#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_handle_idn_tables_format -
"""
import logging
import os
from unittest import TestCase

from lgr.char import Char
from lgr.core import LGR
from lgr.parser.heuristic_parser import HeuristicParser
from lgr.parser.rfc3743_parser import RFC3743Parser
from lgr.parser.rfc4290_parser import RFC4290Parser
from lgr.parser.xml_parser import XMLParser

logger = logging.getLogger('test_handle_idn_tables_format')


class Test(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_filename(self):
        parser = self.load_parser('one_per_line.txt')
        self.assertEqual('one_per_line.txt', parser.filename)

    def test_rfc3743_jpan_return_format_rfc3743(self):
        parser = self.load_parser('rfc3743_jpan.txt')
        parser.parse_document()
        self.assertIsInstance(parser.lgr_parser, RFC3743Parser)

    def test_rfc3743_tw_return_format_rfc3743(self):
        parser = self.load_parser('rfc3743_tw.txt')
        parser.parse_document()
        self.assertIsInstance(parser.lgr_parser, RFC3743Parser)

    def test_rfc4290_return_format_rfc4290(self):
        parser = self.load_parser('rfc4290_de.txt')
        parser.parse_document()
        self.assertIsInstance(parser.lgr_parser, RFC4290Parser)

    def test_lgr_return_format_lgr_with_rng(self):
        parser = self.load_parser('../lgr.rng')
        parser.parse_document()
        self.assertIsInstance(parser.lgr_parser, XMLParser)

    def test_lgr_return_format_lgr_with_xml(self):
        parser = self.load_parser('../idn_table_review/reference_lgr.xml')
        parser.parse_document()
        self.assertIsInstance(parser.lgr_parser, XMLParser)

    def test_rfc3743_1cp_semicolon(self):
        parser = self.load_parser('3743-1cp-semicolon.txt')
        lgr: LGR = parser.parse_document()
        self.assertListEqual([(0x32,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([], [c.cp for c in lgr.get_variants((0x32,))])

    def test_rfc3743_1cp_semicolon_ref(self):
        parser = self.load_parser('3743-1cp-semicolon-ref.txt')
        lgr: LGR = parser.parse_document(force=True)
        self.assertListEqual([(0x31,)], [c.cp for c in lgr.repertoire])
        char: Char = lgr.get_char((0x31,))
        # self.assertListEqual([0], char.references)  # XXX ref is not set as not defined in IDN table
        self.assertListEqual([], [c.cp for c in lgr.get_variants((0x31,))])

    def test_rfc3743_2cp_1line(self):
        parser = self.load_parser('3743-2cp-1line.txt')
        lgr: LGR = parser.parse_document()
        self.assertListEqual([(0x38,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x39,)], [c.cp for c in lgr.get_variants((0x38,))])

    def test_rfc3743_2cp_1line_refs(self):
        parser = self.load_parser('3743-2cp-1line-refs.txt')
        lgr: LGR = parser.parse_document(force=True)
        self.assertListEqual([(0x38,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x39,)], [c.cp for c in lgr.get_variants((0x38,))])

    def test_rfc3743_2vars_ref(self):
        parser = self.load_parser('3743-2vars-ref.txt')
        lgr: LGR = parser.parse_document(force=True)
        self.assertListEqual([(0x3447,), (0x3473,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x3447,), (0x3473,)], [c.cp for c in lgr.get_variants((0x3447,))])
        self.assertListEqual([(0x3447,)], [c.cp for c in lgr.get_variants((0x3473,))])

    def test_rfc3743_missing_var_ref(self):
        parser = self.load_parser('3743-missing-var-ref.txt')
        lgr: LGR = parser.parse_document(force=True)
        self.assertListEqual([(0x3447,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x3447,), (0x3473,)], [c.cp for c in lgr.get_variants((0x3447,))])

    def test_rfc4290_1cp(self):
        parser = self.load_parser('4290-1cp.txt')
        lgr: LGR = parser.parse_document()
        self.assertListEqual([(0x2200,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([], [c.cp for c in lgr.get_variants((0x2200,))])

    def test_rfc4290_2cp_1line(self):
        parser = self.load_parser('4290-2cp-1line.txt')
        lgr: LGR = parser.parse_document()
        self.assertListEqual([(0x2201,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x0043,)], [c.cp for c in lgr.get_variants((0x2201,))])

    def test_rfc4290_2var_same_char(self):
        parser = self.load_parser('4290-2var-same-char.txt')
        lgr: LGR = parser.parse_document()
        self.assertListEqual([(0x2202,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x0064,), (0x03B4,)], [c.cp for c in lgr.get_variants((0x2202,))])

    def test_rfc4290_var_string(self):
        parser = self.load_parser('4290-var-string.txt')
        lgr: LGR = parser.parse_document()
        self.assertListEqual([(0x2237,)], [c.cp for c in lgr.repertoire])
        self.assertListEqual([(0x003A, 0x003A)], [c.cp for c in lgr.get_variants((0x2237,))])

    def load_parser(self, name, unidb=None):
        parser = HeuristicParser(
            os.path.join(os.path.dirname(__file__), '..', '..', 'inputs', 'parser', name))
        if unidb:
            parser.unicode_database = unidb
        return parser
