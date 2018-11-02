# -*- coding: utf-8 -*-
"""
xml_parser.py - Parse a XML document, as described by RFC7940.

Note:
    - Validation of input XML and actual parsing have been split into two
      functions.The idea here is that the validation of an XML LGR file is
      a one-time operation, and can take a bit of time, whereas parsing of LGR
      XML files can be done quite frequently by users, so it has to be a bit
      more performant.
"""

import logging
from lxml import etree

from lgr import text_type
from lgr.core import LGR
from lgr.metadata import (Metadata,
                          ReferenceManager,
                          Scope,
                          Description,
                          Version)
from lgr.rule import Rule
from lgr.action import Action
from lgr.matcher import (AnchorMatcher,
                         AnyMatcher,
                         CharMatcher,
                         ChoiceMatcher,
                         ClassMatcher,
                         EndMatcher,
                         LookAheadMatcher,
                         LookBehindMatcher,
                         RuleMatcher,
                         StartMatcher)
from lgr.classes import (Class,
                         ComplementClass,
                         UnionClass,
                         IntersectionClass,
                         DifferenceClass,
                         SymmetricDifferenceClass)
from lgr.exceptions import (LGRException,
                            LGRFormatTestResults)
from lgr.utils import format_cp
from lgr.parser.parser import LGRParser

logger = logging.getLogger(__name__)

LGR_NS = 'urn:ietf:params:xml:ns:lgr-1.0'

# Most python XML libs do not cope well with NS,
# so define fully-qualified tag names here
META_TAG = '{%s}meta' % LGR_NS

# <meta> elements
VERSION_TAG = '{%s}version' % LGR_NS
DATE_TAG = '{%s}date' % LGR_NS
LANGUAGE_TAG = '{%s}language' % LGR_NS
SCOPE_TAG = '{%s}scope' % LGR_NS
VALIDITY_START_TAG = '{%s}validity-start' % LGR_NS
VALIDITY_END_TAG = '{%s}validity-end' % LGR_NS
UNICODE_VERSION_TAG = '{%s}unicode-version' % LGR_NS
DESCRIPTION_TAG = '{%s}description' % LGR_NS
REFERENCES_TAG = '{%s}references' % LGR_NS

DATA_TAG = '{%s}data' % LGR_NS

# <data> elements
CHAR_TAG = '{%s}char' % LGR_NS
RANGE_TAG = '{%s}range' % LGR_NS
VARIANT_TAG = '{%s}var' % LGR_NS

RULES_TAG = '{%s}rules' % LGR_NS

# <rules> elements
RULE_TAG = '{%s}rule' % LGR_NS
ACTION_TAG = '{%s}action' % LGR_NS
CLASS_TAG = '{%s}class' % LGR_NS

# Matchers
ANCHOR_TAG = '{%s}anchor' % LGR_NS
ANY_TAG = '{%s}any' % LGR_NS
CHOICE_TAG = '{%s}choice' % LGR_NS
END_TAG = '{%s}end' % LGR_NS
LOOKAHEAD_TAG = '{%s}look-ahead' % LGR_NS
LOOKBEHIND_TAG = '{%s}look-behind' % LGR_NS
START_TAG = '{%s}start' % LGR_NS

# Classes
COMPLEMENT_TAG = '{%s}complement' % LGR_NS
UNION_TAG = '{%s}union' % LGR_NS
INTERSECTION_TAG = '{%s}intersection' % LGR_NS
DIFFERENCE_TAG = '{%s}difference' % LGR_NS
SYM_DIFFERENCE_TAG = '{%s}symmetric-difference' % LGR_NS

# List of tags referring to combinator classes
COMBINATOR_TAGS = (COMPLEMENT_TAG, UNION_TAG, INTERSECTION_TAG,
                   DIFFERENCE_TAG, SYM_DIFFERENCE_TAG)


