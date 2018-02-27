# -*- coding: utf-8 -*-
"""
test_char.py - Unit testing of character module.
"""
from __future__ import unicode_literals

import unittest
import itertools
import types

from lgr.char import (Variant,
                      CharBase,
                      Char,
                      RangeChar,
                      CharSequence,
                      Repertoire)
from lgr.exceptions import (NotInLGR,
                            CharAlreadyExists,
                            RangeAlreadyExists,
                            VariantAlreadyExists,
                            LGRFormatException)


class TestVariant(unittest.TestCase):

    def test_simple_hash(self):
        v1 = Variant([1])
        v2 = Variant([1], 'BLOCK')
        v3 = Variant([2])

        self.assertEqual(v1.__hash__(), v2.__hash__())
        self.assertNotEqual(v1.__hash__(), v3.__hash__())

    def test_equal_when_not_when(self):
        v1 = Variant([1], when='w-1')
        v2 = Variant([1], when='w-2')
        v3 = Variant([1], not_when='nw-1')
        v4 = Variant([1], not_when='nw-2')
        v5 = Variant([1], when='w-1', not_when='nw-1')
        v6 = Variant([1], when='w-2', not_when='nw-1')
        v7 = Variant([1], when='w-1', not_when='nw-2')
        v8 = Variant([1], when='w-2', not_when='nw-2')
        variants = [v1, v2, v3, v4, v5, v6, v7, v8]
        for (a, b) in itertools.product(variants, variants):
            if a is b:
                # 'Memory' equality: a and b point to the same object.
                continue
            self.assertNotEqual(a, b)

    def test_hash_when_not_when(self):
        v1 = Variant([1], when='w-1')
        v2 = Variant([1], when='w-2')
        v3 = Variant([1], not_when='nw-1')
        v4 = Variant([1], not_when='nw-2')
        v5 = Variant([1], when='w-1', not_when='nw-1')
        v6 = Variant([1], when='w-2', not_when='nw-1')
        v7 = Variant([1], when='w-1', not_when='nw-2')
        v8 = Variant([1], when='w-2', not_when='nw-2')
        variants = [v1, v2, v3, v4, v5, v6, v7, v8]
        for (a, b) in itertools.product(variants, variants):
            if a is b:
                # 'Memory' equality: a and b point to the same object.
                continue
            self.assertNotEqual(a.__hash__(), b.__hash__())


