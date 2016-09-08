# -*- coding: utf-8 -*-
"""
test_action.py - Unit testing of action module.
"""
from __future__ import unicode_literals

import unittest

from lgr.exceptions import LGRFormatException
from lgr.action import Action


class TestAction(unittest.TestCase):

    def test_match_not_match_action(self):
        with self.assertRaises(LGRFormatException) as exc_cm:
            Action(disp='invalid', match='match', not_match='not-match')

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.MATCH_NOT_MATCH)

    def test_catch_all_action(self):
        action = Action(disp='my-disp')
        self.assertEqual('my-disp',
                         action.apply([], set(), False, {}, {}, None))
        self.assertEqual('my-disp',
                         action.apply([], set(['disp']), False,
                                      {}, {}, None))
        self.assertEqual('my-disp',
                         action.apply([], set(), True, {}, {}, None))
        self.assertEqual('my-disp',
                         action.apply([], set(['disp']), True,
                                      {}, {}, None))

    def test_any_variant_action(self):
        action = Action(disp='my-disp', any_variant=['disp1', 'disp2'])
        self.assertIsNone(action.apply([], set(), False, {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp9']), False,
                                       {}, {}, None))
        self.assertEqual('my-disp', action.apply([], set(['disp1']), False,
                                                 {}, {}, None))
        self.assertEqual('my-disp', action.apply([],
                                                 set(['disp1', 'disp2']), False,
                                                 {}, {}, None))
        self.assertEqual('my-disp', action.apply([],
                                                 set(['disp1', 'disp9']), False,
                                                 {}, {}, None))

    def test_all_variants_action(self):
        action = Action(disp='my-disp', all_variants=['disp1', 'disp2'])
        self.assertIsNone(action.apply([], set(), False, {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp9']), False,
                                       {}, {}, None))
        self.assertEqual('my-disp', action.apply([], set(['disp1']), False,
                                                 {}, {}, None))
        self.assertEqual('my-disp', action.apply([],
                                                 set(['disp1', 'disp2']), False,
                                                 {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp1', 'disp9']), False,
                                       {}, {}, None))

    def test_only_variants_action(self):
        action = Action(disp='my-disp', only_variants=['disp1', 'disp2'])
        self.assertIsNone(action.apply([], set(), False, {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp9']), False,
                                       {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp1']), False,
                                                 {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp1', 'disp2']), False,
                                                 {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp1', 'disp9']), False,
                                       {}, {}, None))
        self.assertIsNone(action.apply([], set(), False, {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp9']), True,
                                       {}, {}, None))
        self.assertEqual('my-disp', action.apply([], set(['disp1']), True,
                                                 {}, {}, None))
        self.assertEqual('my-disp', action.apply([],
                                                 set(['disp1', 'disp2']),
                                                 True,
                                                 {}, {}, None))
        self.assertIsNone(action.apply([], set(['disp1', 'disp9']), True,
                                       {}, {}, None))

if __name__ == '__main__':
    import logging
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