class XMLParser(LGRParser):
    # Keep content intact, so do not strip CDATA section
    # (used in the <meta>/<description> element).
    # Do not resolve entities.
    # Skip comment, as we do not care.
    PARSER_OPTIONS = {'resolve_entities': False,
                      'strip_cdata': False,
                      'remove_comments': True}

    def __init__(self, *args, **kwargs):
        if 'force_mode' in kwargs:
            force_mode = kwargs['force_mode']
            del kwargs['force_mode']
        else:
            force_mode = True

        super(XMLParser, self).__init__(*args, **kwargs)
        self.force_mode = force_mode
        self.rfc7940_checks = LGRFormatTestResults()

    def validate_document(self, rng_schema_path):
        # Construct the RelaxNG validator
        schema = etree.RelaxNG(file=rng_schema_path)

        # Parse the XML file
        parser = etree.XMLParser(**self.PARSER_OPTIONS)
        doc = etree.parse(self.source, parser=parser)

        logger.debug("Validating document '%s' with RNG '%s'",
                     self.source, rng_schema_path)

        error_log = None
        if not schema.validate(doc):
            logger.warning("Validation of document '%s' failed",
                           self.source)
            self.rfc7940_checks.error('schema')
            error_log = schema.error_log
            if len(error_log) == 0:
                # Bug in LXML, see https://bugs.launchpad.net/lxml/+bug/1526522
                error_log = "CANNOT VALIDATE XML"

        self.rfc7940_checks.tested('schema')
        return error_log

    def unicode_version(self):
        logger.debug("Get unicode version from meta")
        # Only parse the "meta" element
        # Skip comment, as we do not care.
        context = etree.iterparse(self.source,
                                  tag=META_TAG,
                                  **self.PARSER_OPTIONS)
        self._fast_iter(context)
        unicode_version = self._lgr.metadata.unicode_version
        self._lgr = None

        # FD is now potentially at the end of the documents,
        # set it back to start
        if hasattr(self.source, "seek"):
            self.source.seek(0)
        return unicode_version

    def parse_document(self):
        logger.debug('Start parsing of file: %s', self.filename)

        # Keep content intact, so do not strip CDATA section
        # (used in the <meta>/<description> element).
        # Do not resolve entities.
        # Skip comment, as we do not care.
        context = etree.iterparse(self.source, **self.PARSER_OPTIONS)

        self._fast_iter(context)

        # FD is now potentially at the end of the documents,
        # set it back to start
        if hasattr(self.source, "seek"):
            self.source.seek(0)

        self.rfc7940_checks.tested('parse_xml')
        return self._lgr

    def _process_meta(self, elem):
        """
        Process the <meta> element of an LGR XML file.
        """
        metadata = Metadata(self.rfc7940_checks)
        reference_manager = ReferenceManager()
        MAPPER = {
            DATE_TAG: lambda d: metadata.set_date(d,
                                                  force=self.force_mode),
            VALIDITY_START_TAG: lambda d: metadata.set_validity_start(d,
                                                                      force=self.force_mode),
            VALIDITY_END_TAG: lambda d: metadata.set_validity_end(d,
                                                                  force=self.force_mode),
            UNICODE_VERSION_TAG: lambda d: metadata.set_unicode_version(d,
                                                                        force=self.force_mode),
        }
        unicode_version_tag_found = False
        for child in elem:
            tag = child.tag
            logger.debug("Got '%s' element", tag)
            if tag in MAPPER:
                MAPPER[tag](child.text)
                if tag == UNICODE_VERSION_TAG:
                    unicode_version_tag_found = True
            elif tag == VERSION_TAG:
                metadata.version = Version(child.text,
                                           child.get('comment', None))
            elif tag == LANGUAGE_TAG:
                metadata.add_language(child.text, force=self.force_mode)
            elif tag == SCOPE_TAG:
                metadata.scopes.append(
                    Scope(child.text, child.get('type', None)))
            elif tag == DESCRIPTION_TAG:
                # Seems to be an issue with CDATA/iterparse: https://bugs.launchpad.net/lxml/+bug/1788449
                # For now, manually replace CRLF with LF
                metadata.description = Description(child.text.replace('\r\n', '\n'),
                                                   child.get('type',
                                                             None))
            elif tag == REFERENCES_TAG:
                for reference in child:
                    value = reference.text
                    # Don't convert it to an int since ref_id may be a string
                    ref_id = reference.get('id')
                    comment = reference.get('comment', None)
                    reference_manager.add_reference(value,
                                                    comment=comment,
                                                    ref_id=ref_id)
                # Since we have processed <reference> elements here, let's clean-up
                child.clear()
            else:
                logger.warning("Unhandled '%s' element in <meta> section",
                               tag)
                self.rfc7940_checks.error('parse_xml')
            child.clear()

        self.rfc7940_checks.add_test_result('explicit_unicode_version',
                                            unicode_version_tag_found)
        self._lgr = LGR(name=self.filename,
                        metadata=metadata,
                        reference_manager=reference_manager,
                        unicode_database=self._unicode_database)

    def _process_data(self, elem):
        """
        Process the <data> element of an LGR XML file.
        """

        # It is RECOMMENDED to list all "char" elements in ascending order of
        # the "cp" attribute. The below variable is used when verifying that.
        previous_codepoint = []

        for child in elem:
            comment = child.get('comment', None)
            when = child.get('when', None)
            not_when = child.get('not-when', None)

            # Handle references
            ref = string_to_list(child.get('ref', ''))

            # Handle tags
            tag = string_to_list(child.get('tag', ''))

            if child.tag == CHAR_TAG:
                codepoint = [int(c, 16) for c in child.get('cp').split()]

                if codepoint <= previous_codepoint:
                    if previous_codepoint[0:len(codepoint)] == codepoint:
                        # Not clear what order is to be recommended here
                        self.rfc7940_checks.error('char_strict_ascending_order')
                    else:
                        logger.warning("cp attribute not in ascending order: '%s'",
                                       child.get('cp'))
                        self.rfc7940_checks.error('char_ascending_order')
                previous_codepoint = codepoint

                try:
                    self._lgr.add_cp(codepoint, comment=comment,
                                     ref=ref, tag=tag,
                                     when=when, not_when=not_when,
                                     force=self.force_mode)
                except LGRException as exc:
                    logger.error("Cannot add code point '%s': %s",
                                 format_cp(codepoint), exc)
                    self.rfc7940_checks.error('parse_xml')
                    self.rfc7940_checks.error('codepoint_valid')
                    if not self.force_mode:
                        raise

                # Variants of char
                for variant in child.iter(VARIANT_TAG):
                    var_codepoint = [int(c, 16) for c
                                     in variant.get('cp').split()]
                    when = variant.get('when', None)
                    not_when = variant.get('not-when', None)
                    variant_type = variant.get('type', None)
                    comment = variant.get('comment', None)

                    # Handle references
                    ref = string_to_list(variant.get('ref', ''))

                    try:
                        self._lgr.add_variant(codepoint, var_codepoint,
                                              variant_type=variant_type,
                                              when=when, not_when=not_when,
                                              comment=comment,
                                              ref=ref,
                                              force=self.force_mode)
                    except LGRException as exc:
                        logger.error("Cannot add variant '%s' "
                                     "to code point '%s': %s",
                                     format_cp(var_codepoint),
                                     format_cp(codepoint),
                                     exc)
                        self.rfc7940_checks.error('parse_xml')
                        self.rfc7940_checks.error('codepoint_valid')
                        if not self.force_mode:
                            raise
            elif child.tag == RANGE_TAG:
                first_cp = int(child.get('first-cp'), 16)
                last_cp = int(child.get('last-cp'), 16)

                try:
                    self._lgr.add_range(first_cp, last_cp, comment=comment,
                                        ref=ref, tag=tag,
                                        when=when, not_when=not_when,
                                        force=self.force_mode)
                except LGRException as exc:
                    self.rfc7940_checks.error('parse_xml')
                    self.rfc7940_checks.error('codepoint_valid')
                    logger.error("Cannot add range '%s-%s': %s",
                                 format_cp(first_cp),
                                 format_cp(last_cp),
                                 exc)
                    if not self.force_mode:
                        raise

            child.clear()

        self.rfc7940_checks.tested('char_ascending_order')
        self.rfc7940_checks.tested('char_strict_ascending_order')

    def _process_rules(self, elem):
        """
        Process the <rules> element of an LGR XML file.
        """
        # Keep "text" version of the rules since we don't do anything with them.
        for child in elem:
            if child.tag in COMBINATOR_TAGS + (CLASS_TAG, ):
                cls = self._parse_class(child)
                self._lgr.add_class(cls, force=self.force_mode)
                child = drop_ns(child)
                self._lgr.classes_xml.append(etree.tostring(child, encoding=text_type))
            elif child.tag == RULE_TAG:
                rule = self._parse_rule(child)
                self._lgr.add_rule(rule, force=self.force_mode)
                child = drop_ns(child)
                self._lgr.rules_xml.append(etree.tostring(child, encoding=text_type))
            elif child.tag == ACTION_TAG:
                action = self._parse_action(child)
                self._lgr.add_action(action, force=self.force_mode)
                child = drop_ns(child)
                self._lgr.actions_xml.append(etree.tostring(child, encoding=text_type))
            else:
                logger.warning("Unhandled '%s' element in <rules> section",
                               child.tag)
                self.rfc7940_checks.error("parse_xml")
            child.clear()

    def _parse_rule(self, elem):
        """
        Parse a <rule> element.

        :return: The rule object created.
        """
        rule = Rule(name=elem.get('name', None),
                    comment=elem.get('comment', None),
                    ref=string_to_list(elem.get('ref', '')),
                    by_ref=elem.get('by-ref', None))

        for child in elem:
            self._parse_rule_helper(child, rule)

        return rule

    def _parse_rule_helper(self, child, rule):
        """
        Helper to parse the content of a <rule> element.

        This function is to be called on children of a top-level <rule>.

        :param child: Child element of a top-level <rule> element.
        :param rule: The top-level rule element to add the content to.
        """
        tag = child.tag
        comment = child.get('comment', None)
        count = child.get('count', None)

        if tag == ANCHOR_TAG:
            rule.add_child(AnchorMatcher(comment=comment))
        elif tag == ANY_TAG:
            rule.add_child(AnyMatcher(comment=comment, count=count))
        elif tag == CHAR_TAG:
            rule.add_child(CharMatcher(cp_or_sequence_from_class(child),
                                       comment=comment, count=count))
        elif tag == CHOICE_TAG:
            choice = ChoiceMatcher(comment=comment,
                                   count=count)
            for matcher in child:
                self._parse_rule_helper(matcher, choice)
            rule.add_child(choice)
        elif tag == END_TAG:
            rule.add_child(EndMatcher(comment=comment))
        elif tag == LOOKAHEAD_TAG:
            look_ahead = LookAheadMatcher(comment=comment)
            for matcher in child:
                self._parse_rule_helper(matcher, look_ahead)
            rule.add_child(look_ahead)
        elif tag == LOOKBEHIND_TAG:
            look_behind = LookBehindMatcher(comment=comment)
            for matcher in child:
                self._parse_rule_helper(matcher, look_behind)
            rule.add_child(look_behind)
        elif tag == START_TAG:
            rule.add_child(StartMatcher(comment=comment))
        elif tag == RULE_TAG:
            child_rule = self._parse_rule(child)
            rule.add_child(RuleMatcher(child_rule,
                                       comment=comment, count=count))
        elif tag == CLASS_TAG or tag in COMBINATOR_TAGS:
            rule.add_child(ClassMatcher(self._parse_class(child),
                           comment=comment,
                           count=count))
        else:
            logger.warning("Unhandled '%s' element in <rule> object", tag)
            self.rfc7940_checks.error('parse_xml')

    def _parse_action(self, elem):
        """
        Parse an <action> element.

        :return: The action object created.
        """
        disp = elem.get('disp')
        comment = elem.get('comment', None)

        match = elem.get('match', None)
        not_match = elem.get('not-match', None)

        any_variant = string_to_list(elem.get('any-variant', ''))
        all_variants = string_to_list(elem.get('all-variants', ''))
        only_variants = string_to_list(elem.get('only-variants', ''))

        return Action(disp, comment=comment, ref=string_to_list(elem.get('ref', '')),
                      match=match, not_match=not_match,
                      any_variant=any_variant,
                      all_variants=all_variants,
                      only_variants=only_variants)

    def _parse_class(self, elem):
        """
        Parse an <class> element.

        :return: The Class object created.
        """
        tag = elem.tag
        name = elem.get('name', None)
        comment = elem.get('comment', None)

        if tag == CLASS_TAG:
            cls = Class(name=name,
                        comment=comment,
                        ref=string_to_list(elem.get('ref', '')),
                        from_tag=elem.get('from-tag', None),
                        unicode_property=elem.get('property', None),
                        by_ref=elem.get('by-ref', None))
            if len(elem) == 0 and elem.text:
                # No child, code point(s) defined in text
                cls.add_codepoint(cp_or_sequence_from_class(elem))
            for child in elem:
                cls.add_codepoint(cp_or_sequence_from_class(child))
        elif tag in COMBINATOR_TAGS:
            MAPPING = {
                UNION_TAG: UnionClass,
                COMPLEMENT_TAG: ComplementClass,
                INTERSECTION_TAG: IntersectionClass,
                DIFFERENCE_TAG: DifferenceClass,
                SYM_DIFFERENCE_TAG: SymmetricDifferenceClass
            }
            cls = MAPPING[tag](name=name, comment=comment)
            # TODO: ensure number of children
            for child in elem:
                cls.add_child(self._parse_class(child))
        else:
            logger.warning("Unhandled '%s' element in <class> object", tag)
            self.rfc7940_checks.error('parse_xml')

        return cls

    def _fast_iter(self, context):
        """
        Iterator used to incrementally parse the XML file.
        """
        metadata_added = False
        for _, elem in context:
            if not metadata_added and elem == DATA_TAG:
                # The optional "meta" element is not present since it must
                # preceed the required data element.
                # However, we still have to call _process_meta
                self._process_meta({})
                metadata_added = True
            if elem.tag == META_TAG:
                logger.debug("Got 'meta' element")
                self._process_meta(elem)
            elif elem.tag == DATA_TAG:
                logger.debug("Got 'data' element")
                self._process_data(elem)
            elif elem.tag == RULES_TAG:
                logger.debug("Got 'rules' element")
                self._process_rules(elem)
            else:
                continue
            # Clean-up memory
            elem.clear()
        del context


