# -*- coding: utf-8 -*-
"""
test_lgr_core.py - Unit testing of LGR code module.
"""
from __future__ import unicode_literals

import types
import unittest

from lgr.char import Char, RangeChar
from lgr.classes import TAG_CLASSNAME_PREFIX
from lgr.core import LGR
from lgr.exceptions import (CharAlreadyExists,
                            VariantAlreadyExists,
                            CharInvalidIdnaProperty,
                            CharInvalidContextRule,
                            VariantInvalidContextRule,
                            RangeInvalidContextRule,
                            NotInRepertoire,
                            NotInLGR,
                            DuplicateReference,
                            LGRFormatException)
from lgr.matcher import LookBehindMatcher, AnchorMatcher, CharMatcher, LookAheadMatcher
from lgr.rule import Rule
from lgr.test_utils.unicode_database_mock import UnicodeDatabaseMock


class TestLGRCore(unittest.TestCase):

    def setUp(self):
        unidb = UnicodeDatabaseMock()
        self.lgr = LGR(unicode_database=unidb)

    def test_add_single_cp_list(self):
        self.lgr.add_cp([0x0061])
        self.assertIn(0x0061, self.lgr.repertoire)

    def test_add_single_cp_int(self):
        self.lgr.add_cp(0x0061)
        self.assertIn(0x0061, self.lgr.repertoire)

    def test_add_cp_sequence(self):
        self.lgr.add_cp([0x0061, 0x0062])
        self.assertIn([0x0061, 0x0062], self.lgr.repertoire)
        self.assertNotIn(0x0061, self.lgr.repertoire)
        self.assertNotIn(0x0062, self.lgr.repertoire)

    def test_add_multiple_cp_sequences(self):
        self.lgr.add_cp([0x0061, 0x0062])
        self.lgr.add_cp([0x0061, 0x0062, 0x0063])
        self.assertIn([0x0061, 0x0062], self.lgr.repertoire)
        self.assertIn([0x0061, 0x0062, 0x0063], self.lgr.repertoire)
        self.assertNotIn(0x0061, self.lgr.repertoire)
        self.assertNotIn(0x0062, self.lgr.repertoire)
        self.assertNotIn(0x0063, self.lgr.repertoire)

    def test_add_cp_in_repertoire(self):
        self.lgr.add_cp([0x0061])
        self.assertRaises(CharAlreadyExists, self.lgr.add_cp, [0x0061])
        self.assertRaises(CharAlreadyExists, self.lgr.add_cp, 0x0061)

    def test_add_cp_validation(self):
        validation_lgr = LGR()
        validation_lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0061], validating_repertoire=validation_lgr,
                        override_repertoire=False)
        self.assertRaises(NotInRepertoire, self.lgr.add_cp, [0x0062],
                          validating_repertoire=validation_lgr,
                          override_repertoire=False)

    def test_add_cp_validation_override(self):
        validation_lgr = LGR()
        validation_lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0061], validating_repertoire=validation_lgr,
                        override_repertoire=False)
        self.lgr.add_cp([0x0062],
                        validating_repertoire=validation_lgr,
                        override_repertoire=True)
        self.assertIn(0x0062, self.lgr.repertoire)

    def test_del_single_cp_list(self):
        self.lgr.add_cp(0x0061)
        self.lgr.del_cp([0x0061])
        self.assertNotIn(0x0061, self.lgr.repertoire)

    def test_del_single_cp_int(self):
        self.lgr.add_cp([0x0061])
        self.lgr.del_cp(0x0061)
        self.assertNotIn(0x0061, self.lgr.repertoire)

    def test_del_cp_sequence(self):
        self.lgr.add_cp([0x0061, 0x0062])
        self.lgr.del_cp([0x0061, 0x0062])
        self.assertEqual(len(self.lgr.repertoire), 0)

    def test_del_cp_sequence_with_cp(self):
        self.lgr.add_cp([0x0061, 0x0062])
        self.assertRaises(NotInLGR, self.lgr.del_cp, 0x0061)
        self.assertRaises(NotInLGR, self.lgr.del_cp, 0x0062)
        self.assertIn([0x0061, 0x0062], self.lgr.repertoire)

    def test_add_cp_when_not_when(self):
        self.lgr.add_cp([0x0061], when='w1')
        with self.assertRaises(CharInvalidContextRule) as cm:
            self.lgr.add_cp([0x0062], when='w2', not_when='nw1')
        the_exception = cm.exception
        self.assertEqual(the_exception.cp,
                         [0x0062])

        self.lgr.add_cp([0x0062], not_when='nw2')
        with self.assertRaises(CharInvalidContextRule) as cm:
            self.lgr.add_cp([0x0063], when='w3', not_when='nw3')
        the_exception = cm.exception
        self.assertEqual(the_exception.cp,
                         [0x0063])

    def test_add_range(self):
        self.lgr.add_range(0x0061, 0x007A)
        for cp in range(0x0061, 0x007A + 1):
            self.assertIn(cp, self.lgr.repertoire)

    def test_add_range_in_repertoire(self):
        self.lgr.add_range(0x0061, 0x007A)
        self.assertRaises(CharAlreadyExists,
                          self.lgr.add_range, 0x0061, 0x007A)

    def test_add_range_validation(self):
        validation_lgr = LGR()
        for cp in range(0x0061, 0x007A + 1):
            validation_lgr.add_cp(cp)
        self.lgr.add_range(0x0061, 0x007A,
                           validating_repertoire=validation_lgr,
                           override_repertoire=False)
        self.assertRaises(NotInRepertoire, self.lgr.add_range, 0x00F8, 0x00FF,
                          validating_repertoire=validation_lgr,
                          override_repertoire=False)

    def test_add_range_validation_with_range(self):
        validation_lgr = LGR()
        validation_lgr.add_range(0x0061, 0x007A)
        self.lgr.add_range(0x0061, 0x007A,
                           validating_repertoire=validation_lgr,
                           override_repertoire=False)
        self.assertRaises(NotInRepertoire, self.lgr.add_range, 0x00F8, 0x00FF,
                          validating_repertoire=validation_lgr,
                          override_repertoire=False)

    def test_add_range_validation_override(self):
        validation_lgr = LGR()
        for cp in range(0x0061, 0x007A):
            validation_lgr.add_cp(cp)
        self.lgr.add_range(0x0031, 0x0032,
                           validating_repertoire=validation_lgr,
                           override_repertoire=True)
        self.assertIn(0x0031, self.lgr.repertoire)

    def test_add_range_when_not_when(self):
        self.lgr.add_range(0x0061, 0x0065, when='w1')
        with self.assertRaises(RangeInvalidContextRule) as cm:
            self.lgr.add_range(0x0066, 0x007A, when='w2', not_when='nw1')
        the_exception = cm.exception
        self.assertEqual(the_exception.first_cp,
                         0x0066)
        self.assertEqual(the_exception.last_cp,
                         0x007A)

        self.lgr.add_range(0x0066, 0x007A, not_when='nw2')
        with self.assertRaises(RangeInvalidContextRule) as cm:
            self.lgr.add_range(0x01BD, 0x01C3, when='w3', not_when='nw3')
        the_exception = cm.exception
        self.assertEqual(the_exception.first_cp,
                         0x01BD)
        self.assertEqual(the_exception.last_cp,
                         0x01C3)

    def test_expand_ranges(self):
        self.lgr.add_range(0x0061, 0x007A)
        for cp in range(0x0061, 0x007A + 1):
            self.assertIsInstance(self.lgr.get_char(cp), RangeChar)
        self.lgr.add_range(0x01BD, 0x01C3)
        for cp in range(0x01BD, 0x01C3 + 1):
            self.assertIsInstance(self.lgr.get_char(cp), RangeChar)

        self.lgr.expand_ranges()
        for cp in range(0x0061, 0x007A + 1):
            char = self.lgr.get_char(cp)
            self.assertIsInstance(char, Char)
            self.assertNotIsInstance(char, RangeChar)
        for cp in range(0x01BD, 0x01C3 + 1):
            char = self.lgr.get_char(cp)
            self.assertIsInstance(char, Char)
            self.assertNotIsInstance(char, RangeChar)

    def test_expand_range(self):
        self.lgr.add_range(0x0061, 0x007A)
        for cp in range(0x0061, 0x007A + 1):
            self.assertIsInstance(self.lgr.get_char(cp), RangeChar)

        self.lgr.expand_range(0x0061, 0x007A)
        for cp in range(0x0061, 0x007A + 1):
            char = self.lgr.get_char(cp)
            self.assertIsInstance(char, Char)
            self.assertNotIsInstance(char, RangeChar)

    def test_add_variant_in_repertoire(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0030])
        self.assertRaises(VariantAlreadyExists, self.lgr.add_variant, [0x0061],
                          [0x0030])

    def test_add_variant_validation(self):
        validation_lgr = LGR()
        validation_lgr.add_cp([0x0061])
        validation_lgr.add_cp([0x0030])

        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0030])

        self.assertRaises(NotInRepertoire, self.lgr.add_variant,
                          [0x0061], [0x0062],
                          validating_repertoire=validation_lgr,
                          override_repertoire=False)

    def test_add_variant_when_not_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0030], when='w1')
        with self.assertRaises(VariantInvalidContextRule) as cm:
            self.lgr.add_variant([0x0061], [0x0031], when='w2', not_when='nw1')
        the_exception = cm.exception
        self.assertEqual(the_exception.cp,
                         [0x0061])
        self.assertEqual(the_exception.variant,
                         [0x0031])

        self.lgr.add_variant([0x0061], [0x0030], not_when='nw2')
        with self.assertRaises(VariantInvalidContextRule) as cm:
            self.lgr.add_variant([0x0061], [0x0031], when='w3', not_when='nw3')
        the_exception = cm.exception
        self.assertEqual(the_exception.cp,
                         [0x0061])
        self.assertEqual(the_exception.variant,
                         [0x0031])

    def test_del_cp_validation_override(self):
        validation_lgr = LGR()
        validation_lgr.add_cp([0x0061])
        validation_lgr.add_cp([0x0030])

        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0030])

        self.lgr.add_variant([0x0061], [0x0062],
                             validating_repertoire=validation_lgr,
                             override_repertoire=True)
        self.assertIn((0x0062,), self.lgr.repertoire[0x0061]._variants)

    def test_get_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0030])

        variants = self.lgr.get_variants([0x0061])
        self.assertIsInstance(variants, types.GeneratorType)

        variant_list = list(variants)

        self.assertEqual(len(variant_list), 1)

    def test_check_range_no_modification(self):
        self.lgr.check_range(0x0060, 0x007F)

        self.assertEqual(len(self.lgr.repertoire), 0)

    def test_check_range(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x007A])

        codepoints = self.lgr.check_range(0x0060, 0x007F)

        for result in codepoints:
            cp = result[0]
            prop = result[1]
            if cp == 0x060 or cp >= 0x007B:
                self.assertIsInstance(prop, CharInvalidIdnaProperty)
            elif cp == 0x0061 or cp == 0x007A:
                self.assertIsInstance(prop, CharAlreadyExists)
            else:
                self.assertIsNone(prop)

    def test_add_codepoints(self):
        self.lgr.add_codepoints([c for c in range(0x0061, 0x007A + 1)] +
                                [0x0107] +
                                [0x0137, 0x0138])

        expected_output = [RangeChar(0x061, 0x0061, 0x007A),
                           Char(0x0107),
                           RangeChar(0x0137, 0x0137, 0x0138)]

        self.assertEqual(expected_output, list(self.lgr.repertoire))

    def test_tags_on_codepoint(self):
        self.lgr.add_cp([0x0061], tag=['t1', 't2'])
        with self.assertRaises(LGRFormatException) as cm:
            self.lgr.add_cp([0x0062], tag=['t1', 't1'])

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.DUPLICATE_TAG)

    def test_tags_on_codepoint_sequence(self):
        with self.assertRaises(LGRFormatException) as cm:
            self.lgr.add_cp([0x0061, 0x0062], tag=['t1'])

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.SEQUENCE_NO_TAG)

    def test_tags_on_range(self):
        self.lgr.add_range(0x0061, 0x0062, tag=['t1', 't2'])
        with self.assertRaises(LGRFormatException) as cm:
            self.lgr.add_range(0x0063, 0x0064, tag=['t1', 't1'])

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.DUPLICATE_TAG)

    def test_del_tag(self):
        self.lgr.add_cp([0x0061], tag=['1'])
        self.lgr.add_cp([0x0062], tag=['1', '2'])

        self.lgr.del_tag('1')

        self.assertNotIn(TAG_CLASSNAME_PREFIX + '1', self.lgr.classes_lookup)
        self.assertEqual(self.lgr.get_char([0x0061]).tags, [])
        self.assertEqual(self.lgr.get_char([0x0062]).tags, ['2'])

    def test_list_types(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0030], variant_type='BLOCK')
        self.lgr.add_variant([0x0061], [0x0031], variant_type='VALID')
        self.lgr.add_variant([0x0061], [0x0032], variant_type='BLOCK')

        self.assertEqual(self.lgr.types, set(['BLOCK', 'VALID']))

    def test_del_reference(self):
        ref_id_1 = self.lgr.add_reference("Test - 1")
        ref_id_2 = self.lgr.add_reference("Test - 2")

        self.lgr.add_cp([0x0061], ref=[ref_id_1])
        self.lgr.add_cp([0x0062], ref=[ref_id_1, ref_id_2])

        self.lgr.del_reference(ref_id_1)

        self.assertNotIn(ref_id_1, self.lgr.reference_manager)
        self.assertEqual(self.lgr.get_char([0x0061]).references, [])
        self.assertEqual(self.lgr.get_char([0x0062]).references, [ref_id_2])

    def test_add_cp_duplicate_reference(self):
        ref_id = self.lgr.add_reference("Test - 1")
        with self.assertRaises(DuplicateReference) as cm:
            self.lgr.add_cp([0x0061], ref=[ref_id, ref_id])

        the_exception = cm.exception
        self.assertEqual(the_exception.cp, [0x0061])

    def test_add_range_duplicate_reference(self):
        ref_id = self.lgr.add_reference("Test - 1")
        with self.assertRaises(DuplicateReference) as cm:
            self.lgr.add_range(0x0061, 0x0062, ref=[ref_id, ref_id])

        the_exception = cm.exception
        self.assertEqual(the_exception.cp, 0x0061)

    def test_add_variant_duplicate_reference(self):
        self.lgr.add_cp([0x0061])
        ref_id = self.lgr.add_reference("Test - 1")
        with self.assertRaises(DuplicateReference) as cm:
            self.lgr.add_variant([0x0061], [0x0062], ref=[ref_id, ref_id])

        the_exception = cm.exception
        self.assertEqual(the_exception.cp, [0x0061])

    def test_generate_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])

        a = self.lgr.get_char([0x0061])
        b = self.lgr.get_char([0x0062])
        c = self.lgr.get_char([0x0063])

        self.lgr.add_variant([0x0061], [0x0070], variant_type="type0")
        self.lgr.add_variant([0x0062], [0x0071], variant_type="type1")
        self.lgr.add_variant([0x0062], [0x0072], variant_type="type2")

        p = a.get_variant((0x0070,))[0]
        q = b.get_variant((0x0071,))[0]
        r = b.get_variant((0x0072,))[0]

        self.assertEqual([], list(self.lgr._generate_label_variants([])))
        self.assertEqual([],
                         list(self.lgr._generate_label_variants([0x0063])))
        self.assertEqual([],
                         list(self.lgr._generate_label_variants([0x0063, 0x0064])))
        self.assertCountEqual([
            ((0x0071, 0x0063), frozenset(['type1']), False, [q, c]),
            ((0x0072, 0x0063), frozenset(['type2']), False, [r, c])
        ], self.lgr._generate_label_variants([0x0062, 0x0063]))
        self.assertCountEqual([
            ((0x0061, 0x0062), frozenset(), False, [a, b]),
            ((0x0061, 0x0071), frozenset(['type1']), False, [a, q]),
            ((0x0061, 0x0072), frozenset(['type2']), False, [a, r]),
            ((0x0070, 0x0062), frozenset(['type0']), False, [p, b]),
            ((0x0070, 0x0071), frozenset(['type0', 'type1']), True, [p, q]),
            ((0x0070, 0x0072), frozenset(['type0', 'type2']), True, [p, r]),
        ], self.lgr._generate_label_variants([0x0061, 0x0062]))
        self.assertCountEqual([
            ((0x0061, 0x0062, 0x0062), frozenset(), False, [a, b, b]),
            ((0x0061, 0x0062, 0x0071), frozenset(['type1']), False, [a, b, q]),
            ((0x0061, 0x0062, 0x0072), frozenset(['type2']), False, [a, b, r]),
            ((0x0061, 0x0071, 0x0062), frozenset(['type1']), False, [a, q, b]),
            ((0x0061, 0x0071, 0x0071), frozenset(['type1']), False, [a, q, q]),
            ((0x0061, 0x0071, 0x0072), frozenset(['type1', 'type2']), False, [a, q, r]),
            ((0x0061, 0x0072, 0x0062), frozenset(['type2']), False, [a, r, b]),
            ((0x0061, 0x0072, 0x0071), frozenset(['type1', 'type2']), False, [a, r, q]),
            ((0x0061, 0x0072, 0x0072), frozenset(['type2']), False, [a, r, r]),
            ((0x0070, 0x0062, 0x0062), frozenset(['type0']), False, [p, b, b]),
            ((0x0070, 0x0062, 0x0071), frozenset(['type0', 'type1']), False, [p, b, q]),
            ((0x0070, 0x0062, 0x0072), frozenset(['type0', 'type2']), False, [p, b, r]),
            ((0x0070, 0x0071, 0x0062), frozenset(['type0', 'type1']), False, [p, q, b]),
            ((0x0070, 0x0071, 0x0071), frozenset(['type0', 'type1']), True, [p, q, q]),
            ((0x0070, 0x0071, 0x0072), frozenset(['type0', 'type1', 'type2']), True, [p, q, r]),
            ((0x0070, 0x0072, 0x0062), frozenset(['type0', 'type2']), False, [p, r, b]),
            ((0x0070, 0x0072, 0x0071), frozenset(['type0', 'type1', 'type2']), True, [p, r, q]),
            ((0x0070, 0x0072, 0x0072), frozenset(['type0', 'type2']), True, [p, r, r]),
        ], self.lgr._generate_label_variants([0x0061, 0x0062, 0x0062]))

    def test_generate_variants_reflexive(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])

        a = self.lgr.get_char([0x0061])
        b = self.lgr.get_char([0x0062])
        c = self.lgr.get_char([0x0063])

        self.lgr.add_variant([0x0062], [0x0062], variant_type="reflexive")
        self.lgr.add_variant([0x0063], [0x0070], variant_type="type")

        p = c.get_variant((0x0070,))[0]

        self.assertCountEqual([], list(self.lgr._generate_label_variants([])))
        self.assertCountEqual([],
                              list(self.lgr._generate_label_variants([0x0061])))
        self.assertCountEqual([((0x0062,), frozenset(['reflexive']), True, [b])],
                              list(self.lgr._generate_label_variants([0x0062])))
        self.assertCountEqual([
            ((0x0062, 0x0063), frozenset(['reflexive']), False, [b, c]),
            ((0x0062, 0x0070), frozenset(['reflexive', 'type']), True, [b, p]),
        ], self.lgr._generate_label_variants([0x0062, 0x0063]))

    def test_generate_variants_sequence_same_cp(self):
        self.lgr.add_cp([0x05D9, 0x05D9])
        self.lgr.add_cp([0X05F2])
        self.lgr.add_cp([0x05D9])

        yod = self.lgr.get_char([0x05D9])
        yodseq = self.lgr.get_char([0x05D9, 0x05D9])

        self.lgr.add_variant([0x05D9, 0x05D9], [0x05F2])
        self.lgr.add_variant([0x05F2], [0x05D9, 0x05D9])

        dyod_var = yodseq.get_variant((0x05F2,))[0]

        self.assertCountEqual([
            ((0x05F2, 0x05D9), frozenset(), False, [dyod_var, yod]),
            ((0x05D9, 0x05D9, 0x05D9), frozenset(), False, [yod, yodseq]),
            ((0x05D9, 0x05F2), frozenset(), False, [yod, dyod_var])
        ], self.lgr._generate_label_variants([0x05D9, 0x05D9, 0x05D9]))

    def test_label_simple(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062, 0x0063])
        self.lgr.add_range(0x0064, 0x0068)

        valid_labels = (
            [0x0061],
            [0x0062, 0x0063],
            [0x0064],
            [0x0068],
            [0x0061, 0x0064],
            [0x0061, 0x0062, 0x0063, 0x0064],
            [0x0062, 0x0063, 0x0068]
        )
        invalid_labels = (
            ([0x0060], [], [(0x0060, None)]),
            ([0x0069], [], [(0x0069, None)]),
            ([0x0062], [], [(0x0062, None)]),
            ([0x0063], [], [(0x0063, None)]),
            ([0x0061, 0x0062], [0x0061], [(0x0062, None)])
        )

        for label in valid_labels:
            self.assertEqual((True, label, []),
                             self.lgr._test_preliminary_eligibility(label))
        for (label, label_part, not_in_lgr) in invalid_labels:
            self.assertEqual((False, label_part, not_in_lgr),
                             self.lgr._test_preliminary_eligibility(label))

    def test_label_eligibility_multiple_choices(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0061, 0x0062, 0x0063])
        self.lgr.add_cp([0x0064])

        self.assertEqual(self.lgr._test_preliminary_eligibility([0x0062]),
                         (False, [], [(0x0062, None)]))
        self.assertEqual(self.lgr._test_preliminary_eligibility([0x0061, 0x0062, 0x0063, 0x0064]),
                         (True, [0x0061, 0x0062, 0x0063, 0x0064], []))

    def test_label_delayed_eligibilty(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0061], 'block')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0062], 'invalid')
        self.lgr.add_cp([0x0063, 0x0064])
        self.lgr.add_variant([0x0063, 0x0064], [0x0063, 0x0064], 'invalid')

        self.assertEqual(self.lgr._test_label_disposition([0x0062]),
                         ('invalid', 0))
        self.assertEqual(self.lgr._test_label_disposition([0x0063, 0x0064]),
                         ('invalid', 0))
        self.assertEqual(self.lgr._test_label_disposition([0x0061, 0x0062]),
                         ('invalid', 0))

    def test_estimate_variant_numbers(self):
        self.lgr.add_cp([0x0061])

        self.assertEqual(1, self.lgr.estimate_variant_number([0x0061]))

        self.lgr.add_variant([0x0061], [0x0061], 'disp')
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0062], 'disp')

        # ignore reflexive variant
        self.assertEqual(1, self.lgr.estimate_variant_number([0x0061]))
        self.assertEqual(1, self.lgr.estimate_variant_number([0x0062]))
        self.assertEqual(1 * 1, self.lgr.estimate_variant_number([0x0061, 0x0062]))

        self.lgr.add_variant([0x0061], [0x0062], 'disp')
        self.lgr.add_variant([0x0062], [0x0061], 'disp')
        self.assertEqual(2, self.lgr.estimate_variant_number([0x0061]))
        self.assertEqual(2, self.lgr.estimate_variant_number([0x0062]))
        self.assertEqual(2 * 2, self.lgr.estimate_variant_number([0x0061, 0x0062]))

        self.lgr.add_cp([0x0063])
        for i in range(10):
            self.lgr.add_variant([0x0063], [0x074D + i], 'disp')

        self.assertEqual(11, self.lgr.estimate_variant_number([0x0063]))
        self.assertEqual(2 * 2 * 11, self.lgr.estimate_variant_number([0x0061, 0x0062, 0x0063]))

        self.assertEqual(2 * 2 * 1, self.lgr.estimate_variant_number([0x0061, 0x0062, 0x0063],
                                                                     hide_mixed_script_variants=True))
        # check that other script variants are also taken into account
        self.lgr.add_cp([0x0064])
        self.lgr.add_variant([0x0064], [0x3078], 'disp')
        self.lgr.add_cp([0x3078])
        self.lgr.add_variant([0x3078], [0x0064], 'disp')
        self.lgr.add_cp([0x0065])
        self.lgr.add_variant([0x0065], [0x3079], 'disp')
        self.lgr.add_cp([0x3079])
        self.lgr.add_variant([0x3079], [0x0065], 'disp')
        # 0x0063 has not Japanese variant, so only all Latin variants can be generated
        self.assertEqual(1, self.lgr.estimate_variant_number([0x0064, 0x0065, 0x0063], hide_mixed_script_variants=True))
        # there is an all Japanese variant as well as the all Latin variant
        self.assertEqual(2, self.lgr.estimate_variant_number([0x0064, 0x0065], hide_mixed_script_variants=True))

    def test_generate_variants_mixed_scripts(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([ord('á')])
        self.lgr.add_cp([ord('ά')])
        self.lgr.add_cp([ord('α')])

        b = self.lgr.get_char([0x0062])
        aacute = self.lgr.get_char([ord('á')])
        alphagrave = self.lgr.get_char([ord('ά')])
        alpha = self.lgr.get_char([ord('α')])

        self.lgr.add_variant([0x0061], [ord('á')], variant_type="disp")
        self.lgr.add_variant([0x0061], [ord('ά')], variant_type="disp")
        self.lgr.add_variant([0x0061], [ord('α')], variant_type="disp")

        self.assertCountEqual([
            ((ord('á'), 0x0062), frozenset(['disp']), False, [aacute, b]),
            ((ord('ά'), 0x0062), frozenset(['disp']), False, [alphagrave, b]),
            ((ord('α'), 0x0062), frozenset(['disp']), False, [alpha, b])
        ], self.lgr._generate_label_variants([0x0061, 0x0062]))
        self.assertCountEqual([((ord('á'), 0x0062), frozenset(['disp']), False, [aacute, b])],
                              self.lgr._generate_label_variants([0x0061, 0x0062], hide_mixed_script_variants=True))

    def test_generate_label_partitions(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])
        self.lgr.add_cp([0x0061, 0x0062])
        self.lgr.add_cp([0x0062, 0x0063])
        self.lgr.add_cp([0x0063, 0x0064])

        a = self.lgr.get_char([0x0061])
        b = self.lgr.get_char([0x0062])
        c = self.lgr.get_char([0x0063])
        d = self.lgr.get_char([0x0064])
        ab = self.lgr.get_char([0x0061, 0x0062])
        bc = self.lgr.get_char([0x0062, 0x0063])
        cd = self.lgr.get_char([0x0063, 0x0064])

        self.assertCountEqual([
            [a, b, c, d],
            [a, b, cd],
            [a, bc, d],
            [ab, c, d],
            [ab, cd],
        ], self.lgr._generate_label_partitions([0x0061, 0x0062, 0x0063, 0x0064]))

    def test_generate_label_partitions_with_code_point_context_rule(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])
        self.lgr.add_cp([0x0061, 0x0062])
        self.lgr.add_cp([0x0062, 0x0063], not_when='after-a')
        self.lgr.add_cp([0x0063, 0x0064])

        a = self.lgr.get_char([0x0061])
        b = self.lgr.get_char([0x0062])
        c = self.lgr.get_char([0x0063])
        d = self.lgr.get_char([0x0064])
        ab = self.lgr.get_char([0x0061, 0x0062])
        cd = self.lgr.get_char([0x0063, 0x0064])

        rule = Rule(name='after-a')
        look = LookBehindMatcher()
        look.add_child(CharMatcher((0x0061,)))
        rule.add_child(look)
        rule.add_child(AnchorMatcher())
        self.lgr.add_rule(rule)

        self.assertCountEqual([
            [a, b, c, d],
            [a, b, cd],
            [ab, c, d],
            [ab, cd],
        ], self.lgr._generate_label_partitions([0x0061, 0x0062, 0x0063, 0x0064]))

    def test_generate_index_label_on_partition(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])
        self.lgr.add_cp([0x0065])
        self.lgr.add_cp([0x0066])
        self.lgr.add_cp([0x0067])
        self.lgr.add_cp([0x0068])
        self.lgr.add_cp([0x0062, 0x0063])
        self.lgr.add_cp([0x0064, 0x0065])

        a = self.lgr.get_char([0x0061])
        b = self.lgr.get_char([0x0062])
        c = self.lgr.get_char([0x0063])
        d = self.lgr.get_char([0x0064])
        e = self.lgr.get_char([0x0065])
        f = self.lgr.get_char([0x0066])
        bc = self.lgr.get_char([0x0062, 0x0063])
        de = self.lgr.get_char([0x0064, 0x0065])

        self.lgr.add_variant([0x0062, 0x0063], [0x0066])
        self.lgr.add_variant([0x0066], [0x0062, 0x0063])
        self.lgr.add_variant([0x0064, 0x0065], [0x0061])
        self.lgr.add_variant([0x0061], [0x0064, 0x0065])
        self.lgr.add_variant([0x0062], [0x0064])
        self.lgr.add_variant([0x0064], [0x0062])

        self.assertEqual((0x0061, 0x0062, 0x0063, 0x0062, 0x0065, 0x0062, 0x0063),
                         self.lgr._generate_index_label_on_partition([a, b, c, d, e, f]))
        self.assertEqual((0x0061, 0x0062, 0x0063, 0x0061, 0x0062, 0x0063),
                         self.lgr._generate_index_label_on_partition([a, bc, de, f]))
        self.assertEqual((0x0061, 0x0062, 0x0063, 0x0061, 0x0062, 0x0063),
                         self.lgr._generate_index_label_on_partition([a, b, c, de, f]))

    def test_generate_index_label_on_partition_with_variant_context_rule(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])
        self.lgr.add_cp([0x0065])
        self.lgr.add_cp([0x0066])
        self.lgr.add_cp([0x0067])
        self.lgr.add_cp([0x0068])
        self.lgr.add_cp([0x0062, 0x0063])
        self.lgr.add_cp([0x0064, 0x0065])

        a = self.lgr.get_char([0x0061])
        f = self.lgr.get_char([0x0066])
        bc = self.lgr.get_char([0x0062, 0x0063])
        de = self.lgr.get_char([0x0064, 0x0065])

        self.lgr.add_variant([0x0062, 0x0063], [0x0066])
        self.lgr.add_variant([0x0066], [0x0062, 0x0063])
        self.lgr.add_variant([0x0064, 0x0065], [0x0061], not_when='after-c')
        self.lgr.add_variant([0x0061], [0x0064, 0x0065])
        self.lgr.add_variant([0x0062], [0x0064])
        self.lgr.add_variant([0x0064], [0x0062])

        rule = Rule(name='after-c')
        look = LookBehindMatcher()
        look.add_child(CharMatcher((0x0063,)))
        rule.add_child(look)
        rule.add_child(AnchorMatcher())
        self.lgr.add_rule(rule)

        self.assertEqual((0x0061, 0x0062, 0x0063, 0x0064, 0x0065, 0x0062, 0x0063),
                         self.lgr._generate_index_label_on_partition([a, bc, de, f]))

        self.lgr.del_variant([0x0064, 0x0065], [0x0061])
        self.lgr.add_variant([0x0064, 0x0065], [0x0061], when='after-c')

        self.assertEqual((0x0061, 0x0062, 0x0063, 0x0061, 0x0062, 0x0063),
                         self.lgr._generate_index_label_on_partition([a, bc, de, f]))

    def test_generate_index_label(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])
        self.lgr.add_cp([0x0065])
        self.lgr.add_cp([0x0066])
        self.lgr.add_cp([0x0067])
        self.lgr.add_cp([0x0068])
        self.lgr.add_cp([0x0062, 0x0063])
        self.lgr.add_cp([0x0064, 0x0065])

        self.lgr.add_variant([0x0062, 0x0063], [0x0066])
        self.lgr.add_variant([0x0066], [0x0062, 0x0063])
        self.lgr.add_variant([0x0064, 0x0065], [0x0061])
        self.lgr.add_variant([0x0061], [0x0064, 0x0065])

        self.assertEqual((0x0061, 0x0062, 0x0063, 0x0061, 0x0062, 0x0063),
                         self.lgr.generate_index_label([0x0061, 0x0062, 0x0063, 0x0064, 0x0065, 0x0066]))

    def test_generate_index_label_effective_null_variant(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        self.lgr.add_cp([0x0063])
        self.lgr.add_cp([0x0064])
        self.lgr.add_cp([0x0062, 0x0063])

        self.lgr.add_variant([0x0062, 0x0063], [0x0062])
        self.lgr.add_variant([0x0062], [0x0062, 0x0063])

        # partitions are {a}{b}{c} and {a}{b,c}, with possible indexes {a}{b}{c} and {a}{b}
        self.assertEqual((0x0061, 0x0062),
                         self.lgr.generate_index_label([0x0061, 0x0062, 0x0063]))
        # partitions are {b}{c}{d} and {b,c}{d}, with possible indexes {b}{c}{d} and {b}{d}, however,
        # {b}{c}{d} is lower in code point order
        self.assertEqual((0x0062, 0x0063, 0x0064),
                         self.lgr.generate_index_label([0x0062, 0x0063, 0x0064]))
        # partitions are {b}{c}{d} and {b,c}{d}, with possible indexes {b}{c}{a} and {b}{a}
        self.assertEqual((0x0062, 0x0061),
                         self.lgr.generate_index_label([0x0062, 0x0063, 0x0061]))

    def test_generate_index_label_overlap(self):
        self.lgr.add_cp([0x0062])  # a
        self.lgr.add_cp([0x0062, 0x006C])  # bl
        self.lgr.add_cp([0x0065])  # e
        self.lgr.add_cp([0x0069])  # i
        self.lgr.add_cp([0x006C])  # l
        self.lgr.add_cp([0x0075])  # u
        self.lgr.add_cp([0x0435])  # е (Cyrillic)
        self.lgr.add_cp([0x044B])  # ы (Cyrillic)
        self.lgr.add_cp([0x045F])  # џ (Cyrillic)

        self.lgr.add_variant([0x0062, 0x006C], [0x044B])
        self.lgr.add_variant([0x044B], [0x0062, 0x006C])
        self.lgr.add_variant([0x0065], [0x0435])
        self.lgr.add_variant([0x0435], [0x0065])
        self.lgr.add_variant([0x0069], [0x006C])
        self.lgr.add_variant([0x006C], [0x0069])
        self.lgr.add_variant([0x0075], [0x045F])
        self.lgr.add_variant([0x045F], [0x0075])

        # if not context rule is provided, those 2 variant labels (blue and ыџе) end up with different indexes
        self.assertEqual((0x062, 0x0069, 0x0075, 0x0065),
                         self.lgr.generate_index_label([0x062, 0x006C, 0x0075, 0x0065]))
        self.assertEqual((0x062, 0x006C, 0x0075, 0x0065),
                         self.lgr.generate_index_label([0x044B, 0x045F, 0x0435]))

        # adding a rule to make it right
        self.lgr.del_variant([0x006C], [0x0069])
        self.lgr.add_variant([0x006C], [0x0069], not_when='preceded-by-0062')
        rule = Rule(name='preceded-by-0062')
        look = LookBehindMatcher()
        look.add_child(CharMatcher((0x0062,)))
        rule.add_child(look)
        rule.add_child(AnchorMatcher())
        self.lgr.add_rule(rule)

        self.assertEqual((0x062, 0x006C, 0x0075, 0x0065),
                         self.lgr.generate_index_label([0x062, 0x006C, 0x0075, 0x0065]))
        self.assertEqual((0x062, 0x006C, 0x0075, 0x0065),
                         self.lgr.generate_index_label([0x044B, 0x045F, 0x0435]))





if __name__ == '__main__':
    import logging

    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
