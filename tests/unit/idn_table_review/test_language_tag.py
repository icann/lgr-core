#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
test_variant_sets - 
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
            'idn_table_language_tag': 'ar',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MATCH',
                'remark': 'Exact match'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MATCH',
                'remark': 'The language tag in IDN Table relevant to the script tag in Reference LGR'
            }, {
                'reference_lgr_language_tag': 'zh-hani',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }]
        }, {
            'idn_table_language_tag': 'ar-arab',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MATCH',
                'remark': 'Consider minimizing the tag as per the RFC5646 and IANA subtag registry'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MATCH',
                'remark': 'The language tag in IDN Table relevant to the script tag in Reference LGR'
            }, {
                'reference_lgr_language_tag': 'zh-hani',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }]
        }, {
            'idn_table_language_tag': 'test-unexisting',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may have been included in the comment'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may have been included in the comment'
            }, {
                'reference_lgr_language_tag': 'zh-hani',
                'result': 'MANUAL CHECK',
                'remark': 'Language tag may have been included in the comment'
            }]
        }, {
            'idn_table_language_tag': 'zh',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'zh-hani',
                'result': 'MATCH',
                'remark': 'Language match'
            }]
        }, {
            'idn_table_language_tag': 'zh-hani',
            'comparison': [{
                'reference_lgr_language_tag': 'ar',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'und-Arab',
                'result': 'REVIEW',
                'remark': 'The language tag in IDN Table and Reference LGR are mismatched'
            }, {
                'reference_lgr_language_tag': 'zh-hani',
                'result': 'MATCH',
                'remark': 'Exact match'
            }]
        }])