def cp_or_sequence_from_class(elem):
    """
    Parse a given element to retrieve the code points it refers to.

    :param elem: XML node element.
    :return: List of code point defined in the class.
    """
    if elem.tag == CHAR_TAG:
        return [int(c, 16) for c in elem.get('cp').split()]
    elif elem.tag == RANGE_TAG:
        first_cp = int(elem.get('first-cp'), 16)
        last_cp = int(elem.get('last-cp'), 16)
        return range(first_cp, last_cp + 1)
    elif elem.tag == CLASS_TAG:
        cp_list = []
        codepoints = elem.text.strip().split()
        for cp in codepoints:
            if '-' in cp:
                # Range
                first_cp, last_cp = (int(c, 16) for c in cp.split('-'))
                cp_list.extend(range(first_cp, last_cp + 1))
            else:
                # Single
                cp_list.append(int(cp, 16))
        return cp_list


def string_to_list(string):
    """
    Convert to list from space-separated entry.

    If input string is empty, return empty list.

    :param string: Input space-separated list.
    :return: List of strings.

    >>> string_to_list("") == []
    True
    >>> string_to_list("one") == ["one"]
    True
    >>> string_to_list("one two") == ["one", "two"]
    True
    """
    # This is because(''.split('') -> [''])
    result = []
    if len(string) > 0:
        result = string.split(' ')

    return result


def drop_ns(node):
    """
    Remove namespace from a node and its children.

    This function destroys the input!

    :param node: The parent node.
    :return: new node without namespace.
    """
    # First step: remove default namespace from node and its children
    for elem in node.iter():
        elem.tag = elem.tag.replace("{{{}}}".format(LGR_NS), "")

    # Create new node with same sanitized tag and attributes
    new_node = etree.Element(node.tag, node.attrib)
    new_node.text = node.text
    # Then move all node children to new node
    new_node[:] = node[:]

    # Clear any memory used by node itself.
    node.clear()

    return new_node

if __name__ == "__main__":
    import doctest

    logger.addHandler(logging.NullHandler())
    doctest.testmod()
