#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
test_actions - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.actions import generate_actions_report
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_actions')


class Test(TestCase):
    ref = load_lgr('idn_table_review', 'reference_lgr.xml')
    matching_actions = [{
        'name': '<Action: 0>',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (action name and content are the same)'
    }, {
        'name': '<Action: 1>',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (action name and content are the same)'
    }, {
        'name': '<Action: 2>',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (action name and content are the same)'
    }, {
        'name': '<Action: 3>',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (action name and content are the same)'
    }, {
        'name': '<Action: 4>',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Exact Match (action name and content are the same)'
    }]

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def test_generate_actions_report_match(self):
        idn = load_lgr('idn_table_review/actions', 'actions_match.xml')

        result = generate_actions_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': self.matching_actions,
            'sequence': 'MATCH'
        })

    def test_generate_actions_report_missing(self):
        idn = load_lgr('idn_table_review/actions', 'actions_missing.xml')

        result = generate_actions_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': [{
                'name': '<Action: 0>',
                'idn_table': True,
                'reference_lgr': True,
                'result': 'MATCH',
                'remark': 'Exact Match (action name and content are the same)'
            }, {
                'name': '<Action: 1>',
                'idn_table': True,
                'reference_lgr': True,
                'result': 'MATCH',
                'remark': 'Exact Match (action name and content are the same)'
            }, {
                'name': '<Action: 2>',
                'idn_table': True,
                'reference_lgr': True,
                'result': 'MATCH',
                'remark': 'Exact Match (action name and content are the same)'
            }, {
                'name': '<Action: 3>',
                'idn_table': True,
                'reference_lgr': True,
                'result': 'MATCH',
                'remark': 'Exact Match (action name and content are the same)'
            }, {
                'name': '<Action: 1>',
                'idn_table': False,
                'reference_lgr': True,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (missing action)'
            }],
            'sequence': 'MATCH'
        })

    def test_generate_actions_report_additional(self):
        idn = load_lgr('idn_table_review/actions', 'actions_additional.xml')

        result = generate_actions_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': self.matching_actions + [{
                'name': '<Action: additional>',
                'idn_table': True,
                'reference_lgr': False,
                'result': 'MANUAL CHECK',
                'remark': 'Mismatch (additional action)'
            }],
            'sequence': 'MATCH'
        })

    def test_generate_actions_report_sequence_mismatch(self):
        idn = load_lgr('idn_table_review/actions', 'actions_sequence_mismatch.xml')

        result = generate_actions_report(idn, self.ref)

        self.assertDictEqual(result, {
            'comparison': self.matching_actions,
            'sequence': 'MANUAL CHECK'
        })