class TestChar(unittest.TestCase):

    def test_equal_cp(self):
        self.assertEqual(Char([0x002A]), Char([0x002A]))
        self.assertNotEqual(Char([0x002A]), Char([0x002B]))
        c1 = Char(0x002A)
        c2 = Char(0x002A)
        self.assertEqual(c1, c2)

    def test_char_factory(self):
        self.assertIsInstance(CharBase.from_cp_or_sequence(0x002A), Char)
        self.assertIsInstance(CharBase.from_cp_or_sequence([0x002A]), Char)
        self.assertIsInstance(CharBase.from_cp_or_sequence([0x002A, 0x002B]),
                              CharSequence)

    def test_as_index(self):
        self.assertEqual(Char(0x002A).as_index(), 0x002A)
        self.assertEqual(CharSequence((0x002A, 0x002B)).as_index(),
                         0x002A)
        self.assertEqual(RangeChar(0x002A, 0x002A, 0x02C).as_index(),
                         0x002A)
        self.assertEqual(CharBase.from_cp_or_sequence(0x002A).as_index(),
                         0x002A)
        self.assertEqual(CharBase.from_cp_or_sequence([0x002A]).as_index(),
                         0x002A)
        self.assertEqual(CharBase.from_cp_or_sequence([0x002A,
                                                       0x002B]).as_index(),
                         0x002A)

    def test_len(self):
        self.assertEqual(len(Char(0x002A)), 1)
        self.assertEqual(len(CharBase.from_cp_or_sequence([0x002A, 0x002B])), 2)
        self.assertEqual(len(RangeChar(0x002A, 0x002A, 0x002B)), 1)

    def test_is_prefix_of(self):
        c = Char(0x002A)
        s = CharBase.from_cp_or_sequence([0x002A, 0x002B])
        r = RangeChar(0x002A, 0x002A, 0x002B)

        self.assertTrue(c.is_prefix_of([0x002A]))
        self.assertTrue(r.is_prefix_of([0x002A]))
        self.assertTrue(c.is_prefix_of([0x002A, 0x002B]))
        self.assertTrue(r.is_prefix_of([0x002A, 0x002B]))
        self.assertTrue(s.is_prefix_of([0x002A, 0x002B]))
        self.assertTrue(s.is_prefix_of([0x002A, 0x002B, 0x002C]))

        self.assertFalse(c.is_prefix_of([0x002B]))
        self.assertFalse(r.is_prefix_of([0x002B]))
        self.assertFalse(s.is_prefix_of([0x002B, 0x002A]))
        self.assertFalse(s.is_prefix_of([0x002A]))
        self.assertFalse(s.is_prefix_of([0x002B]))

    def test_hash_char(self):
        c1 = Char(0x002A)
        c2 = Char(0x002A)
        c3 = Char(0x002B)
        self.assertEqual(c1.__hash__(), c2.__hash__())
        self.assertNotEqual(c1.__hash__(), c3.__hash__())

    def test_hash_sequence(self):
        c1 = CharSequence((0x002A, 0x002B))
        c2 = CharSequence((0x002A, 0x002B))
        c3 = CharSequence((0x002A, 0x002C))
        c4 = CharSequence((0x002A, 0x002B, 0x002C))
        c5 = CharSequence((0x002A, 0x002C, 0x002B))

        self.assertEqual(c1.__hash__(), c2.__hash__())
        self.assertNotEqual(c1.__hash__(), c3.__hash__())
        self.assertNotEqual(c1.__hash__(), c4.__hash__())
        self.assertNotEqual(c1.__hash__(), c5.__hash__())
        self.assertNotEqual(c3.__hash__(), c4.__hash__())
        self.assertNotEqual(c3.__hash__(), c5.__hash__())
        self.assertNotEqual(c4.__hash__(), c5.__hash__())

    def test_char_range(self):
        char = Char(0x002A)
        range_char = RangeChar(0x002A, 0x002A, 0x002B)
        self.assertEqual(char, range_char)
        self.assertEqual(char.__hash__(), range_char.__hash__())

    def test_add_variant(self):
        c = Char(0x002A)
        c.add_variant([0x0030])

        self.assertEqual(len(c._variants), 1)
        self.assertIn((0x0030,), c._variants)
        self.assertEqual(len(c._variants[(0x0030,)]), 1)
        self.assertEqual(c._variants[(0x0030,)][0].cp, (0x0030,))

        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030])

        c.add_variant([0x0030], when='w1')
        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030],
                          when='w1')

        c.add_variant([0x0030], not_when='w1')
        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030],
                          not_when='w1')

        c.add_variant([0x0030], when='w1', not_when='nw-1')
        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030],
                          when='w1', not_when='nw-1')

        self.assertEqual(len(c._variants[(0x0030,)]), 4)


    def test_add_variant_sequence(self):
        c = CharSequence([0x002A, 0x002B])
        c.add_variant([0x0030])

        self.assertEqual(len(c._variants), 1)
        self.assertIn((0x0030,), c._variants)
        self.assertEqual(len(c._variants[(0x0030,)]), 1)
        self.assertEqual(c._variants[(0x0030,)][0].cp, (0x0030,))

        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030])

        c.add_variant([0x0030], when='w1')
        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030],
                          when='w1')

        c.add_variant([0x0030], not_when='w1')
        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030],
                          not_when='w1')

        c.add_variant([0x0030], when='w1', not_when='nw-1')
        self.assertRaises(VariantAlreadyExists, c.add_variant, [0x0030],
                          when='w1', not_when='nw-1')

        self.assertEqual(len(c._variants[(0x0030,)]), 4)
    def test_add_variant_range(self):
        range_char = RangeChar(0x002A, 0x002A, 0x002B)
        with self.assertRaises(LGRFormatException) as cm:
            range_char.add_variant([0x0030])

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.RANGE_NO_CHILD)

    def test_del_variant(self):
        c = Char(0x002A)
        c.add_variant([0x0030])
        c.del_variant([0x0030])

        self.assertEqual(len(c._variants), 0)

        c.add_variant([0x0030])
        c.add_variant([0x0031])
        c.del_variant([0x0031])

        self.assertEqual(len(c._variants), 1)
        self.assertIn((0x0030,), c._variants)
        self.assertEqual(len(c._variants[(0x0030,)]), 1)
        self.assertEqual(c._variants[(0x0030,)][0].cp, (0x0030,))

        c.add_variant([0x0030], when='w1')
        c.del_variant([0x0030], when='w1')
        self.assertEqual(len(c._variants[(0x0030,)]), 1)
        self.assertEqual(c._variants[(0x0030,)][0].cp, (0x0030,))
        self.assertIsNone(c._variants[(0x0030,)][0].when)

    def test_del_variant_range(self):
        range_char = RangeChar(0x002A, 0x002A, 0x002B)
        with self.assertRaises(LGRFormatException) as cm:
            range_char.del_variant([0x0030])

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.RANGE_NO_CHILD)

    def test_get_variants(self):
        c = Char(0x002A)
        c.add_variant([0x0030])
        c.add_variant([0x0030], when='w1')
        c.add_variant([0x0030], not_when='w1')
        c.add_variant([0x0030], when='w1', not_when='nw-1')

        variants = c.get_variants()

        self.assertIsInstance(variants, types.GeneratorType)

        variant_list = list(variants)
        self.assertEqual(len(variant_list), 4)

        expected_output = [
            Variant((0x0030,)),
            Variant((0x0030, ), when='w1'),
            Variant((0x0030, ), not_when='w1'),
            Variant((0x0030, ), when='w1', not_when='nw-1')
        ]

        self.assertEqual(variant_list, expected_output)

    def test_get_variant(self):
        c = Char(0x002A)
        c.add_variant([0x0030], when='w1')
        c.add_variant([0x0031], when='w2')
        c.add_variant([0x0031], not_when='nw-1')

        variant = c.get_variant((0x031, ))
        expected_output = [
            Variant((0x0031, ), when='w2'),
            Variant((0x0031, ), not_when='nw-1')
        ]

        self.assertEqual(variant, expected_output)


