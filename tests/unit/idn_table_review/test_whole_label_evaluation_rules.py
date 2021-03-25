#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_whole_label_evaluation_rules -
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
    general_rules_combining_mark = {
        'applicable': False,
        'exists': None
    }
    general_rules_consecutive_hyphens = {
        'applicable': False,
        'exists': None
    }
    general_rules_rtl = {
        'applicable': False,
        'exists': None
    }
    general_rules_digits_sets = {
        'applicable': False,
        'exists': None
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
            'additional_cp': [],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
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
            'additional_cp': [],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
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
            'additional_cp': [],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
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
                'remark': 'Check the content of the rule'
            }, self.not_match_match],
            'additional_cp': [],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
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
                'remark': 'Check the content of the rule'
            }, self.not_match_match],
            'additional_cp': [],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_combining_mark_applicable_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_combining_marks.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'leading-combining-mark',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [
                {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA'},
                {'cp': (2497,), 'glyph': 'ু', 'name': 'BENGALI VOWEL SIGN U'}
            ],
            'additional_general_rules': {
                'combining_mark': {
                    'applicable': True,
                    'exists': True
                },
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_combining_mark_applicable_missing_cp(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_combining_marks_missing_cp.xml',
                       unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'leading-combining-mark',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [{'cp': (2497,), 'glyph': 'ু', 'name': 'BENGALI VOWEL SIGN U'}],
            'additional_general_rules': {
                'combining_mark': {
                    'applicable': True,
                    'exists': None
                },
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_combining_mark_applicable_not_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_combining_marks_wrong.xml',
                       unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, self.match_match, self.not_match_match],
            'additional_cp': [
                {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA'},
                {'cp': (2497,), 'glyph': 'ু', 'name': 'BENGALI VOWEL SIGN U'}
            ],
            'additional_general_rules': {
                'combining_mark': {
                    'applicable': True,
                    'exists': False
                },
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_hyphen_applicable_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_hyphen.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'hyphen-minus-disallowed',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [{'cp': (109,), 'glyph': 'm', 'name': 'LATIN SMALL LETTER M'}],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': {
                    'applicable': True,
                    'exists': True
                },
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_hyphen_applicable_not_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_hyphen_wrong.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'hyphen-minus-disallowed',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [{'cp': (109,), 'glyph': 'm', 'name': 'LATIN SMALL LETTER M'}],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': {
                    'applicable': True,
                    'exists': False
                },
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_rtl_digit_applicable_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_rtl.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, self.match_match, self.not_match_match],
            'additional_cp': [{'cp': (1489,), 'glyph': 'ב', 'name': 'HEBREW LETTER BET'}],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': {
                    'applicable': True,
                    'exists': False
                },
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_rtl_digit_applicable_not_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_rtl_wrong.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'leading-digit',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [{'cp': (1489,), 'glyph': 'ב', 'name': 'HEBREW LETTER BET'}],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': {
                    'applicable': True,
                    'exists': True
                },
                'digits_set': self.general_rules_digits_sets,
            }
        })

    def test_wle_digits_mixing_applicable_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_digits_sets.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'digit-mixing',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [
                {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA'},
                {'cp': (2534,), 'glyph': '০', 'name': 'BENGALI DIGIT ZERO'},
                {'cp': (2535,), 'glyph': '১', 'name': 'BENGALI DIGIT ONE'},
                {'cp': (2536,), 'glyph': '২', 'name': 'BENGALI DIGIT TWO'},
                {'cp': (2537,), 'glyph': '৩', 'name': 'BENGALI DIGIT THREE'},
                {'cp': (2538,), 'glyph': '৪', 'name': 'BENGALI DIGIT FOUR'},
                {'cp': (2539,), 'glyph': '৫', 'name': 'BENGALI DIGIT FIVE'},
                {'cp': (2540,), 'glyph': '৬', 'name': 'BENGALI DIGIT SIX'},
                {'cp': (2541,), 'glyph': '৭', 'name': 'BENGALI DIGIT SEVEN'},
                {'cp': (2542,), 'glyph': '৮', 'name': 'BENGALI DIGIT EIGHT'},
                {'cp': (2543,), 'glyph': '৯', 'name': 'BENGALI DIGIT NINE'},
            ],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_digits_sets,
                'digits_set': {
                    'applicable': True,
                    'exists': True
                },
            }
        })

    def test_wle_digits_mixing_applicable_not_ok(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_digits_sets_wrong.xml', unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [self.all_match_match, {
                'name': 'digit-mixing',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in IDN Table)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [
                {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA'},
                {'cp': (2534,), 'glyph': '০', 'name': 'BENGALI DIGIT ZERO'},
                {'cp': (2535,), 'glyph': '১', 'name': 'BENGALI DIGIT ONE'},
                {'cp': (2536,), 'glyph': '২', 'name': 'BENGALI DIGIT TWO'},
                {'cp': (2537,), 'glyph': '৩', 'name': 'BENGALI DIGIT THREE'},
                {'cp': (2538,), 'glyph': '৪', 'name': 'BENGALI DIGIT FOUR'},
                {'cp': (2539,), 'glyph': '৫', 'name': 'BENGALI DIGIT FIVE'},
                {'cp': (2540,), 'glyph': '৬', 'name': 'BENGALI DIGIT SIX'},
                {'cp': (2541,), 'glyph': '৭', 'name': 'BENGALI DIGIT SEVEN'},
                {'cp': (2542,), 'glyph': '৮', 'name': 'BENGALI DIGIT EIGHT'},
                {'cp': (2543,), 'glyph': '৯', 'name': 'BENGALI DIGIT NINE'},
            ],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_digits_sets,
                'digits_set': {
                    'applicable': True,
                    'exists': False
                },
            }
        })

    def test_wle_missing_in_idn_table_not_applied_to_cp(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_missing_in_idn_table_not_applied_to_cp.xml',
                       unidb=self.unidb)

        result = generate_whole_label_evaluation_rules_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [{
                'name': 'all-match',
                'idn_table': False,
                'reference_lgr': True,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (WLE rule only exists in Ref. LGR)'
            }, self.match_match, self.not_match_match],
            'additional_cp': [],
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
            }
        })