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

        self.assertEquals(0, len(result))

    def test_non_compliant(self):
        lgr = load_lgr('idna2008_compliance', 'non_compliant.xml', unidb=self.unidb)

        result = check_idna2008_compliance(lgr)

        self.assertEquals(1, len(result))
        self.assertListEqual([{
            'cp': (65,),
            'glyph': 'A',
            'name': "LATIN CAPITAL LETTER A",
            'idna_property': 'DISALLOWED',
            'category': 'Lu'
        }], result)


if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
