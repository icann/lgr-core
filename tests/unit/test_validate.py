# -*- coding: utf-8 -*-
"""
test_validate.py - Unit testing of LGR validation module.
"""
from __future__ import unicode_literals

import logging

import unittest

import os
from io import StringIO

from munidata.database import IDNADatabase

from lgr.core import LGR
from lgr.char import RangeChar, CharSequence
from lgr.rule import Rule
from lgr.exceptions import CharInvalidIdnaProperty

from lgr.validate.xml_validity import check_xml_validity
from lgr.validate.symmetry import check_symmetry
from lgr.validate.lgr_stats import compute_stats
from lgr.validate.rebuild_lgr import rebuild_lgr
from lgr.validate.transitivity import check_transitivity
from lgr.validate.conditional_variants import check_conditional_variants


RESOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inputs')


class TestSymmetry(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.DEBUG)
        logging.getLogger('lgr.validate').addHandler(ch)

    def test_empty_lgr(self):
        success, result = check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing symmetry',
                                      'repertoire': []})

    def test_no_symmetric_in_repertoire(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        success, result = check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         "CP U+0061: Variant U+0062 is not in repertoire.\n")
        self.assertFalse(success)
        self.assertDictEqual(result, {'description': 'Testing symmetry',
                                      'repertoire': [{'char': self.lgr.get_char([0x0061]),
                                                      'variant': self.lgr.get_variant([0x0061], (0x0062, ))[0],
                                                      'type': 'not-in-repertoire'}]})

    def test_no_symmetric_in_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        success, result = check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         'CP U+0062 should have CP U+0061 in its variants.\n')
        self.assertFalse(success)
        self.assertDictEqual(result, {'description': 'Testing symmetry',
                                      'repertoire': [{'char': self.lgr.get_variant([0x0061], (0x0062, ))[0],
                                                      'variant': self.lgr.get_char([0x0061]),
                                                      'type': 'missing'}]})

    def test_symmetry_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0061])
        success, result = check_symmetry(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing symmetry',
                                      'repertoire': []})


class TestTransitivity(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.DEBUG)
        logging.getLogger('lgr.validate').addHandler(ch)

    def test_empty_lgr(self):
        success, result = check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing transitivity',
                                      'repertoire': []})

    def test_no_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        success, result = check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing transitivity',
                                      'repertoire': []})

    def test_no_transitivity(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0063])
        self.lgr.add_cp([0x0063])
        success, result = check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         'CP U+0061 should have CP U+0063 in its variants.\n')
        self.assertFalse(success)
        self.assertDictEqual(result, {'description': 'Testing transitivity',
                                      'repertoire': [{'char': self.lgr.get_char([0x0061]),
                                                      'variant': self.lgr.get_variant([0x0062], (0x0063, ))[0]}]})

    def test_transitivity_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062])
        self.lgr.add_variant([0x0061], [0x0063])
        self.lgr.add_cp([0x0062])
        self.lgr.add_variant([0x0062], [0x0063])
        self.lgr.add_cp([0x0063])
        success, result = check_transitivity(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing transitivity',
                                      'repertoire': []})


class TestConditionalVariants(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        # Configure log system to redirect validation logs to local attribute
        self.log_output = StringIO()
        ch = logging.StreamHandler(self.log_output)
        ch.setLevel(logging.DEBUG)
        logging.getLogger('lgr.validate').addHandler(ch)

    def test_empty_lgr(self):
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': []})

    def test_no_variants(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_cp([0x0062])
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': []})

    def test_no_rule_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when="when-rule")
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         "CP U+0061: Variant 'U+0062' \"when\" attribute "
                         "'when-rule' is not an existing rule name.\n")
        self.assertFalse(success)
        var = self.lgr.get_variant([0x0061], (0x0062, ))[0]
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': [{'char': self.lgr.get_char([0x0061]),
                                                      'variant': var,
                                                      'rule_type': 'when',
                                                      'rule': var.when}]})

    def test_no_rule_not_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], not_when="not-when-rule")
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         "CP U+0061: Variant 'U+0062' \"not-when\" attribute "
                         "'not-when-rule' is not an existing rule name.\n")
        self.assertFalse(success)
        var = self.lgr.get_variant([0x0061], (0x0062, ))[0]
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': [{'char': self.lgr.get_char([0x0061]),
                                                      'variant': var,
                                                      'rule_type': 'not-when',
                                                      'rule': var.not_when}]})

    def test_no_rule_when_not_when(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when="when-rule", not_when="not-when-rule", force=True)
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertGreater(len(log_content), 0)
        self.assertEqual(log_content,
                         "CP U+0061: Variant 'U+0062' \"when\" attribute "
                         "'when-rule' is not an existing rule name.\n"
                         "CP U+0061: Variant 'U+0062' \"not-when\" attribute "
                         "'not-when-rule' is not an existing rule name.\n")
        self.assertFalse(success)
        var = self.lgr.get_variant([0x0061], (0x0062, ))[0]
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': [{'char': self.lgr.get_char([0x0061]),
                                                      'variant': var,
                                                      'rule_type': 'when',
                                                      'rule': var.when},
                                                     {'char': self.lgr.get_char([0x0061]),
                                                      'variant': var,
                                                      'rule_type': 'not-when',
                                                      'rule': var.not_when}
                                                     ]})

    def test_conditional_when_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], when="when-rule")
        self.lgr.rules.append("when-rule")
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': []})

    def test_conditional_not_when_ok(self):
        self.lgr.add_cp([0x0061])
        self.lgr.add_variant([0x0061], [0x0062], not_when="not-when-rule")
        self.lgr.rules.append("not-when-rule")
        success, result = check_conditional_variants(self.lgr, {})
        log_content = self.log_output.getvalue()
        self.assertEqual(len(log_content), 0)
        self.assertTrue(success)
        self.assertDictEqual(result, {'description': 'Testing conditional variants',
                                      'repertoire': []})


