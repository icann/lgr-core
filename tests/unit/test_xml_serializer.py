# -*- coding: utf-8 -*-
"""
test_xml_serializer - Unit testing of XML serializer
"""
from __future__ import unicode_literals

import unittest

from lxml import etree

from lgr.core import LGR
from lgr.metadata import Metadata, Version, Scope, Description
from lgr.parser.xml_serializer import NSMAP, _serialize_meta


class TestXmlSerializer(unittest.TestCase):

    def setUp(self):
        self.lgr = LGR()
        self.root = etree.Element('lgr', nsmap=NSMAP)

    def test_serialize_meta(self):
        metadata = Metadata()
        metadata.version = Version('1.0', comment='First version')
        metadata.date = '2017-09-01'
        metadata.description = Description('The LGR description', description_type='text/plain')
        metadata.scopes = [Scope('.', scope_type='domain')]
        self.lgr.metadata = metadata

        meta_node = etree.SubElement(self.root, 'meta')

        _serialize_meta(self.lgr, meta_node)

        version = meta_node.find('version', namespaces=NSMAP)
        self.assertEqual(version.text, '1.0')
        # LXML can return strings as bytestring in python2...
        # See https://mailman-mail5.webfaction.com/pipermail/lxml/2011-December/006239.html
        self.assertEqual(u'' + version.get('comment'), 'First version')

        date = meta_node.find('date', namespaces=NSMAP)
        self.assertEqual(date.text, '2017-09-01')

        description = meta_node.find('description', namespaces=NSMAP)
        self.assertEqual(description.text, 'The LGR description')
        self.assertEqual(description.get('type'), 'text/plain')

        scopes = meta_node.findall('scope', namespaces=NSMAP)
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].text, '.')
        self.assertEqual(scopes[0].get('type'), 'domain')

    def test_serialize_meta_unicode(self):
        metadata = Metadata()
        metadata.version = Version('1.0 日本', comment='First version (はじめて)')
        metadata.description = Description('The LGR description containing Unicode characters: ΘΞΠ', description_type='text/plain')
        self.lgr.metadata = metadata

        meta_node = etree.SubElement(self.root, 'meta')

        _serialize_meta(self.lgr, meta_node)

        version = meta_node.find('version', namespaces=NSMAP)
        self.assertEqual(version.text, '1.0 日本')
        self.assertEqual(version.get('comment'), 'First version (はじめて)')

        description = meta_node.find('description', namespaces=NSMAP)
        self.assertEqual(description.text, 'The LGR description containing Unicode characters: ΘΞΠ')
        self.assertEqual(description.get('type'), 'text/plain')
