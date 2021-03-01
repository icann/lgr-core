#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_variant_sets - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.whole_label_evaluation_rules import generate_whole_label_evaluation_rules_report
from tests.unit.unicode_database_mock import UnicodeDatabaseMock
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_variant_sets')


class Test(TestCase):
    match_match = {
        'name': 'match',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (matched names and content)'
    }
    not_match_match = {
        'name': 'not-match',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (matched names and content)'
    }
    all_match_match = {
        'name': 'all-match',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (matched names and content)'
    }
    additional_cp = [{
        'cp': (100,),
        'glyph': 'd',
        'name': 'LATIN SMALL LETTER D'
    }, {
        'cp': (101,),
        'glyph': 'e',
        'name': 'LATIN SMALL LETTER E'
    }, {
        'cp': (102,),
        'glyph': 'f',
        'name': 'LATIN SMALL LETTER F'
    }, {
        'cp': (103,),
        'glyph': 'g',
        'name': 'LATIN SMALL LETTER G'
    }, {
        'cp': (104,),
        'glyph': 'h',
        'name': 'LATIN SMALL LETTER H'
    }, {
        'cp': (105,),
        'glyph': 'i',
        'name': 'LATIN SMALL LETTER I'
    }, {
        'cp': (339,),
        'glyph': 'œ',
        'name': 'LATIN SMALL LIGATURE OE'
    }]
    general_rules_combining_mark = {
        'applicable': False,
        'exists': False
    }
    general_rules_consecutive_hyphens = {
        'applicable': False,
        'exists': False
    }
    general_rules_rtl = {
        'applicable': False,
        'exists': False
    }
    general_rules_digits_sets = {
        'applicable': False,
        'exists': False
    }
    general_rules_ascii_cp = {
        'applicable': True,
        'exists': False
    }

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.unidb = UnicodeDatabaseMock()
        self.ref = load_lgr('idn_table_review', 'reference_lgr.xml', unidb=self.unidb)

    def test_wle_subset(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_subset.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, self.match_match, {
                'name': 'not-match',
                'idn_table': False,
                'reference_lgr': True,
                'result': 'SUBSET',
                'remark': 'Match as a subset (for the rules missing in IDN Table, '
                          'applicable code points in Ref. LGR are not in IDN Table)'
            }],
            'additional_cp': self.additional_cp,
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'ascii_cp': self.general_rules_ascii_cp
            }
        })

    def test_wle_missing_in_ref_lgr(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_missing_in_ref_lgr.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, self.match_match, {
                'name': 'new',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.not_match_match],
            'additional_cp': self.additional_cp,
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'ascii_cp': self.general_rules_ascii_cp
            }
        })

    def test_wle_missing_in_idn_table(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_missing_in_idn_table.xml',
                       unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, self.match_match, {
                'name': 'not-match',
                'idn_table': False,
                'reference_lgr': True,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in Ref. LGR)'
            }],
            'additional_cp': sorted([{
                'cp': (99,),
                'glyph': 'c',
                'name': 'LATIN SMALL LETTER C'
            }, {
                'cp': (111, 101),
                'glyph': 'oe',
                'name': 'LATIN SMALL LETTER O LATIN SMALL LETTER E'
            }] + self.additional_cp, key=lambda x: x['cp']),
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'ascii_cp': self.general_rules_ascii_cp
            }
        })

    def test_wle_mismatch_cp(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_mismatch_cp.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'match',
                'idn_table': True,
                'reference_lgr': True,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch class (content mismatch)'
            }, self.not_match_match],
            'additional_cp': self.additional_cp[1:],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'ascii_cp': self.general_rules_ascii_cp
            }
        })

    def test_wle_mismatch_content(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_mismatch_content.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'match',
                'idn_table': True,
                'reference_lgr': True,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch class (content mismatch)'
            }, self.not_match_match],
            'additional_cp': self.additional_cp,
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'ascii_cp': self.general_rules_ascii_cp
            }
        })
