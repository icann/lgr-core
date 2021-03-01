#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_variant_sets - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.classes import generate_classes_report
from munidata.database import IDNADatabase
from tests.unit.unicode_database_mock import UnicodeDatabaseMock
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_variant_sets')


class Test(TestCase):
    num_match = {
        'name': "num",
        'idn_members': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'ref_members': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'result': 'MATCH',
        'remark': 'Classes and their members are matched'
    }
    bc_match = {
        'name': "bc",
        'idn_members': ['b', 'c'],
        'ref_members': ['b', 'c'],
        'result': 'MATCH',
        'remark': 'Classes and their members are matched'
    }
    union_match = {
        'name': "union",
        'idn_members': ['b', 'c', 'g', 'h', 'i'],
        'ref_members': ['b', 'c', 'g', 'h', 'i'],
        'result': 'MATCH',
        'remark': 'Classes and their members are matched'
    }

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.unidb = IDNADatabase('6.3.0')
        self.unidb = UnicodeDatabaseMock()
        self.ref = load_lgr('idn_table_review', 'reference_lgr.xml', unidb=self.unidb)

    def test_classes_extra_members_in_ref_not_in_idn(self):
        idn = load_lgr('idn_table_review/classes', 'classes_extra_members_in_ref_not_in_idn.xml', unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [self.bc_match, self.num_match, {
            'name': "union",
            'idn_members': ['b', 'c', 'g'],
            'ref_members': ['b', 'c', 'g', 'h', 'i'],
            'result': 'SUBSET',
            'remark': 'Extra members in Ref. LGR not in IDN Table'
        }])

    def test_classes_mismatch_does_not_exist_in_ref(self):
        idn = load_lgr('idn_table_review/classes', 'classes_mismatch_does_not_exist_in_ref.xml', unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [self.bc_match, self.num_match, self.union_match, {
            'name': "idn-only",
            'idn_members': ['a', 'b', 'c'],
            'ref_members': [],
            'result': 'MANUAL CHECK',
            'remark': 'Mismatch class (class does not exist in ref. LGR; check for different class names)'
        }])

    def test_classes_mismatch_does_not_exist_in_idn(self):
        idn = load_lgr('idn_table_review/classes', 'classes_mismatch_does_not_exist_in_idn.xml', unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [self.bc_match, self.num_match, {
            'name': "union",
            'idn_members': [],
            'ref_members': ['b', 'c', 'g', 'h', 'i'],
            'result': 'MANUAL CHECK',
            'remark': 'Mismatch class (class does not exist in IDN Table; check for different class names)'
        }])

    def test_classes_mismatch_missing_members_in_idn(self):
        idn = load_lgr('idn_table_review/classes', 'classes_mismatch_missing_members_in_idn.xml', unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [self.bc_match, self.num_match, {
            'name': "union",
            'idn_members': ['b', 'c', 'g', 'h'],
            'ref_members': ['b', 'c', 'g', 'h', 'i'],
            'result': 'REVIEW',
            'remark': 'Mismatch class members (missing member(s) in IDN Table)'
        }])

    def test_classes_mismatch_extra_members_idn_in_ref(self):
        idn = load_lgr('idn_table_review/classes', 'classes_mismatch_extra_members_idn_in_ref.xml', unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [{
            'name': "bc",
            'idn_members': ['b', 'c', 'd', 'e'],
            'ref_members': ['b', 'c'],
            'result': 'REVIEW',
            'remark': 'Mismatch class members (extra member(s) in IDN Table)'
        }, self.num_match, {
            'name': "union",
            'idn_members': ['b', 'c', 'd', 'e', 'g', 'h', 'i'],
            'ref_members': ['b', 'c', 'g', 'h', 'i'],
            'result': 'REVIEW',
            'remark': 'Mismatch class members (extra member(s) in IDN Table)'
        }])

    def test_classes_mismatch_extra_members_idn_not_in_ref(self):
        idn = load_lgr('idn_table_review/classes', 'classes_mismatch_extra_members_idn_not_in_ref.xml',
                       unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [{
            'name': "bc",
            'idn_members': ['b', 'c', 'j'],
            'ref_members': ['b', 'c'],
            'result': 'MANUAL CHECK',
            'remark': 'Mismatch class members (extra member(s) in IDN Table which are not in Ref. LGR repertoire)'
        }, self.num_match, {
            'name': "union",
            'idn_members': ['b', 'c', 'g', 'h', 'i', 'j'],
            'ref_members': ['b', 'c', 'g', 'h', 'i'],
            'result': 'MANUAL CHECK',
            'remark': 'Mismatch class members (extra member(s) in IDN Table which are not in Ref. LGR repertoire)'
        }])

    def test_classes_mismatch_additional_code_points(self):
        idn = load_lgr('idn_table_review/classes', 'classes_mismatch_additional_code_points.xml', unidb=self.unidb)

        result = generate_classes_report(idn, self.ref)

        self.assertCountEqual(result, [self.bc_match, self.num_match, self.union_match, {
            'name': "additional",
            'idn_members': ['j', 'k', 'l', 'm', 'n', 'o', 'p'],
            'ref_members': [],
            'result': 'MANUAL CHECK',
            'remark': 'Mismatch class with only additional code points.'
        }])
