# -*- coding: utf-8 -*-
"""
test_harmonize.py - Unit testing of LGR harmonization module.
"""
from __future__ import unicode_literals

import unittest
import logging

from lgr.tools.harmonize import harmonize
from tests.unit.utils import load_lgr


class TestHarmonize(unittest.TestCase):

    def test_case_1(self):
        hindi = load_lgr('harmonization', 'hindi.xml')
        nepali = load_lgr('harmonization', 'nepali.xml')

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
        hindi = load_lgr('harmonization', 'hindi-rz.xml')
        nepali = load_lgr('harmonization', 'nepali-rz.xml')
        rz = load_lgr('harmonization', 'rz-lgr.xml')

        hindi_harmonized, nepali_harmonized, log = harmonize(hindi, nepali, rz)

        self.assertEqual(len(hindi.repertoire) + 1, len(hindi_harmonized.repertoire))
        self.assertEqual(len(nepali.repertoire) + 1, len(nepali_harmonized.repertoire))

        for lgr, cp, var_cp in ((hindi_harmonized, 0x0066, 0x0065), (nepali_harmonized, 0x0065, 0x0066)):
            char = lgr.get_char(cp)
            self.assertEqual(char.comment, 'Out-of-repertoire')
            variants = list(char.get_variants())
            self.assertEqual(len(variants), 2)
            variant_set = {(var.cp, var.type) for var in variants}
            self.assertSetEqual(variant_set, {
                ((var_cp, ), 'blocked'),
                ((cp, ), 'out-of-repertoire')  # Identity mapping for out-of-repertoire code points
            })

            var_char = lgr.get_char(var_cp)
            variants = list(var_char.get_variants())
            self.assertEqual(len(variants), 1)
            self.assertEqual(variants[0].cp, (cp, ))
            self.assertEqual(variants[0].type, 'blocked')

    def test_case_3(self):
        hindi = load_lgr('harmonization', 'hindi-log.xml')
        nepali = load_lgr('harmonization', 'nepali-log.xml')
        rz = load_lgr('harmonization', 'rz-lgr.xml')

        hindi_harmonized, nepali_harmonized, (log_hindi, log_nepali) = harmonize(hindi, nepali, rz)

        self.assertEqual(len(hindi.repertoire), len(hindi_harmonized.repertoire))
        self.assertEqual(len(nepali.repertoire), len(nepali_harmonized.repertoire))

        self.assertEqual(log_hindi, {(0x0079, )})
        self.assertEqual(log_nepali, {(0x007A, )})

    def test_lgr_with_range(self):
        a_z = load_lgr('harmonization', 'a-z-range.xml')
        a_b = load_lgr('harmonization', 'a-b.xml')

        a_z_harmonized, a_b_harmonized, _ = harmonize(a_z, a_b)

        for cp, var_cp in ((0x0061, 0x0062), (0x0062, 0x0061)):
            char = a_z_harmonized.get_char(cp)
            variants = list(char.get_variants())
            self.assertEqual(len(variants), 1)
            self.assertEqual(variants[0].cp, (var_cp, ))
            self.assertEqual(variants[0].type, 'blocked')

    def test_identity_mappings(self):
        a_c = load_lgr('harmonization', 'a-c.xml')
        c_e = load_lgr('harmonization', 'c-e.xml')

        a_c_harmonized, c_e_harmonized, _ = harmonize(a_c, c_e)

        all_cp = {(0x0061, ), (0x0062, ), (0x0063, ), (0x0064, ), (0x0065, )}
        for lgr, cp_list in ((a_c_harmonized, (0x0064, 0x0065)), (c_e_harmonized, (0x0061, 0x0062))):
            for cp in cp_list:
                char = lgr.get_char(cp)
                variants = {var.cp for var in char.get_variants()}
                self.assertSetEqual(variants, all_cp)
                # Ensure identity mapping is present
                id_mapping = char.get_variant((cp, ))
                self.assertEqual(len(id_mapping), 1)
                self.assertEqual(id_mapping[0].type, 'out-of-repertoire')

            for char in lgr.repertoire:
                if char.cp[0] in cp_list:  # Skip newly added code points
                    continue
                variants = {var.cp for var in char.get_variants()}
                # Ensure that already-present code points do not have identity mapping
                self.assertNotIn(char.cp, variants)
                # Ensure that already-present code points have new variants
                self.assertSetEqual(variants, all_cp - {char.cp})

        for lgr in (a_c_harmonized, c_e_harmonized):
            c_variants = [c.cp for c in lgr.get_variants(0x0063)]
            self.assertEqual(len(c_variants), 4)  # No identity mapping here
            self.assertNotIn((0x0063, ), c_variants)
            for cp in all_cp - {(0x0063, )}:
                self.assertIn(cp, c_variants)


if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
