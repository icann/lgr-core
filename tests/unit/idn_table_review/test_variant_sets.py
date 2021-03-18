#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_variant_sets - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.variant_sets import generate_variant_sets_report
from tests.unit.unicode_database_mock import UnicodeDatabaseMock
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_variant_sets')


class Test(TestCase):
    ref = load_lgr('idn_table_review', 'reference_lgr.xml')
    report_oe = {
        'idn_table': ((111, 101), (339,)),
        'ref_lgr': ((111, 101), (339,)),
        'relevant_idn_table_repertoire': ((111, 101), (339,)),
        'symmetry_check': True,
        'transitivity_check': True,
        'report': [
            {
                'source_cp': (111, 101),
                'source_glyph': 'oe',
                'dest_cp': (339,),
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
    }

    def setUp(self) -> None:
        super().setUp()
        self.unidb = UnicodeDatabaseMock()
        self.maxDiff = None

    def test_generate_variant_sets_report_exact_match(self):
        idn = load_lgr('idn_table_review/variant_sets', 'variant_sets_exact_match.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,), (99,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
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
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'activated',
                        'fwd_type_ref': 'activated',
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
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
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
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_subset_match(self):
        idn = load_lgr('idn_table_review/variant_sets', 'variant_sets_subset_match.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
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
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'activated',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'NOTE',
                        'result_rev': 'NOTE',
                        'remark_fwd': 'Not applicable',
                        'remark_rev': 'Not applicable'
                    }, {
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'allocatable',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'NOTE',
                        'result_rev': 'NOTE',
                        'remark_fwd': 'Not applicable',
                        'remark_rev': 'Not applicable'
                    }
                ]
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_missing(self):
        idn = load_lgr('idn_table_review/variant_sets', 'variant_sets_missing.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': (),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': None,
                'transitivity_check': None,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
                        'dest_glyph': 'b',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': True,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Variant set exists in the reference LGR',
                        'remark_rev': 'Variant set exists in the reference LGR'
                    }, {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'activated',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Variant set exists in the reference LGR',
                        'remark_rev': 'Variant set exists in the reference LGR'
                    }, {
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'allocatable',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Variant set exists in the reference LGR',
                        'remark_rev': 'Variant set exists in the reference LGR'
                    }
                ]
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_missing_variant_members(self):
        idn = load_lgr('idn_table_review/variant_sets', 'variant_sets_missing_variant_members.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
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
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'activated',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Variant member exists in the reference LGR',
                        'remark_rev': 'Variant member exists in the reference LGR'
                    }, {
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': '',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': '',
                        'rev_type_ref': 'allocatable',
                        'dest_in_idn': False,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Variant member exists in the reference LGR',
                        'remark_rev': 'Variant member exists in the reference LGR'
                    }
                ]
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_report_mismatch_contextual_rule_idn_table_less_conservative(self):
        idn = load_lgr('idn_table_review/variant_sets',
                       'variant_sets_mismatch_contextual_rule_idn_table_less_conservative.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,), (99,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
                        'dest_glyph': 'b',
                        'fwd_type_idn': 'blocked',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': 'blocked',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': True,
                        'dest_in_ref': True,
                        'symmetric': True,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'MATCH',
                        'remark_fwd': 'IDN Table variant generation is less conservative as it only applies with some conditions',
                        'remark_rev': 'Exact match (including type, conditional variant rule)'
                    }, {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'activated',
                        'fwd_type_ref': 'activated',
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
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
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
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_report_mismatch_contextual_rule_idn_table_more_conservative(self):
        idn = load_lgr('idn_table_review/variant_sets',
                       'variant_sets_mismatch_contextual_rule_idn_table_more_conservative.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,), (99,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
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
                        'result_rev': 'MANUAL CHECK',
                        'remark_fwd': 'Exact match (including type, conditional variant rule)',
                        'remark_rev': 'Variant condition rules are mismatched. The IDN Table misses the rule. '
                                      'If the rule is not needed for the proper variant index calculation, then this is ok'
                    }, {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'activated',
                        'fwd_type_ref': 'activated',
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
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
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
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_report_mismatch_variant_type_idn_type_less_conservative(self):
        idn = load_lgr('idn_table_review/variant_sets',
                       'variant_sets_mismatch_variant_type_and_idn_type_less_conservative.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,), (99,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
                        'dest_glyph': 'b',
                        'fwd_type_idn': 'allocatable',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': 'blocked',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': True,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'MATCH',
                        'remark_fwd': 'Variant type in the IDN Table is less conservative compared to the Ref. LGR',
                        'remark_rev': 'Exact match (including type, conditional variant rule)'
                    }, {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'activated',
                        'fwd_type_ref': 'activated',
                        'reverse': True,
                        'rev_type_idn': 'optionally-allocatable',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': True,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'MATCH',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Exact match (including type, conditional variant rule)',
                        'remark_rev': 'Variant type in the IDN Table is less conservative compared to the Ref. LGR'
                    }, {
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'blocked',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': 'unknown',
                        'rev_type_ref': 'allocatable',
                        'dest_in_idn': True,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'MATCH',
                        'result_rev': 'REVIEW',
                        'remark_fwd': 'Exact match (including type, conditional variant rule)',
                        'remark_rev': 'Unknown variant type'
                    }
                ]
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_report_mismatch_variant_type_idn_type_more_conservative(self):
        idn = load_lgr('idn_table_review/variant_sets',
                       'variant_sets_mismatch_variant_type_and_idn_type_more_conservative.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,), (99,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
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
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'blocked',
                        'fwd_type_ref': 'activated',
                        'reverse': True,
                        'rev_type_idn': 'blocked',
                        'rev_type_ref': 'blocked',
                        'dest_in_idn': True,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'NOTE',
                        'result_rev': 'MATCH',
                        'remark_fwd': 'Variant types are mismatched. '
                                      'IDN Table is more conservative comparing to the Reference LGR',
                        'remark_rev': 'Exact match (including type, conditional variant rule)'
                    }, {
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'unknown',
                        'fwd_type_ref': 'blocked',
                        'reverse': True,
                        'rev_type_idn': 'optionally-allocatable',
                        'rev_type_ref': 'allocatable',
                        'dest_in_idn': True,
                        'dest_in_ref': True,
                        'symmetric': False,
                        'result_fwd': 'REVIEW',
                        'result_rev': 'NOTE',
                        'remark_fwd': 'Unknown variant type',
                        'remark_rev': 'Variant types are mismatched. '
                                      'IDN Table is more conservative comparing to the Reference LGR'
                    }
                ]
            }, self.report_oe],
            'additional': []
        })

    def test_generate_variant_sets_additional(self):
        idn = load_lgr('idn_table_review/variant_sets', 'variant_sets_additional.xml', unidb=self.unidb)

        result = generate_variant_sets_report(idn, self.ref)

        self.assertDictEqual(result, {
            'reports': [{
                'idn_table': ((97,), (98,), (99,)),
                'ref_lgr': ((97,), (98,), (99,)),
                'relevant_idn_table_repertoire': ((97,), (98,), (99,)),
                'symmetry_check': True,
                'transitivity_check': True,
                'report': [
                    {
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (98,),
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
                        'source_cp': (97,),
                        'source_glyph': 'a',
                        'dest_cp': (99,),
                        'dest_glyph': 'c',
                        'fwd_type_idn': 'activated',
                        'fwd_type_ref': 'activated',
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
                        'source_cp': (98,),
                        'source_glyph': 'b',
                        'dest_cp': (99,),
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
            }, self.report_oe],
            'additional': [{
                'cp': (112,),
                'glyph': 'p',
                'name': 'LATIN SMALL LETTER P'
            }, {
                'cp': (113,),
                'glyph': 'q',
                'name': 'LATIN SMALL LETTER Q'
            }]
        })
