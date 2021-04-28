#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_language_tag -
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.language_tag import generate_language_tag_report
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_variant_sets')


class Test(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.ref = load_lgr('idn_table_review', 'reference_lgr.xml')

    def test_language_tag(self):
        idn = load_lgr('idn_table_review/language_tag', 'language_tag.xml')

        result = generate_language_tag_report(idn, self.ref)

        self.assertCountEqual(result, [{
            'idn_table_language_tag': 'arab',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MATCH',
                'remark': 'Exact match'
            }]
        }, {
            'idn_table_language_tag': 'ar',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MATCH',
                'remark': 'Exact match'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MATCH',
                'remark': 'The language tag in IDN Table relevant to the script tag in Reference LGR'
            }]
        }, {
            'idn_table_language_tag': 'ar-arab',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MATCH',
                'remark': 'Consider minimizing the tag as per the RFC5646 and IANA subtag registry'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MATCH',
                'remark': 'The language tag in IDN Table relevant to the script tag in Reference LGR'
            }]
        }, {
            'idn_table_language_tag': 'test-unexisting',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may be included in the comment'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may be included in the comment'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may be included in the comment'
            }]
        }, {
            'idn_table_language_tag': 'ja',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'MATCH',
                'remark': 'Language match'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }]
        }, {
            'idn_table_language_tag': 'ja-hira',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'MATCH',
                'remark': 'Exact match'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }]
        }])

    def test_language_tag_none(self):
        idn = load_lgr('idn_table_review/language_tag', 'language_tag_none.xml')

        result = generate_language_tag_report(idn, self.ref)

        self.assertCountEqual(result, [{
            'idn_table_language_tag': '-',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may be included in the comment'
            }, {
                'reference_lgr_language_tag': 'ja-hira',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may be included in the comment'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may be included in the comment'
            }]
        }])