class TestRebuildLGR(unittest.TestCase):

    DEFAULT_UNICODE_VERSION = '6.3.0'

    def setUp(self):
        self.lgr = LGR()

    def test_empty_lgr(self):
        __, result = rebuild_lgr(self.lgr, {})
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                        self.DEFAULT_UNICODE_VERSION),
                                      'repertoire': {}})

    def test_lgr_non_default_unicode(self):
        self.lgr.metadata.set_unicode_version('6.2.0')
        __, result = rebuild_lgr(self.lgr, {})
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version 6.2.0',
                                      'repertoire': {}})

    def test_lgr_validating_repertoire(self):
        validating_repertoire = LGR(name='validating')
        __, result = rebuild_lgr(self.lgr, {'validating_repertoire': validating_repertoire})
        self.assertDictEqual(result, {'description': "Rebuilding LGR with Unicode version {} "
                                                     "and validating repertoire '{}'".format(
                                                                self.DEFAULT_UNICODE_VERSION, validating_repertoire),
                                      'repertoire': {}})

    def test_lgr_unidb_same_unicode(self):
        unidb = IDNADatabase('6.3.0')
        __, result = rebuild_lgr(self.lgr, {'unidb': unidb})
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                    self.DEFAULT_UNICODE_VERSION),
                                      'repertoire': {}})

    def test_lgr_unidb_different_unicode(self):
        unidb = IDNADatabase('6.2.0')
        __, result = rebuild_lgr(self.lgr, {'unidb': unidb})
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                    self.DEFAULT_UNICODE_VERSION),
                                      'generic': "Target Unicode version {} differs from UnicodeDatabase {}".format(
                                                                                    self.DEFAULT_UNICODE_VERSION,
                                                                                    '6.2.0'),
                                      'repertoire': {}})

    def test_lgr_wrong_range_char(self):
        self.lgr.add_range(0x0060, 0x0063, force=True)
        r = RangeChar(0x0060, 0x0060, 0x0063)
        unidb = IDNADatabase(self.DEFAULT_UNICODE_VERSION)
        self.lgr.unicode_database = unidb
        _, result = rebuild_lgr(self.lgr, {'unidb': unidb})
        errors = result.get('repertoire', {}).get(r, {'errors': []})['errors']
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], CharInvalidIdnaProperty)
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                    self.DEFAULT_UNICODE_VERSION),
                                      'repertoire': {r: {'errors': errors}}})

    def test_lgr_wrong_char(self):
        self.lgr.add_cp(0x0060)
        char = self.lgr.get_char([0x0060])
        unidb = IDNADatabase(self.DEFAULT_UNICODE_VERSION)
        self.lgr.unicode_database = unidb
        _, result = rebuild_lgr(self.lgr, {'unidb': unidb})
        errors = result.get('repertoire', {}).get(char, {'errors': []})['errors']
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], CharInvalidIdnaProperty)
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                    self.DEFAULT_UNICODE_VERSION),
                                      'repertoire': {char: {'errors': errors}}})

    def test_lgr_wrong_variant(self):
        self.lgr.add_cp(0x0061)
        self.lgr.add_variant(0x0061, 0x0060)
        char = self.lgr.get_char([0x0061])
        var = char.get_variant((0x0060, ))[0]
        unidb = IDNADatabase(self.DEFAULT_UNICODE_VERSION)
        self.lgr.unicode_database = unidb
        _, result = rebuild_lgr(self.lgr, {'unidb': unidb})
        errors = result.get('repertoire', {}).get(char, {}).get('variants', {}).get(var, [])
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], CharInvalidIdnaProperty)
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                    self.DEFAULT_UNICODE_VERSION),
                                      'repertoire': {char: {'variants': {var: errors}}}})

    def test_lgr_ok(self):
        self.lgr.add_range(0x0061, 0x0063, force=True)
        self.lgr.add_cp(0x0064)
        self.lgr.add_cp(0x0065)
        self.lgr.add_variant(0x0064, 0x0065)
        self.lgr.add_variant(0x0065, 0x0064)
        unidb = IDNADatabase(self.DEFAULT_UNICODE_VERSION)
        self.lgr.unicode_database = unidb
        _, result = rebuild_lgr(self.lgr, {'unidb': unidb})
        self.assertDictEqual(result, {'description': 'Rebuilding LGR with Unicode version {}'.format(
                                                                                        self.DEFAULT_UNICODE_VERSION),
                                      'repertoire': {}})


