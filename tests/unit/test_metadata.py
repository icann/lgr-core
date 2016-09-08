# -*- coding: utf-8 -*-
"""
test_metadata.py - Unit testing of metadata module.
"""
from __future__ import unicode_literals

import unittest

from lgr.metadata import Metadata, ReferenceManager
from lgr.exceptions import (LGRFormatException,
                            ReferenceAlreadyExists,
                            ReferenceNotDefined)


class TestMetadata(unittest.TestCase):

    def setUp(self):
        self.metadata = Metadata()

    def test_get_scripts(self):
        self.metadata.languages = ['und-Cyrl', 'und-Zyyy', 'fr']
        self.assertEqual(self.metadata.get_scripts(),
                         ['Cyrl', 'Zyyy'])

    def test_add_language(self):
        self.metadata.add_language('fr')
        self.metadata.add_language('sr-Cyrl')
        self.metadata.add_language('zh-yue-HK')
        self.metadata.add_language('sr-Latn-RS')
        self.metadata.add_language('sl-nedis')
        self.metadata.add_language('de-CH-1901')
        self.metadata.add_language('hy-Latn-IT-arevela')
        self.metadata.add_language('es-419')
        self.assertEqual(self.metadata.languages,
                         ['fr', 'sr-Cyrl', 'zh-yue-HK',
                          'sr-Latn-RS', 'sl-nedis', 'de-CH-1901',
                          'hy-Latn-IT-arevela', 'es-419'])
        with self.assertRaises(LGRFormatException) as cm:
            self.metadata.add_language('de-419-DE')

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_LANGUAGE_TAG)

    def test_add_language_force(self):
        self.metadata.add_language('fr', force=True)
        self.metadata.add_language('de-419-DE', force=True)
        self.assertEqual(self.metadata.languages,
                         ['fr', 'de-419-DE'])

    def test_set_date(self):
        self.metadata.set_date('2015-06-25')
        self.assertEqual(self.metadata.date, '2015-06-25')

        with self.assertRaises(LGRFormatException) as cm:
            self.metadata.set_date('2012-13-14')

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_DATE_TAG)

    def test_set_date_force(self):
        self.metadata.set_date('2012-13-14', force=True)
        self.assertEqual(self.metadata.date, '2012-13-14')

    def test_set_validity_start(self):
        self.metadata.set_validity_start('2015-06-25')
        self.assertEqual(self.metadata.validity_start, '2015-06-25')

        with self.assertRaises(LGRFormatException) as cm:
            self.metadata.set_validity_start('2012-13-14')

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_DATE_TAG)

    def test_set_validity_start_force(self):
        self.metadata.set_validity_start('2012-13-14', force=True)
        self.assertEqual(self.metadata.validity_start, '2012-13-14')

    def test_set_validity_end(self):
        self.metadata.set_validity_end('2015-06-25')
        self.assertEqual(self.metadata.validity_end, '2015-06-25')

        with self.assertRaises(LGRFormatException) as cm:
            self.metadata.set_validity_end('2012-13-14')

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_DATE_TAG)

    def test_set_validity_end_force(self):
        self.metadata.set_validity_end('2012-13-14', force=True)
        self.assertEqual(self.metadata.validity_end, '2012-13-14')

    def test_set_unicode_version(self):
        self.metadata.set_unicode_version('6.3.0')
        self.assertEqual(self.metadata.unicode_version, '6.3.0')

        with self.assertRaises(LGRFormatException) as cm:
            self.metadata.set_unicode_version('a.b.c')

        the_exception = cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_UNICODE_VERSION_TAG)

    def test_set_unicode_version_force(self):
        self.metadata.set_unicode_version('a.b.c', force=True)
        self.assertEqual(self.metadata.unicode_version, 'a.b.c')


class TestReferenceManager(unittest.TestCase):

    def setUp(self):
        self.manager = ReferenceManager()

    def test_add_reference(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1',
                                            comment='A pretty old version')
        self.assertEqual('0', ref_id)
        self.assertIn('0', self.manager)

        reference = self.manager[ref_id]
        self.assertIsInstance(reference, dict)
        self.assertEqual('The Unicode Standard 1.1', reference['value'])
        self.assertEqual('A pretty old version', reference['comment'])

    def test_add_existing_reference(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1',
                                            comment='A pretty old version')
        self.assertEqual(ref_id, '0')
        self.assertRaises(ReferenceAlreadyExists,
                          self.manager.add_reference,
                          'The Unicode Standard 6.3', ref_id=ref_id)

    def test_add_existing_reference_other_type(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1',
                                            comment='A pretty old version')
        self.assertEqual(ref_id, '0')
        self.assertRaises(ReferenceAlreadyExists,
                          self.manager.add_reference,
                          'The Unicode Standard 6.3', ref_id=0)

    def test_del_existing_reference(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1',
                                            comment='A pretty old version')
        self.manager.del_reference(ref_id)
        self.assertEqual(0, len(self.manager))

    def test_del_inexisting_reference(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1',
                                            comment='A pretty old version')
        self.assertEqual(ref_id, '0')
        self.assertRaises(ReferenceNotDefined,
                          self.manager.del_reference, 1)
        self.assertRaises(ReferenceNotDefined,
                          self.manager.del_reference, '1')

    def test_update_reference(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1')

        self.manager.update_reference(ref_id, value='The Unicode Standard 1.2')
        self.assertEqual(self.manager[ref_id]['value'],
                         'The Unicode Standard 1.2')
        self.assertNotIn('comment', self.manager[ref_id])

        self.manager.update_reference(ref_id, comment='A recent version')
        self.assertEqual(self.manager[ref_id]['value'],
                         'The Unicode Standard 1.2')
        self.assertEqual(self.manager[ref_id]['comment'],
                         'A recent version')

    def test_update_inexsting_reference(self):
        ref_id = self.manager.add_reference('The Unicode Standard 1.1',
                                            comment='A pretty old version')
        self.assertEqual(ref_id, '0')
        self.assertRaises(ReferenceNotDefined,
                          self.manager.update_reference, 1,
                          **{'value': 'The Unicode Standard 1.2'})

if __name__ == '__main__':
    import logging
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
