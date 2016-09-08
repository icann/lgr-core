# -*- coding: utf-8 -*-
"""
test_matcher.py - Unit testing of matcher module.
"""
from __future__ import unicode_literals

import unittest

from lgr.matcher import (StartMatcher,
                         EndMatcher,
                         AnchorMatcher,
                         LookAheadMatcher,
                         LookBehindMatcher,
                         CountMatcher,
                         ChoiceMatcher,
                         AnyMatcher,
                         CharMatcher)


class TestMatcher(unittest.TestCase):

    def test_start_matcher(self):
        self.assertEqual(StartMatcher().get_pattern({}, {}, None), '^')

    def test_end_matcher(self):
        self.assertEqual(EndMatcher().get_pattern({}, {}, None), '$')

    def test_anchor_matcher(self):
        anchor = AnchorMatcher()
        self.assertEqual(anchor.get_pattern({}, {}, None),
                         '%(anchor)s')

    def test_look_ahead_matcher(self):
        look = LookAheadMatcher()
        look.add_child(CharMatcher([0x002A]))
        look.add_child(CharMatcher([0x002B]))

        self.assertEqual(look.get_pattern({}, {}, None),
                         '(?=\\x{2A}\\x{2B})')

    def test_look_behind_matcher(self):
        look = LookBehindMatcher()
        look.add_child(CharMatcher([0x002A]))
        look.add_child(CharMatcher([0x002B]))

        self.assertEqual(look.get_pattern({}, {}, None),
                         '(?<=\\x{2A}\\x{2B})')

    def test_count_matcher(self):
        self.assertEqual(CountMatcher().get_pattern({}, {}, None), '')
        self.assertEqual(CountMatcher(count='1').get_pattern(), '{1}')
        self.assertEqual(CountMatcher(count='10').get_pattern(), '{10}')
        self.assertEqual(CountMatcher(count='3+').get_pattern(), '{3,}')
        self.assertEqual(CountMatcher(count='4:7').get_pattern(), '{4,7}')

    def test_choice_matcher(self):
        choice = ChoiceMatcher()
        choice.add_child(StartMatcher())
        choice.add_child(EndMatcher())

        self.assertEqual(choice.get_pattern({}, {}, None), "(?:(?:^)|(?:$))")

    def test_choice_with_count_matcher(self):
        choice = ChoiceMatcher(count="10")
        choice.add_child(StartMatcher())
        choice.add_child(EndMatcher())

        self.assertEqual(choice.get_pattern({}, {}, None), "(?:(?:^)|(?:$)){10}")

    def test_any_matcher(self):
        self.assertEqual(AnyMatcher().get_pattern({}, {}, None), '.')
        self.assertEqual(AnyMatcher(count='2').get_pattern({}, {}, None),
                         '.{2}')
        self.assertEqual(AnyMatcher(count='2+').get_pattern({}, {}, None),
                         '.{2,}')

    def test_char_matcher(self):
        self.assertEqual(CharMatcher([0x002A]).get_pattern({}, {}, None),
                         '\\x{2A}')
        self.assertEqual(CharMatcher([0x002A, 0x002B]).get_pattern({}, {}, None),
                         '\\x{2A}\\x{2B}')


if __name__ == '__main__':
    import logging
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
