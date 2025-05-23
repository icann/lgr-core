#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_whole_label_evaluation_rules -
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.whole_label_evaluation_rules import generate_whole_label_evaluation_rules_report, \
    generate_whole_label_evaluation_rules_core_report
from lgr.test_utils.unicode_database_mock import UnicodeDatabaseMock
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
        'exists': None,
    }
    general_rules_consecutive_hyphens = {
        'applicable': False,
        'exists': None,
    }
    general_rules_rtl = {
        'applicable': False,
        'exists': None,
    }
    general_rules_digits_sets = {
        'applicable': False,
        'exists': None,
    }
    general_rules_japanese_contextj = {
        'applicable': False,
        'exists': None,
    }
    general_rules_arabic_no_end = {
        'applicable': False,
        'exists': None,
    }
    general_rules_kannada_script = {
        'applicable': False,
        'exists': None,
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
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
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
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
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
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
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
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
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
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        })

    def wle_combining_mark_applicable_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_combining_marks.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': {
                    'applicable': True,
                    'exists': True,
                },
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'leading-combining-mark',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [
                    {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA', 'idna_property': 'PVALID',
                     'category': 'Lo'},
                    {
                        'cp': (2497,),
                        'glyph': 'ু',
                        'name': 'BENGALI VOWEL SIGN U',
                        'idna_property': 'PVALID',
                        'category': 'Mn'
                    }
                ]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_combining_mark_applicable_missing_cp(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_combining_marks_missing_cp.xml',
                       unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': {
                    'applicable': True,
                    'exists': None,
                },
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'leading-combining-mark',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [{
                    'cp': (2497,),
                    'glyph': 'ু',
                    'name': 'BENGALI VOWEL SIGN U',
                    'idna_property': 'PVALID',
                    'category': 'Mn'
                }]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_combining_mark_applicable_not_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_combining_marks_wrong.xml',
                       unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': {
                    'applicable': True,
                    'exists': False,
                },
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, self.match_match, self.not_match_match],
                'additional_cp': [
                    {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA', 'idna_property': 'PVALID',
                     'category': 'Lo'},
                    {'cp': (2497,),
                     'glyph': 'ু',
                     'name': 'BENGALI VOWEL SIGN U',
                     'idna_property': 'PVALID',
                     'category': 'Mn'
                     }
                ]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_hyphen_applicable_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_hyphen.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': {
                    'applicable': True,
                    'exists': True,
                },
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'hyphen-minus-disallowed',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [{
                    'cp': (109,),
                    'glyph': 'm',
                    'name': 'LATIN SMALL LETTER M',
                    'idna_property': 'PVALID',
                    'category': 'Ll'}]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_hyphen_applicable_not_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_hyphen_wrong.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': {
                    'applicable': True,
                    'exists': False,
                },
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'hyphen-minus-disallowed',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [{
                    'cp': (109,),
                    'glyph': 'm',
                    'name': 'LATIN SMALL LETTER M',
                    'idna_property': 'PVALID',
                    'category': 'Ll'
                }]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_rtl_digit_applicable_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_rtl.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': {
                    'applicable': True,
                    'exists': True,
                },
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'leading-digit',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [{
                    'cp': (1489,),
                    'glyph': 'ב',
                    'name': 'HEBREW LETTER BET',
                    'idna_property': 'PVALID',
                    'category': 'Lo'
                }]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_rtl_digit_applicable_not_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_rtl_wrong.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': {
                    'applicable': True,
                    'exists': False,
                },
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, self.match_match, self.not_match_match],
                'additional_cp': [{
                    'cp': (1489,),
                    'glyph': 'ב',
                    'name': 'HEBREW LETTER BET',
                    'idna_property': 'PVALID',
                    'category': 'Lo'
                }]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_digits_mixing_applicable_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_digits_sets.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_digits_sets,
                'digits_set': {
                    'applicable': True,
                    'exists': True,
                },
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'digit-mixing',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [
                    {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA', 'idna_property': 'PVALID',
                     'category': 'Lo'},
                    {'cp': (2534,), 'glyph': '০', 'name': 'BENGALI DIGIT ZERO', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2535,), 'glyph': '১', 'name': 'BENGALI DIGIT ONE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2536,), 'glyph': '২', 'name': 'BENGALI DIGIT TWO', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2537,), 'glyph': '৩', 'name': 'BENGALI DIGIT THREE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2538,), 'glyph': '৪', 'name': 'BENGALI DIGIT FOUR', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2539,), 'glyph': '৫', 'name': 'BENGALI DIGIT FIVE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2540,), 'glyph': '৬', 'name': 'BENGALI DIGIT SIX', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2541,), 'glyph': '৭', 'name': 'BENGALI DIGIT SEVEN', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2542,), 'glyph': '৮', 'name': 'BENGALI DIGIT EIGHT', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2543,), 'glyph': '৯', 'name': 'BENGALI DIGIT NINE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                ]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_digits_mixing_applicable_not_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_digits_sets_wrong.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_digits_sets,
                'digits_set': {
                    'applicable': True,
                    'exists': False,
                },
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'digit-mixing',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [
                    {'cp': (2478,), 'glyph': 'ম', 'name': 'BENGALI LETTER MA', 'idna_property': 'PVALID',
                     'category': 'Lo'},
                    {'cp': (2534,), 'glyph': '০', 'name': 'BENGALI DIGIT ZERO', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2535,), 'glyph': '১', 'name': 'BENGALI DIGIT ONE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2536,), 'glyph': '২', 'name': 'BENGALI DIGIT TWO', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2537,), 'glyph': '৩', 'name': 'BENGALI DIGIT THREE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2538,), 'glyph': '৪', 'name': 'BENGALI DIGIT FOUR', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2539,), 'glyph': '৫', 'name': 'BENGALI DIGIT FIVE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2540,), 'glyph': '৬', 'name': 'BENGALI DIGIT SIX', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2541,), 'glyph': '৭', 'name': 'BENGALI DIGIT SEVEN', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2542,), 'glyph': '৮', 'name': 'BENGALI DIGIT EIGHT', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                    {'cp': (2543,), 'glyph': '৯', 'name': 'BENGALI DIGIT NINE', 'idna_property': 'PVALID',
                     'category': 'Nd'},
                ]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def japanese_contextj_applicable_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_japanese_contextj.xml', unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': {
                    'applicable': True,
                    'exists': True,
                },
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'contextj',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in IDN Table)'
                }, {
                                   'name': 'match',
                                   'idn_table': True,
                                   'reference_lgr': True,
                                   'result': 'MANUAL CHECK',
                                   'remark': 'Check the content of the rule'
                               }, self.not_match_match],
                'additional_cp': [{
                    'cp': (12353,),
                    'glyph': 'ぁ',
                    'name': 'HIRAGANA LETTER SMALL A',
                    'idna_property': 'PVALID',
                    'category': 'Lo'
                }]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def japanese_contextj_missing_cp(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_japanese_contextj_missing_cp.xml',
                       unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': {
                    'applicable': False,
                    'exists': None,
                },
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, self.match_match, self.not_match_match],
                'additional_cp': [],
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def japanese_contextj_applicable_not_ok(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_japanese_contextj_wrong.xml',
                       unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': {
                    'applicable': True,
                    'exists': False,
                },
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [self.all_match_match, {
                    'name': 'match',
                    'idn_table': True,
                    'reference_lgr': True,
                    'result': 'MANUAL CHECK',
                    'remark': 'Check the content of the rule'
                }, self.not_match_match],
                'additional_cp': [{
                    'cp': (12539,),
                    'glyph': '・',
                    'name': 'KATAKANA MIDDLE DOT',
                    'idna_property': 'CONTEXTO',
                    'category': 'Po'
                }]
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def wle_missing_in_idn_table_not_applied_to_cp(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules',
                       'wle_missing_in_idn_table_not_applied_to_cp.xml',
                       unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        if not core:
            result = generate_whole_label_evaluation_rules_report(idn, self.ref)
            expected = {
                'comparison': [{
                    'name': 'all-match',
                    'idn_table': False,
                    'reference_lgr': True,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (WLE rule only exists in Ref. LGR)'
                }, self.match_match, self.not_match_match],
                'additional_cp': [],
            }
            expected.update(additional_general_rules)
        else:
            result = generate_whole_label_evaluation_rules_core_report(idn)
            expected = additional_general_rules

        self.assertDictEqual(result, expected)

    def test_wle_combining_mark_applicable_ok(self):
        self.wle_combining_mark_applicable_ok()

    def test_wle_combining_mark_applicable_missing_cp(self):
        self.wle_combining_mark_applicable_missing_cp()

    def test_wle_combining_mark_applicable_not_ok(self):
        self.wle_combining_mark_applicable_not_ok()

    def test_wle_hyphen_applicable_ok(self):
        self.wle_hyphen_applicable_ok()

    def test_wle_hyphen_applicable_not_ok(self):
        self.wle_hyphen_applicable_not_ok()

    def test_wle_rtl_digit_applicable_ok(self):
        self.wle_rtl_digit_applicable_ok()

    def test_wle_rtl_digit_applicable_not_ok(self):
        self.wle_rtl_digit_applicable_not_ok()

    def test_wle_digits_mixing_applicable_ok(self):
        self.wle_digits_mixing_applicable_ok()

    def test_wle_digits_mixing_applicable_not_ok(self):
        self.wle_digits_mixing_applicable_not_ok()

    def test_japanese_contextj_applicable_ok(self):
        self.japanese_contextj_applicable_ok()

    def test_japanese_contextj_missing_cp(self):
        self.japanese_contextj_missing_cp()

    def test_japanese_contextj_applicable_not_ok(self):
        self.japanese_contextj_applicable_not_ok()

    def test_wle_missing_in_idn_table_not_applied_to_cp(self):
        self.wle_missing_in_idn_table_not_applied_to_cp()

    def test_wle_core_requirements(self):
        result = generate_whole_label_evaluation_rules_core_report(self.ref)

        self.assertDictEqual(result, {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': {
                    'applicable': True,
                    'exists': None,
                },
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        })

    def test_wle_core_requirements_no_language_tags(self):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_no_language_tags.xml', unidb=self.unidb)
        result = generate_whole_label_evaluation_rules_core_report(idn)

        self.assertDictEqual(result, {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': self.general_rules_rtl,
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        })

    def test_wle_combining_mark_applicable_ok_core_requirements(self):
        self.wle_combining_mark_applicable_ok(core=True)

    def test_wle_combining_mark_applicable_missing_cp_core_requirements(self):
        self.wle_combining_mark_applicable_missing_cp(core=True)

    def test_wle_combining_mark_applicable_not_ok_core_requirements(self):
        self.wle_combining_mark_applicable_not_ok(core=True)

    def test_wle_hyphen_applicable_ok_core_requirements(self):
        self.wle_hyphen_applicable_ok(core=True)

    def test_wle_hyphen_applicable_not_ok_core_requirements(self):
        self.wle_hyphen_applicable_not_ok(core=True)

    def test_wle_rtl_digit_applicable_ok_core_requirements(self):
        self.wle_rtl_digit_applicable_ok(core=True)

    def test_wle_rtl_digit_applicable_not_ok_core_requirements(self):
        self.wle_rtl_digit_applicable_not_ok(core=True)

    def test_wle_digits_mixing_applicable_ok_core_requirements(self):
        self.wle_digits_mixing_applicable_ok(core=True)

    def test_wle_digits_mixing_applicable_not_ok_core_requirements(self):
        self.wle_digits_mixing_applicable_not_ok(core=True)

    def test_japanese_contextj_applicable_ok_core_requirements(self):
        self.japanese_contextj_applicable_ok(core=True)

    def test_japanese_contextj_missing_cp_core_requirements(self):
        self.japanese_contextj_missing_cp(core=True)

    def test_japanese_contextj_applicable_not_ok_core_requirements(self):
        self.japanese_contextj_applicable_not_ok(core=True)

    def test_wle_missing_in_idn_table_not_applied_to_cp_core_requirements(self):
        self.wle_missing_in_idn_table_not_applied_to_cp(core=True)

    def test_wle_rtl_digit_applicable_no_script_ok_core_requirements(self, core=False):
        idn = load_lgr('idn_table_review/whole_label_evaluation_rules', 'wle_rtl_script_not_specified.xml',
                       unidb=self.unidb)

        additional_general_rules = {
            'additional_general_rules': {
                'combining_mark': self.general_rules_combining_mark,
                'consecutive_hyphens': self.general_rules_consecutive_hyphens,
                'rtl': {
                    'applicable': True,
                    'exists': None,
                },
                'digits_set': self.general_rules_digits_sets,
                'japanese_contextj': self.general_rules_japanese_contextj,
                # 'arabic_no_extended_end': self.general_rules_arabic_no_end,
            }
        }

        result = generate_whole_label_evaluation_rules_core_report(idn)

        self.assertDictEqual(result, additional_general_rules)
