# -*- coding: utf-8 -*-
"""
test_harmonize.py - Unit testing of LGR harmonization module.
"""
from __future__ import unicode_literals

import unittest
import logging
import os

from lgr.parser.xml_parser import XMLParser
from lgr.tools.harmonize import harmonize


def load_lgr(name):
    parser = XMLParser(os.path.join(os.path.dirname(__file__), '..', 'inputs', 'harmonization', name))
    return parser.parse_document()


class TestHarmonize(unittest.TestCase):

    def test_case_1(self):
        hindi = load_lgr('hindi.xml')
        nepali = load_lgr('nepali.xml')

        hindi_harmonized, nepali_harmonized, log = harmonize(hindi, nepali)

        self.assertEqual(len(hindi_harmonized.repertoire), 5)
        for cp, var_cp in ((0x0061, 0x0062), (0x0062, 0x0061), (0x0063, 0x0064), (0x0064, 0x0063)):
            char = hindi_harmonized.get_char(cp)
            variants = list(char.get_variants())
            self.assertEqual(len(variants), 1)
            self.assertEqual(variants[0].cp, (var_cp, ))

        char = hindi_harmonized.get_char(0x0065)
        variants = list(char.get_variants())
        self.assertEqual(len(variants), 0)

        self.assertEqual(len(nepali_harmonized.repertoire), 4)
        for cp, var_cp in ((0x0061, 0x0062), (0x0062, 0x0061), (0x0063, 0x0064), (0x0064, 0x0063)):
            char = nepali_harmonized.get_char(cp)
            variants = list(char.get_variants())
            self.assertEqual(len(variants), 1)
            var = variants[0]
            self.assertEqual(var.cp, (var_cp, ))

        self.assertEqual(nepali_harmonized.get_variant(0x0063, (0x0064, ))[0].type, 'blocked')
        self.assertEqual(nepali_harmonized.get_variant(0x0064, (0x0063, ))[0].type, 'blocked')

    def test_case_2(self):
        hindi = load_lgr('hindi-rz.xml')
        nepali = load_lgr('nepali-rz.xml')
        rz = load_lgr('rz-lgr.xml')

        hindi_harmonized, nepali_harmonized, log = harmonize(hindi, nepali, rz)

        self.assertEqual(len(hindi.repertoire) + 1, len(hindi_harmonized.repertoire))
        self.assertEqual(len(nepali.repertoire) + 1, len(nepali_harmonized.repertoire))

        for lgr, cp, var_cp in ((hindi_harmonized, 0x0066, 0x0065), (nepali_harmonized, 0x0065, 0x0066)):
            char = lgr.get_char(cp)
            self.assertEqual(char.comment, 'Out-of-repertoire')
            variants = list(char.get_variants())
            self.assertEqual(len(variants), 1)
            self.assertEqual(variants[0].cp, (var_cp, ))
            self.assertEqual(variants[0].type, 'blocked')

            var_char = lgr.get_char(var_cp)
            variants = list(var_char.get_variants())
            self.assertEqual(len(variants), 1)
            self.assertEqual(variants[0].cp, (cp, ))
            self.assertEqual(variants[0].type, 'blocked')

    def test_case_3(self):
        hindi = load_lgr('hindi-log.xml')
        nepali = load_lgr('nepali-log.xml')
        rz = load_lgr('rz-lgr.xml')

        hindi_harmonized, nepali_harmonized, (log_hindi, log_nepali) = harmonize(hindi, nepali, rz)

        self.assertEqual(len(hindi.repertoire), len(hindi_harmonized.repertoire))
        self.assertEqual(len(nepali.repertoire), len(nepali_harmonized.repertoire))

        self.assertEqual(log_hindi, {(0x0079, )})
        self.assertEqual(log_nepali, {(0x007A, )})

    def test_lgr_with_range(self):
        a_z = load_lgr('a-z-range.xml')
        a_b = load_lgr('a-b.xml')

        a_z_harmonized, a_b_harmonized, _ = harmonize(a_z, a_b)

        for cp, var_cp in ((0x0061, 0x0062), (0x0062, 0x0061)):
            char = a_z_harmonized.get_char(cp)
            variants = list(char.get_variants())
            self.assertEqual(len(variants), 1)
            self.assertEqual(variants[0].cp, (var_cp, ))
            self.assertEqual(variants[0].type, 'blocked')


if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
