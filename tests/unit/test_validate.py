# -*- coding: utf-8 -*-
"""
test_validate.py - Unit testing of LGR validation module.
"""
from __future__ import unicode_literals

import unittest
import logging
from cStringIO import StringIO

from lgr.core import LGR
from lgr.validate import check_symmetry, check_transitivity, check_conditional_variants


class TestSymmetry(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.DEBUG)
        logging.getLogger('lgr.validate').addHandler(ch)

    def test_empty_lgr(self):
        check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)

    def test_no_symmetric_in_repertoire(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         "CP U+0061: Variant U+0062 is not in repertoire.\n")

    def test_no_symmetric_in_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         'CP U+0062 should have CP U+0061 in its variants.\n')

    def test_symmetry_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061])
        check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)


class TestTransitivity(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.DEBUG)
        logging.getLogger('lgr.validate').addHandler(ch)

    def test_empty_lgr(self):
        check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)

    def test_no_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)

    def test_no_transitivity(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0063])
        self.lgr.add_cp([0x0063])
        check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         'CP U+0061 should have CP U+0063 in its variants.\n')

    def test_transitivity_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_variant([0x0061], [0x0063])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0063])
        self.lgr.add_cp([0x0063])
        check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)


class TestConditionalVariants(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.DEBUG)
        logging.getLogger('lgr.validate').addHandler(ch)

    def test_empty_lgr(self):
        check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)

    def test_no_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)

    def test_no_rule(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when="when-rule")
        check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         "CP U+0061: Variant 'U+0062' \"when\" attribute "
                         "'when-rule' is not an existing rule name.\n")

    def test_conditional_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when="when-rule")
        self.lgr.rules.append("when-rule")
        check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)

if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