class TestXmlValidity(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()

    def test_no_validation(self):
        success, result = check_xml_validity(self.lgr, {})
        self.assertTrue(success)
        self.assertDictEqual(result, {})

    def test_invalid_xml_lgr(self):
        self.lgr.add_cp(0x0061, when='#when')
        success, result = check_xml_validity(self.lgr, {'rng_filepath': os.path.join(RESOURCE_DIR, 'lgr.rng')})
        self.assertIn('validation_result', result)
        validation_result = result['validation_result']
        self.assertFalse(success)
        self.assertDictEqual(result, {'description': 'Testing XML validity using RNG',
                                      'rng_result': False,
                                      'validation_result': validation_result})


class TestStats(unittest.TestCase):

    STATS = {
        'codepoint_number': 0,

        'range_number': 0,
        'largest_range': None,
        'largest_range_len': 0,

        'sequence_number': 0,
        'largest_sequence': None,
        'largest_sequence_len': 0,

        'codepoints_with_variants': 0,
        'mapping_number': 0,
        'variants_by_type': {},
        'largest_variant_set': 0,

        'average_variants': 0,

        'codepoints_by_tag': {},

        'rule_number': 0
    }

    def setUp(self):
        self.lgr = LGR()

    def test_empty_lgr(self):
        __, result = compute_stats(self.lgr, {})
        self.assertDictEqual(result, {'description': 'Generate stats',
                                      'stats': self.STATS})

    def test_lgr_chars(self):
        self.lgr.add_cp(0x0061)
        self.lgr.add_cp(0x0062, tag=['test'])
        __, result = compute_stats(self.lgr, {})
        stats = self.STATS.copy()
        stats['codepoint_number'] = 2
        stats['codepoints_by_tag'] = {'test': 1}
        self.assertDictEqual(result, {'description': 'Generate stats',
                                      'stats': stats})

    def test_lgr_ranges(self):
        self.lgr.add_range(0x0061, 0x0065)
        self.lgr.add_range(0x0066, 0x0068)
        __, result = compute_stats(self.lgr, {})
        stats = self.STATS.copy()
        stats['codepoint_number'] = 8
        stats['range_number'] = 2
        stats['largest_range'] = RangeChar(0x0061, 0x0061, 0x0065)
        stats['largest_range_len'] = 5
        self.assertDictEqual(result, {'description': 'Generate stats',
                                      'stats': stats})

    def test_lgr_sequence(self):
        self.lgr.add_cp([0x0061, 0x0062, 0x0063])
        self.lgr.add_cp([0x0061, 0x0062])
        __, result = compute_stats(self.lgr, {})
        stats = self.STATS.copy()
        stats['codepoint_number'] = 2
        stats['sequence_number'] = 2
        stats['largest_sequence'] = CharSequence(cp_or_sequence=(0x0061, 0x0062, 0x0063))
        stats['largest_sequence_len'] = 3
        self.assertDictEqual(result, {'description': 'Generate stats',
                                      'stats': stats})

    def test_lgr_variants(self):
        self.lgr.add_cp(0x0061)
        self.lgr.add_cp(0x0062)
        self.lgr.add_cp(0x0063)
        self.lgr.add_variant(0x0061, 0x0062)
        self.lgr.add_variant(0x0061, 0x0063)
        self.lgr.add_variant(0x0062, 0x0061)
        self.lgr.add_variant(0x0063, 0x0061, variant_type='blocked')
        __, result = compute_stats(self.lgr, {})
        stats = self.STATS.copy()
        stats['codepoint_number'] = 3
        stats['codepoints_with_variants'] = 3
        stats['mapping_number'] = 4
        stats['variants_by_type'] = {None: 3, 'blocked': 1}
        stats['largest_variant_set'] = 3
        stats['average_variants'] = round(4 / 3, 1)
        self.assertDictEqual(result, {'description': 'Generate stats',
                                      'stats': stats})

    def test_lgr_rules(self):
        rule1 = Rule(name='rule1')
        rule2 = Rule(name='rule2')
        self.lgr.add_rule(rule1)
        self.lgr.add_rule(rule2)
        __, result = compute_stats(self.lgr, {})
        stats = self.STATS.copy()
        stats['rule_number'] = 2
        self.assertDictEqual(result, {'description': 'Generate stats',
                                      'stats': stats})


if __name__ == '__main__':
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
