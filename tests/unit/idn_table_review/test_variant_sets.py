#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
test_variant_sets - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.variant_sets import generate_variant_sets_report
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_variant_sets')


class Test(TestCase):
    ref = load_lgr('idn_table_review', 'reference_lgr.xml')

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def test_generate_variant_sets_report(self):
        idn = load_lgr('idn_table_review/variant_sets', 'variant_sets_exact_match.xml')

        result = generate_variant_sets_report(idn, self.ref)

        self.assertCountEqual(result, [{
            'set_number': (97,),
            'idn_table': ((97,), (98,), (99,)),
            'ref_lgr': ((97,), (98,), (99,)),
            'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
            'symmetry_check': True,
            'transitivity_check': True,
            'report': [
                {
                    'source_cp': 'U+0061',
                    'source_glyph': 'a',
                    'dest_cp': 'U+0062',
                    'dest_glyph': 'b',
                    'fwd_type_idn': 'blocked',
                    'fwd_type_ref': 'blocked',
                    'reverse': True,
                    'rev_type_idn': 'blocked',
                    'rev_type_ref': 'blocked',
                    'dest_in_idn': True,
                    'dest_in_ref': True,
                    'symmetric': True,
                    'result_fwd': 'MATCH',
                    'result_rev': 'MATCH',
                    'remark_fwd': 'Exact match (including type, conditional variant rule)',
                    'remark_rev': 'Exact match (including type, conditional variant rule)'
                }, {
                    'source_cp': 'U+0061',
                    'source_glyph': 'a',
                    'dest_cp': 'U+0063',
                    'dest_glyph': 'c',
                    'fwd_type_idn': 'invalid',
                    'fwd_type_ref': 'invalid',
                    'reverse': True,
                    'rev_type_idn': 'blocked',
                    'rev_type_ref': 'blocked',
                    'dest_in_idn': True,
                    'dest_in_ref': True,
                    'symmetric': False,
                    'result_fwd': 'MATCH',
                    'result_rev': 'MATCH',
                    'remark_fwd': 'Exact match (including type, conditional variant rule)',
                    'remark_rev': 'Exact match (including type, conditional variant rule)'
                }, {
                    'source_cp': 'U+0062',
                    'source_glyph': 'b',
                    'dest_cp': 'U+0063',
                    'dest_glyph': 'c',
                    'fwd_type_idn': 'blocked',
                    'fwd_type_ref': 'blocked',
                    'reverse': True,
                    'rev_type_idn': 'allocatable',
                    'rev_type_ref': 'allocatable',
                    'dest_in_idn': True,
                    'dest_in_ref': True,
                    'symmetric': False,
                    'result_fwd': 'MATCH',
                    'result_rev': 'MATCH',
                    'remark_fwd': 'Exact match (including type, conditional variant rule)',
                    'remark_rev': 'Exact match (including type, conditional variant rule)'
                }
            ]
        }, {
            'set_number': (111, 101),
            'idn_table': ((111, 101), (339,)),
            'ref_lgr': ((111, 101), (339,)),
            'relevant_idn_table_repertoire': ((111, 101), (339,)),
            'symmetry_check': True,
            'transitivity_check': True,
            'report': [
                {
                    'source_cp': 'U+006F U+0065',
                    'source_glyph': 'oe',
                    'dest_cp': 'U+0153',
                    'dest_glyph': 'œ',
                    'fwd_type_idn': 'blocked',
                    'fwd_type_ref': 'blocked',
                    'reverse': True,
                    'rev_type_idn': 'blocked',
                    'rev_type_ref': 'blocked',
                    'dest_in_idn': True,
                    'dest_in_ref': True,
                    'symmetric': True,
                    'result_fwd': 'MATCH',
                    'result_rev': 'MATCH',
                    'remark_fwd': 'Exact match (including type, conditional variant rule)',
                    'remark_rev': 'Exact match (including type, conditional variant rule)'
                }
            ]
        }])
