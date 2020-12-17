#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
test_variant_sets -
"""
import logging
import os
from unittest import TestCase

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
    parser = self.load_parser('lgr.rng')
    parser.parse_document()
    self.assertIsInstance(parser.lgr_parser, XMLParser)

  def test_lgr_return_format_lgr_with_xml(self):
    parser = self.load_parser('idn_table_review/reference_lgr.xml')
    parser.parse_document()
    self.assertIsInstance(parser.lgr_parser, XMLParser)

  def load_parser(self, name, unidb=None):
    parser = HeuristicParser(
      os.path.join(os.path.dirname(__file__), '../../inputs', name))
    if unidb:
      parser.unicode_database = unidb
    return parser
