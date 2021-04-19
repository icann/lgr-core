#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
test_summary - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.summary import generate_summary

logger = logging.getLogger('test_summary')


class Test(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def test_generate_summary(self):
        reports = {
            'language_tags': [{
                'idn_table_language_tag': 'ar-arab',
                'comparison': [{
                    'reference_lgr_language_tag': 'und-Arab',
                    'result': 'MATCH',
                    'remark': 'The language tag in IDN Table relevant to the script tag in Reference LGR'
                }, {
                    'reference_lgr_language_tag': 'zh-hani',
                    'result': 'REVIEW',
                    'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
                }]
            }],
            'repertoire': {
                'reports': [{
                    'cp': (97,),
                    'glyph': 'a',
                    'name': 'LATIN SMALL LETTER A',
                    'idn_table': True,
                    'reference_lgr': True,
                    'result': 'MATCH',
                    'remark': 'Matches code point (including tags, context rule)'
                }, {
                    'cp': (98,),
                    'glyph': 'b',
                    'name': 'LATIN SMALL LETTER B',
                    'idn_table': True,
                    'reference_lgr': True,
                    'result': 'MATCH',
                    'remark': 'Matches code point (including tags, context rule)'
                }, {
                    'cp': (99,),
                    'glyph': 'c',
                    'name': 'LATIN SMALL LETTER C',
                    'idn_table': True,
                    'reference_lgr': True,
                    'result': 'NOTE',
                    'remark': 'Rules not required in Reference LGR'
                }],
                'cp_in_sequences': []
            },
            'variant_sets': {
                'reports': [{
                    'idn_table': (),
                    'ref_lgr': ((97,), (98,)),
                    'relevant_idn_table_repertoire': ((97,), (98,)),
                    'symmetry_check': None,
                    'transitivity_check': None,
                    'report': [{
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
                    }]
                }],
                'additional': []
            },
            'classes': [{
                'name': "union",
                'idn_members': ['b', 'c', 'g', 'h', 'i'],
                'ref_members': ['b', 'c', 'g', 'h', 'i'],
                'result': 'MATCH',
                'remark': 'Classes and their members are matched'
            }, {
                'name': "union",
                'idn_members': ['b', 'c', 'g'],
                'ref_members': ['b', 'c', 'g', 'h', 'i'],
                'result': 'SUBSET',
                'remark': 'Extra members in Ref. LGR not in IDN Table'
            }],
            'wle': {
                'comparison': [{
                    'name': 'not-match',
                    'idn_table': False,
                    'reference_lgr': True,
                    'result': 'SUBSET',
                    'remark': 'Match as a subset (for the rules missing in IDN Table, '
                              'applicable code points in Ref. LGR are not in IDN Table)'
                }, {
                    'name': 'match',
                    'idn_table': True,
                    'reference_lgr': True,
                    'result': 'MANUAL CHECK',
                    'remark': 'Check the content of the rule'
                }],
                'additional_cp': [],
                'additional_general_rules': {
                    'combining_mark': {
                        'applicable': False,
                        'exists': None
                    },
                    'consecutive_hyphens': {
                        'applicable': False,
                        'exists': None
                    },
                    'rtl': {
                        'applicable': False,
                        'exists': None
                    },
                    'digits_set': {
                        'applicable': False,
                        'exists': None
                    }
                }
            },
            'actions': {
                'comparison': [{
                    'name': 'IDN Table-1 (0)',
                    'idn_table': True,
                    'reference_lgr': True,
                    'result': 'MATCH',
                    'remark': 'Exact Match (action name and content are the same)'
                }, {
                    'name': 'IDN Table-2 (additional)',
                    'idn_table': True,
                    'reference_lgr': False,
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (additional action)'
                }],
                'sequence': 'MATCH'
            }
        }

        result = generate_summary(reports)
        self.assertDictEqual(result, {
            'language_tag': {
                'overall': 'REVIEW',
                'results': [{
                    'result': 'MATCH',
                    'remark': 'The language tag in IDN Table relevant to the script tag in Reference LGR',
                    'count': 1
                }, {
                    'result': 'REVIEW',
                    'remark': 'The language tag in IDN Table and Reference LGR are mismatched',
                    'count': 1
                }]
            },
            'repertoire': {
                'overall': 'NOTE',
                'results': [{
                    'result': 'MATCH',
                    'remark': 'Matches code point (including tags, context rule)',
                    'count': 2
                }, {
                    'result': 'NOTE',
                    'remark': 'Rules not required in Reference LGR',
                    'count': 1
                }]
            },
            'variant_sets': {
                'overall': 'REVIEW',
                'results': [{
                    'result': 'REVIEW',
                    'remark': 'IDN Table variant generation is less conservative as it only applies with some conditions',
                    'count': 1
                }, {
                    'result': 'MATCH',
                    'remark': 'Exact match (including type, conditional variant rule)',
                    'count': 1
                }]
            },
            'classes': {
                'overall': 'SUBSET',
                'results': [{
                    'result': 'MATCH',
                    'remark': 'Classes and their members are matched',
                    'count': 1
                }, {
                    'result': 'SUBSET',
                    'remark': 'Extra members in Ref. LGR not in IDN Table',
                    'count': 1
                }]
            },
            'wle': {
                'overall': 'MANUAL CHECK',
                'results': [{
                    'result': 'SUBSET',
                    'remark': 'Match as a subset (for the rules missing in IDN Table, '
                              'applicable code points in Ref. LGR are not in IDN Table)',
                    'count': 1
                }, {
                    'result': 'MANUAL CHECK',
                    'remark': 'Check the content of the rule',
                    'count': 1
                }]
            },
            'actions': {
                'overall': 'MANUAL CHECK',
                'results': [{
                    'result': 'MATCH',
                    'remark': 'Exact Match (action name and content are the same)',
                    'count': 1
                }, {
                    'result': 'MANUAL CHECK',
                    'remark': 'Mismatch (additional action)',
                    'count': 1
                }]
            },
        })
