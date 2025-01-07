# -*- coding: utf-8 -*-
"""
test_harmonize.py - Unit testing of LGR harmonization module.
"""
from __future__ import unicode_literals

import logging
import unittest

from lgr.tools.idna2008_compliance import check_idna2008_compliance
from tests.unit.unicode_database_mock import UnicodeDatabaseMock
from tests.unit.utils import load_lgr


class TestIDNA2008Compliance(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.unidb = UnicodeDatabaseMock()

    def test_compliant(self):
        lgr = load_lgr('idna2008_compliance', 'compliant.xml', unidb=self.unidb)

        result = check_idna2008_compliance(lgr)

        self.assertEqual(7, result['compliant_nbr'])
        self.assertFalse(result['contains_non_compliant'])
        self.assertEqual(0, len(result['non_compliant']))

    def test_non_compliant(self):
        lgr = load_lgr('idna2008_compliance', 'non_compliant.xml', unidb=self.unidb)

        result = check_idna2008_compliance(lgr)
        non_compliant = result['non_compliant']

        self.assertEqual(6, result['compliant_nbr'])
        self.assertTrue(result['contains_non_compliant'])
        self.assertEqual(1, len(non_compliant))
        self.assertListEqual([{
            'cp': (65,),
            'glyph': 'A',
            'name': "LATIN CAPITAL LETTER A",
            'idna_property': 'DISALLOWED',
            'category': 'Lu',
            'idna2003_compliant': True
        }], non_compliant)

    def test_non_compliant_idna2003(self):
        lgr = load_lgr('idna2008_compliance', 'non_compliant_idna2003.xml', unidb=self.unidb)

        result = check_idna2008_compliance(lgr)
        non_compliant = result['non_compliant']

        self.assertEqual(6, result['compliant_nbr'])
        self.assertTrue(result['contains_non_compliant'])
        self.assertEqual(2, len(non_compliant))
        self.assertListEqual([{
            'cp': (65,),
            'glyph': 'A',
            'name': "LATIN CAPITAL LETTER A",
            'idna_property': 'DISALLOWED',
            'category': 'Lu',
            'idna2003_compliant': True
        }, {
            'cp': (1304,),
            'glyph': 'Ԙ',
            'name': "CYRILLIC CAPITAL LETTER YAE",
            'idna_property': 'DISALLOWED',
            'category': 'Lu',
            'idna2003_compliant': False
        }], non_compliant)


if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
