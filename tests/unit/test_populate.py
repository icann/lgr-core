# -*- coding: utf-8 -*-
"""
test_populate.py - Unit testing of LGR populate module.
"""
from __future__ import unicode_literals

import unittest
import logging
from io import StringIO

from lgr.core import LGR
from lgr.populate import populate_lgr


class TestPopulate(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.INFO)
        logger = logging.getLogger('lgr.populate')
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)

    def test_no_symmetric_in_repertoire(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add missing code point 'U+0062' in LGR as it is a variant of 'U+0061'\n"
                         "Add code point 'U+0061' as variant of 'U+0062' for symmetry\n", log_content)
        self.assertIn(0x0062, self.lgr.repertoire)
        new_variant = self.lgr.get_char([0x0062])
        self.assertEqual([(0x0061,)], [c.cp for c in new_variant.get_variants()])

    def test_no_symmetric_in_repertoire_twice(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_variant([0x0061], [0x0063])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061])
        self.lgr.add_variant([0x0062], [0x0063])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add missing code point 'U+0063' in LGR as it is a variant of 'U+0061'\n"
                         "Add code point 'U+0061' as variant of 'U+0063' for symmetry\n"
                         "Add code point 'U+0062' as variant of 'U+0063' for symmetry\n", log_content)
        self.assertIn(0x0063, self.lgr.repertoire)
        new_variant = self.lgr.get_char([0x0063])
        self.assertEqual([(0x0061,), (0x0062,)], [c.cp for c in new_variant.get_variants()])

    def test_no_symmetric_in_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add code point 'U+0061' as variant of 'U+0062' for symmetry\n", log_content)
        cp = self.lgr.get_char([0x0062])
        self.assertEqual([(0x0061,)], [c.cp for c in cp.get_variants()])

    def test_no_transitivity(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0063])
        self.lgr.add_cp([0x0063])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add code point 'U+0061' as variant of 'U+0062' for symmetry\n"
                         "Add code point 'U+0062' as variant of 'U+0063' for symmetry\n"
                         "Add code point 'U+0063' as variant of 'U+0061' for transitivity with 'U+0062'\n"
                         "Add code point 'U+0061' as variant of 'U+0063' for transitivity with 'U+0062'\n", log_content)
        cp = self.lgr.get_char([0x0061])
        self.assertEqual([(0x0062,), (0x0063,)], [c.cp for c in cp.get_variants()])
        cp = self.lgr.get_char([0x0062])
        self.assertEqual([(0x0061,), (0x0063,)], [c.cp for c in cp.get_variants()])
        cp = self.lgr.get_char([0x0063])
        self.assertEqual([(0x0061,), (0x0062,)], [c.cp for c in cp.get_variants()])

    def test_no_symmetric_rule_when_in_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when='test-when')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061])
        populate_lgr(self.lgr)
        print(self.log_output.getvalue())
        log_content = self.log_output.getvalue()
        self.assertEqual("Update variant 'U+0061' of code point 'U+0062' for contextual rule when symmetry\n",
                         log_content)
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].when, 'test-when')

    def test_no_symmetric_rule_not_when_in_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], not_when='test-not-when')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Update variant 'U+0061' of code point 'U+0062' for contextual rule not-when symmetry\n",
                         log_content)
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].not_when, 'test-not-when')

    def test_no_symmetric_variant_with_rule_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when='test-when')
        self.lgr.add_cp([0x0062])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add code point 'U+0061' with when rule test-when as variant of 'U+0062' for symmetry\n",
                         log_content)
        cp = self.lgr.get_char([0x0062])
        self.assertEqual([(0x0061,)], [c.cp for c in cp.get_variants()])
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].when, 'test-when')

    def test_no_symmetric_variant_with_rule_not_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], not_when='test-not-when')
        self.lgr.add_cp([0x0062])
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add code point 'U+0061' with not-when rule test-not-when as variant of 'U+0062' for "
                         "symmetry\n", log_content)
        cp = self.lgr.get_char([0x0062])
        self.assertEqual([(0x0061,)], [c.cp for c in cp.get_variants()])
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].not_when, 'test-not-when')

    def test_no_symmetric_rule_in_variants_when_not_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when='test-when')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061], not_when='test-not-when')
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Add code point 'U+0061' as variant of 'U+0062' for contextual rule when symmetry\n"
                         "Add code point 'U+0062' as variant of 'U+0061' for contextual rule not-when symmetry\n",
                         log_content)
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 2)
        self.assertEqual(v[0].not_when, 'test-not-when')
        self.assertEqual(v[1].when, 'test-when')
        v = self.lgr.get_variant([0x0061], (0x0062,))
        self.assertEqual(len(v), 2)
        self.assertEqual(v[0].when, 'test-when')
        self.assertEqual(v[1].not_when, 'test-not-when')

    def test_no_symmetric_rule_when_in_variants_with_when(self):
        # nothing should change in that case, we cannot achieve variant contextual rules symmetry
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when='test-when')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061], when='test-when-not-matching')
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Could not achieve rule symmetry for variant 'U+0061' of code point 'U+0062' as it already "
                         "has a when rule\n"
                         "Could not achieve rule symmetry for variant 'U+0062' of code point 'U+0061' as it already "
                         "has a when rule\n", log_content)
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].when, 'test-when-not-matching')
        v = self.lgr.get_variant([0x0061], (0x0062,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].when, 'test-when')

    def test_no_symmetric_rule_not_when_in_variants_with_not_when(self):
        # nothing should change in that case, we cannot achieve variant contextual rules symmetry
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], not_when='test-not-when')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061], not_when='test-not-when-not-matching')
        populate_lgr(self.lgr)
        log_content = self.log_output.getvalue()
        self.assertEqual("Could not achieve rule symmetry for variant 'U+0061' of code point 'U+0062' as it already "
                         "has a not-when rule\n"
                         "Could not achieve rule symmetry for variant 'U+0062' of code point 'U+0061' as it already "
                         "has a not-when rule\n", log_content)
        v = self.lgr.get_variant([0x0062], (0x0061,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].not_when, 'test-not-when-not-matching')
        v = self.lgr.get_variant([0x0061], (0x0062,))
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].not_when, 'test-not-when')


if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
