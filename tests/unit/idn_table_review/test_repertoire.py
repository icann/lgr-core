#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_variant_sets - 
"""
import logging
from unittest import TestCase

from lgr.tools.idn_review.repertoire import generate_repertoire_report
from tests.unit.unicode_database_mock import UnicodeDatabaseMock
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_variant_sets')


class Test(TestCase):
    matching_cp = [{
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
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (100,),
        'glyph': 'd',
        'name': 'LATIN SMALL LETTER D',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (101,),
        'glyph': 'e',
        'name': 'LATIN SMALL LETTER E',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (102,),
        'glyph': 'f',
        'name': 'LATIN SMALL LETTER F',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (103,),
        'glyph': 'g',
        'name': 'LATIN SMALL LETTER G',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (104,),
        'glyph': 'h',
        'name': 'LATIN SMALL LETTER H',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (105,),
        'glyph': 'i',
        'name': 'LATIN SMALL LETTER I',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (48,),
        'glyph': '0',
        'name': 'DIGIT ZERO',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (49,),
        'glyph': '1',
        'name': 'DIGIT ONE',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (50,),
        'glyph': '2',
        'name': 'DIGIT TWO',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (51,),
        'glyph': '3',
        'name': 'DIGIT THREE',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (52,),
        'glyph': '4',
        'name': 'DIGIT FOUR',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (53,),
        'glyph': '5',
        'name': 'DIGIT FIVE',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (54,),
        'glyph': '6',
        'name': 'DIGIT SIX',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (55,),
        'glyph': '7',
        'name': 'DIGIT SEVEN',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (56,),
        'glyph': '8',
        'name': 'DIGIT EIGHT',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (57,),
        'glyph': '9',
        'name': 'DIGIT NINE',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (339,),
        'glyph': 'œ',
        'name': 'LATIN SMALL LIGATURE OE',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }, {
        'cp': (111, 101),
        'glyph': 'oe',
        'name': 'LATIN SMALL LETTER O LATIN SMALL LETTER E',
        'idn_table': True,
        'reference_lgr': True,
        'result': 'MATCH',
        'remark': 'Matches code point (including tags, context rule)'
    }]

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.unidb = UnicodeDatabaseMock()
        self.ref = load_lgr('idn_table_review', 'reference_lgr.xml', unidb=self.unidb)

    def test_repertoire_missing_in_lgr(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_missing_in_lgr.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp + [{
            'cp': (106,),
            'glyph': 'j',
            'name': 'LATIN SMALL LETTER J',
            'idn_table': True,
            'reference_lgr': False,
            'result': 'MANUAL CHECK',
            'remark': 'The code point only exists in the IDN Table but not in the reference LGR'
        }], key=lambda x: x['cp']))

    def test_repertoire_note_rule(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_note_rule.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:3] + self.matching_cp[4:] + [{
            'cp': (100,),
            'glyph': 'd',
            'name': 'LATIN SMALL LETTER D',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'NOTE',
            'remark': 'Rules not required in Reference LGR'
        }], key=lambda x: x['cp']))

    def test_repertoire_note_tag(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_note_tag.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:2] + self.matching_cp[3:] + [{
            'cp': (99,),
            'glyph': 'c',
            'name': 'LATIN SMALL LETTER C',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'NOTE',
            'remark': 'Tags not required in Reference LGR'
        }], key=lambda x: x['cp']))

    def test_repertoire_notes(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_notes.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:3] + self.matching_cp[4:] + [{
            'cp': (100,),
            'glyph': 'd',
            'name': 'LATIN SMALL LETTER D',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'NOTE',
            'remark': 'Tags not required in Reference LGR\nRules not required in Reference LGR'
        }], key=lambda x: x['cp']))

    def test_repertoire_review_rules(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_review_rules.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:2] + self.matching_cp[3:] + [{
            'cp': (99,),
            'glyph': 'c',
            'name': 'LATIN SMALL LETTER C',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'REVIEW',
            'remark': 'Rules do not match'
        }], key=lambda x: x['cp']))

    def test_repertoire_review_tag_missing(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_review_tag_missing.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:9] + self.matching_cp[10:] + [{
            'cp': (48,),
            'glyph': '0',
            'name': 'DIGIT ZERO',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'REVIEW',
            'remark': 'Tags do not match'
        }], key=lambda x: x['cp']))

    def test_repertoire_review_tag(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_review_tag.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:8] + self.matching_cp[9:] + [{
            'cp': (105,),
            'glyph': 'i',
            'name': 'LATIN SMALL LETTER I',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'REVIEW',
            'remark': 'Tags do not match'
        }], key=lambda x: x['cp']))

    def test_repertoire_reviews_and_note(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_reviews_and_note.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:9] + self.matching_cp[10:] + [{
            'cp': (48,),
            'glyph': '0',
            'name': 'DIGIT ZERO',
            'idn_table': True,
            'reference_lgr': True,
            'result': 'REVIEW',
            'remark': 'Tags do not match\nRules do not match'
        }], key=lambda x: x['cp']))

    def test_repertoire_subset(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_subset.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp[:3] + self.matching_cp[4:] + [{
            'cp': (100,),
            'glyph': 'd',
            'name': 'LATIN SMALL LETTER D',
            'idn_table': False,
            'reference_lgr': True,
            'result': 'SUBSET',
            'remark': 'Match as a subset of repertoire'
        }], key=lambda x: x['cp']))

    def test_repertoire_ignore_script_tag(self):
        idn = load_lgr('idn_table_review/repertoire', 'repertoire_script_tag.xml', unidb=self.unidb)

        result = generate_repertoire_report(idn, self.ref)

        self.assertCountEqual(result, sorted(self.matching_cp, key=lambda x: x['cp']))