class TestRepertoire(unittest.TestCase):

    def setUp(self):
        self.cd = Repertoire()

    def test_add_single_char(self):
        self.cd.add_char([0x002A])
        self.assertIn(0x002A, self.cd)
        char = self.cd[0x002A]
        self.assertIsInstance(char, Char)

    def test_add_char_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        self.assertIn([0x002A, 0x002B], self.cd)
        self.assertNotIn(0x002A, self.cd)
        self.assertNotIn(0x002B, self.cd)
        char = self.cd[[0x002A, 0x002B]]
        self.assertIsInstance(char, CharSequence)

    def test_add_existing_char(self):
        self.cd.add_char([0x002A])
        with self.assertRaises(CharAlreadyExists) as exc_cm:
            self.cd.add_char([0x002A])

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.cp, (0x002A, ))

    def test_add_multiple_char_sequences(self):
        self.cd.add_char([0x002A, 0x002B])
        self.cd.add_char([0x002A, 0x002B, 0x002C])
        self.assertIn([0x002A, 0x002B], self.cd)
        self.assertIn([0x002A, 0x002B, 0x002C], self.cd)
        char = self.cd[[0x002A, 0x002B]]
        self.assertIsInstance(char, CharSequence)
        self.assertEqual(char.__hash__(), (0x002A, 0x002B).__hash__())

    def test_add_existing_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        with self.assertRaises(CharAlreadyExists) as exc_cm:
            self.cd.add_char([0x002A, 0x002B])

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.cp, (0x002A, 0x002B))

    def test_del_single_char(self):
        self.cd.add_char([0x002A])
        self.cd.del_char([0x002A])
        self.assertNotIn(0x002A, self.cd)

    def test_del_char_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        self.cd.del_char([0x002A, 0x002B])
        self.assertEqual(len(self.cd), 0)

    def test_del_char_sequence_with_cp(self):
        self.cd.add_char([0x002A, 0x002B])
        self.assertRaises(NotInLGR, self.cd.del_char, [0x002A])
        self.assertRaises(NotInLGR, self.cd.del_char, [0x002B])
        self.assertIn([0x002A, 0x002B], self.cd)

    def test_add_range(self):
        self.cd.add_range(0x002A, 0x0030)
        for cp in range(0x002A, 0x0030 + 1):
            self.assertIn(cp, self.cd)
            range_char = self.cd[cp]
            self.assertEqual(range_char.cp, (cp, ))
            self.assertEqual(range_char.first_cp, 0x002A)
            self.assertEqual(range_char.last_cp, 0x0030)

    def test_add_existing_range(self):
        self.cd.add_range(0x002A, 0x0030)
        self.assertRaises(RangeAlreadyExists,
                          self.cd.add_range, 0x002A, 0x0030)

    def test_add_range_overlap(self):
        self.cd.add_char([0x002A])
        self.assertRaises(CharAlreadyExists,
                          self.cd.add_range, 0x002A, 0x0030)

    def test_check_range_overlap(self):
        self.cd.ranges = [(5, 10), (20, 30)]
        self.assertFalse(self.cd._check_range_overlap(1, 2))
        self.assertTrue(self.cd._check_range_overlap(1, 5))
        self.assertTrue(self.cd._check_range_overlap(6, 8))
        self.assertTrue(self.cd._check_range_overlap(5, 10))
        self.assertTrue(self.cd._check_range_overlap(7, 13))
        self.assertTrue(self.cd._check_range_overlap(10, 15))
        self.assertFalse(self.cd._check_range_overlap(15, 18))
        self.assertTrue(self.cd._check_range_overlap(19, 23))
        self.assertTrue(self.cd._check_range_overlap(20, 25))
        self.assertTrue(self.cd._check_range_overlap(24, 31))
        self.assertTrue(self.cd._check_range_overlap(20, 30))
        self.assertTrue(self.cd._check_range_overlap(30, 31))
        self.assertFalse(self.cd._check_range_overlap(31, 55))

    def test_del_range(self):
        self.cd.add_range(0x002A, 0x0030)
        self.cd.del_range(0x002A, 0x0030)
        self.assertEqual(len(self.cd), 0)
        self.assertRaises(NotInLGR, self.cd.del_range, 0x002A, 0x0030)

    def test_get_char(self):
        single_char = self.cd.add_char([0x002A])
        sequence_char = self.cd.add_char([0x002B, 0x002C])
        self.cd.add_range(0x002D, 0x0030)

        self.assertIs(single_char, self.cd.get_char([0x002A]))
        self.assertIs(sequence_char, self.cd.get_char([0x002B, 0x002C]))
        for cp in range(0x002D, 0x0030 + 1):
            char = self.cd.get_char([cp])
            self.assertIsInstance(char, RangeChar)
            self.assertEqual(0x002D, char.first_cp)
            self.assertEqual(0x0030, char.last_cp)

    def test_add_single_variant_single_cp(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030])

        self.assertIn((0x0030, ), self.cd[0x002A]._variants)

    def test_add_single_variant_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        self.cd.add_variant([0x002A, 0x002B], [0x0030])

        self.assertIn((0x0030, ), self.cd[[0x002A, 0x002B]]._variants)

    def test_add_sequence_variant_single_cp(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030, 0x0031])

        self.assertIn((0x0030, 0x0031), self.cd[0x002A]._variants)

    def test_add_sequence_variant_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        self.cd.add_variant([0x002A, 0x002B], [0x0030, 0x0031])

        self.assertIn((0x0030, 0x0031), self.cd[[0x002A, 0x002B]]._variants)

    def test_add_variant_when(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030], when='w1')

        self.assertIn((0x0030, ), self.cd[0x002A]._variants)
        self.assertEqual(self.cd[0x002A]._variants[(0x0030,)][0].when,
                         'w1')

    def test_del_single_variant_single_cp(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030])
        self.cd.del_variant([0x002A], [0x0030])

        self.assertEqual(len(self.cd[0x02A]._variants), 0)

    def test_del_single_variant_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        self.cd.add_variant([0x002A, 0x002B], [0x0030])
        self.cd.del_variant([0x002A, 0x002B], [0x0030])

        self.assertEqual(len(self.cd[[0x002A, 0x002B]]._variants), 0)

    def test_del_sequence_variant_single_cp(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030, 0x0031])
        self.cd.del_variant([0x002A], [0x0030, 0x0031])

        self.assertEqual(len(self.cd[0x02A]._variants), 0)

    def test_del_sequence_variant_sequence(self):
        self.cd.add_char([0x002A, 0x002B])
        self.cd.add_variant([0x002A, 0x002B], [0x0030, 0x0031])
        self.cd.del_variant([0x002A, 0x002B], [0x0030, 0x0031])

        self.assertEqual(len(self.cd[[0x002A, 0x002B]]._variants), 0)

    def test_del_variant_when(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030], when='w1')
        self.cd.del_variant([0x002A], [0x0030], when='w1')

        self.assertEqual(len(self.cd[0x02A]._variants), 0)

    def test_iter(self):
        self.cd.add_char([0x0010])
        self.cd.add_range(0x0001, 0x000A)
        self.cd.add_char([0x0000])
        self.cd.add_char([0x0011, 0x0012])
        self.cd.add_char([0x0013])

        expected_output = [
            Char(0x0000),
            RangeChar(0x0001, 0x0001, 0x000A),
            Char(0x0010),
            CharSequence([0x0011, 0x0012]),
            Char(0x0013),
        ]

        self.assertEqual(list(self.cd), expected_output)

    def test_all_repertoire(self):
        self.cd.add_char([0x0010])
        self.cd.add_range(0x0001, 0x0005)
        self.cd.add_char([0x0000])
        self.cd.add_char([0x0011, 0x0012])
        self.cd.add_char([0x0013])

        # Full output
        expected_output = {
            Char(0x0000),
            RangeChar(0x0001, 0x0001, 0x0005),
            RangeChar(0x0002, 0x0001, 0x0005),
            RangeChar(0x0003, 0x0001, 0x0005),
            RangeChar(0x0004, 0x0001, 0x0005),
            RangeChar(0x0005, 0x0001, 0x0005),
            Char(0x0010),
            CharSequence([0x0011, 0x0012]),
            Char(0x0013),
        }
        self.assertEqual(set(self.cd.all_repertoire()), expected_output)

        # Exclude ranges
        expected_output = {
            Char(0x0000),
            Char(0x0010),
            CharSequence([0x0011, 0x0012]),
            Char(0x0013),
        }
        self.assertEqual(set(self.cd.all_repertoire(include_ranges=False)),
                         expected_output)

        # Exclude sequences
        expected_output = {
            Char(0x0000),
            RangeChar(0x0001, 0x0001, 0x0005),
            RangeChar(0x0002, 0x0001, 0x0005),
            RangeChar(0x0003, 0x0001, 0x0005),
            RangeChar(0x0004, 0x0001, 0x0005),
            RangeChar(0x0005, 0x0001, 0x0005),
            Char(0x0010),
            Char(0x0013),
        }
        self.assertEqual(set(self.cd.all_repertoire(include_sequences=False)),
                         expected_output)

        # Exclude ranges and sequences
        expected_output = {
            Char(0x0000),
            Char(0x0010),
            Char(0x0013),
        }
        self.assertEqual(set(self.cd.all_repertoire(include_ranges=False,
                                                     include_sequences=False)),
                         expected_output)

    def test_get_variants(self):
        self.cd.add_char([0x002A])
        self.cd.add_variant([0x002A], [0x0030])
        self.cd.add_variant([0x002A], [0x0030], when='w1')
        self.cd.add_variant([0x002A], [0x0030], not_when='w1')
        self.cd.add_variant([0x002A], [0x0030], when='w1', not_when='nw-1')

        variants = self.cd.get_variants([0x002A])

        self.assertIsInstance(variants, types.GeneratorType)

        variant_list = list(variants)
        self.assertEqual(len(variant_list), 4)

        expected_output = [
            Variant((0x0030,)),
            Variant((0x0030, ), when='w1'),
            Variant((0x0030, ), not_when='w1'),
            Variant((0x0030, ), when='w1', not_when='nw-1')
        ]

        self.assertEqual(variant_list, expected_output)

    def test_del_reference(self):
        self.cd.add_char([0x002A], ref=['1', '2'])
        self.cd.add_char([0x002B], ref=['2', '3'])
        self.cd.add_char([0x002C], ref=['3', '4'])
        self.cd.del_reference('2')

        self.assertEqual(self.cd.get_char([0x002A]).references, ['1'])
        self.assertEqual(self.cd.get_char([0x002B]).references, ['3'])
        self.assertEqual(self.cd.get_char([0x002C]).references, ['3', '4'])

    def test_del_reference_variant(self):
        self.cd.add_char([0x002A], ref=['1', '2'])
        self.cd.add_variant([0x002A], [0x0030], ref=['2', '3'])
        self.cd.del_reference('2')

        self.assertEqual(self.cd.get_char([0x002A]).references, ['1'])
        self.assertEqual(list(self.cd.get_variants([0x002A]))[0].references, ['3'])

    def test_get_chars_from_prefix(self):
        c1 = self.cd.add_char([0x002A])
        c2 = self.cd.add_char([0x002A, 0x002B])
        c3 = self.cd.add_char([0x002A, 0x002B, 0x002C])
        c4 = self.cd.add_char([0x002A, 0x002B, 0x002C, 0x002D])

        char_list = self.cd.get_chars_from_prefix(0x002A)
        self.assertEqual(len(char_list), 4)
        self.assertListEqual(char_list,
                             [c4, c3, c2, c1])

    def test_get_variant_sets(self):
        self.cd.add_char([0x002A])
        self.cd.add_char([0x002B])
        self.cd.add_char([0x002C])
        self.cd.add_char([0x002D])
        self.cd.add_char([0x002E])
        self.cd.add_char([0x002F])

        # Set 1 {2A, 2C, 2F}
        self.cd.add_variant([0x002A], [0x002C])
        self.cd.add_variant([0x002A], [0x002F])
        self.cd.add_variant([0x002C], [0x002A])
        self.cd.add_variant([0x002C], [0x002F])
        self.cd.add_variant([0x002F], [0x002A])
        self.cd.add_variant([0x002F], [0x002C])

        # Set 2 {2B, 2E}
        self.cd.add_variant([0x002B], [0x002E])
        self.cd.add_variant([0x002E], [0x002B])

        variant_sets = frozenset(self.cd.get_variant_sets())
        self.assertEqual(len(variant_sets), 2)

        self.assertSetEqual(variant_sets,
                            {((0x002A,), (0x002C,), (0x002F,)),
                             ((0x002B,), (0x002E,))})


if __name__ == '__main__':
    import logging
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
