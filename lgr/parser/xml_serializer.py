# -*- coding: utf-8 -*-
"""
xml_serializer.py - Create an LGR XML compliant with RFC7940.
"""
from __future__ import unicode_literals

import logging
from lxml import etree

from lgr.char import Char, CharSequence, RangeChar
from lgr.utils import cp_to_str

logger = logging.getLogger(__name__)

LGR_NS = 'urn:ietf:params:xml:ns:lgr-1.0'
NSMAP = {None: LGR_NS}


def serialize_lgr(lgr):
    """
    Serialize an LGR structure to LXML structure.

    :param lgr: LGR structure.
    :returns: XML root element.
    """

    root = etree.Element('lgr', nsmap=NSMAP)

    meta = etree.SubElement(root, 'meta')
    data = etree.SubElement(root, 'data')
    rules = etree.SubElement(root, 'rules')

    _serialize_meta(lgr, meta)
    _serialize_data(lgr, data)
    _serialize_rules(lgr, rules)

    return root


def serialize_lgr_xml(lgr,
                      pretty_print=False,
                      encoding='utf-8',
                      xml_declaration=True):
    """
    Serialize the LGR into XML format.

    :param lgr: LGR structure
    :param pretty_print: If True, the output is prettyfied.
    :param encoding: Give the encoding of the output string.
    :param xml_declaration: If True, add the XML declaration.
    :return: XML string or bytes depending on encoding.
    """
    root = serialize_lgr(lgr)
    return etree.tostring(root,
                          pretty_print=pretty_print,
                          encoding=encoding,
                          xml_declaration=xml_declaration)


def _serialize_meta(lgr, meta):
    """
    Serialize meta-data to XML.

    :param lgr: The LGR structure to serialize.
    :param meta: Metadata root node.
    """
    metadata = lgr.metadata

    if metadata.version is not None:
        version_attributes = {}
        version_comment = metadata.version.comment
        if version_comment is not None:
            version_attributes['comment'] = version_comment
        version_node = etree.SubElement(meta, 'version',
                                        version_attributes)
        if metadata.version.value is not None:
            version_node.text = "{}".format(metadata.version.value)

    for elem in ['date', 'validity_start', 'validity_end', 'unicode_version']:
        value = getattr(metadata, elem, None)
        if value is not None:
            # Python prevents using '-' in attribute names
            node = etree.SubElement(meta, elem.replace('_', '-'))
            node.text = "{}".format(value)

    for language in metadata.languages:
        etree.SubElement(meta, 'language').text = language

    for scope in metadata.scopes:
        scope_attributes = {}
        scope_type = scope.scope_type
        if scope_type is not None:
            scope_attributes['type'] = scope_type
        etree.SubElement(meta, 'scope',
                         scope_attributes).text = scope.value

    if metadata.description is not None:
        node = etree.SubElement(meta, 'description')
        if metadata.description.description_type is not None:
            node.attrib['type'] = metadata.description.description_type

        content = metadata.description.value
        if metadata.description.description_type not in [None, 'text/plain']:
            # Wrap content in CDATA section
            content = etree.CDATA(content)
        node.text = content

    references = lgr.reference_manager
    if len(references) > 0:
        references_node = etree.SubElement(meta, 'references')
        for ref_id in references:
            ref = references[ref_id]
            ref_attributes = {
                'id': str(ref_id)
            }
            if len(ref.get('comment', "")) > 0:
                ref_attributes['comment'] = ref['comment']

            node = etree.SubElement(references_node,
                                    'reference',
                                    ref_attributes)
            node.text = ref['value']


def _serialize_data(lgr, data):
    """
    Serialize data to XML.

    :param lgr: The LGR structure to serialize.
    :param data: Data root node.
    """
    for char in lgr.repertoire:
        attributes = {}
        if char.comment is not None:
            attributes['comment'] = char.comment
        if char.when is not None:
            attributes['when'] = char.when
        if char.not_when is not None:
            attributes['not-when'] = char.not_when
        if len(char.references) > 0:
            attributes['ref'] = ' '.join(str(r) for r in char.references)
        if len(char.tags) > 0:
            attributes['tag'] = ' '.join(char.tags)
        if isinstance(char, RangeChar):
            tag = 'range'
            attributes['first-cp'] = cp_to_str(char.first_cp)
            attributes['last-cp'] = cp_to_str(char.last_cp)
        elif isinstance(char, Char) or isinstance(char, CharSequence):
            tag = 'char'
            attributes['cp'] = ' '.join('%04X' % c for c in char.cp)

        char_node = etree.SubElement(data, tag, **attributes)

        for variant in char.get_variants():
            variant_attributes = {}
            if variant.type is not None:
                variant_attributes['type'] = variant.type
            if variant.when is not None:
                variant_attributes['when'] = variant.when
            if variant.not_when is not None:
                variant_attributes['not-when'] = variant.not_when
            if variant.comment is not None:
                variant_attributes['comment'] = variant.comment
            if len(variant.references) > 0:
                variant_attributes['ref'] = ' '.join(str(r) for r
                                                     in variant.references)

            variant_attributes['cp'] = ' '.join(cp_to_str(c) for c in
                                                variant.cp)
            etree.SubElement(char_node, 'var', **variant_attributes)


def _serialize_rules(lgr, rules):
    """
    Serialize rules to XML.

    :param lgr: The LGR structure to serialize.
    :param rules: rules root node.
    """
    for cls in lgr.classes_xml:
        rules.append(etree.fromstring(cls))
    for rule in lgr.rules_xml:
        rules.append(etree.fromstring(rule))
    for action in lgr.actions_xml:
        rules.append(etree.fromstring(action))
