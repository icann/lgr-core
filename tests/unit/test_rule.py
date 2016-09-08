# -*- coding: utf-8 -*-
"""
test_rule.py - Unit testing of rule module.
"""
from __future__ import unicode_literals

import unittest

from lgr.rule import Rule
from lgr.matcher import (AnchorMatcher,
                         LookAheadMatcher,
                         CharMatcher)
from lgr.exceptions import LGRFormatException


class TestRule(unittest.TestCase):

    def setUp(self):
        self.rule = Rule('test')

    def test_simple_matcher(self):
        self.rule.add_child(CharMatcher([0x002A]))
        self.assertEqual(self.rule.get_pattern({}, {}, None),
                         '\\x{2A}')

    def test_anchor_look_ahead_rule(self):
        self.rule.add_child(AnchorMatcher())
        look = LookAheadMatcher()
        look.add_child(CharMatcher([0x002A]))
        self.rule.add_child(look)
        self.assertEqual(self.rule.get_pattern({}, {}, None),
                         '%(anchor)s(?=\\x{2A})')

    def test_by_ref_rule(self):
        rules_lookup = {
            'test': self.rule
        }
        by_ref_rule = Rule(by_ref='test')
        self.assertEqual(by_ref_rule.get_pattern(rules_lookup, {}, None),
                         self.rule.get_pattern({}, {}, None))

    def test_no_name_by_ref_rule(self):
        with self.assertRaises(LGRFormatException) as exc_cm:
            Rule(name='this-will-fail', by_ref='test')

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

    def test_validate_named_rule(self):
        rule = Rule(name='named-rule')
        rule.validate([], {}, {})

        with self.assertRaises(LGRFormatException) as exc_cm:
            rule.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_TOP_LEVEL_NAME)

    def test_validate_by_ref_rule(self):
        rule = Rule(by_ref='named-rule')
        rule.validate([None], {'named-rule': None}, {})

        with self.assertRaises(LGRFormatException) as exc_cm:
            rule.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_BY_REF)

    def test_validate_composed_rules(self):
        rule = Rule(name='top-level-rule')
        rule.add_child(Rule(name='child-rule'))

        with self.assertRaises(LGRFormatException) as exc_cm:
            rule.validate([], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_TOP_LEVEL_NAME)


if __name__ == '__main__':
    unittest.main()
