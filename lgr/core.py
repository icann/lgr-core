# -*- coding: utf-8 -*-
"""
core.py - Definition of main object and methods of a LGR structure.
"""
from __future__ import unicode_literals

import logging
import collections
from collections import OrderedDict
from io import StringIO

from lgr.metadata import ReferenceManager, Metadata
from lgr.char import Repertoire, CharSequence
from lgr.action import Action
from lgr.classes import Class, TAG_CLASSNAME_PREFIX
from lgr.exceptions import (LGRApiInvalidParameter,
                            CharAlreadyExists,
                            CharInvalidContextRule,
                            NotInRepertoire,
                            NotInLGR,
                            CharInvalidIdnaProperty,
                            CharNotInScript,
                            RangeInvalidContextRule,
                            VariantInvalidContextRule,
                            ReferenceNotDefined,
                            DuplicateReference,
                            LGRFormatException,
                            LGRApiException,
                            LGRException)
from lgr.mixed_scripts_variant_filter import MixedScriptsVariantFilter, BaseMixedScriptsVariantFilter
from lgr.validate import validate_lgr
from lgr.populate import populate_lgr
from lgr.utils import (collapse_codepoints,
                       format_cp, is_idna_valid_cp_or_sequence)

logger = logging.getLogger(__name__)
rule_logger = logging.getLogger('lgr-rule-logger')

# Default disposition used in
# 7.3.  Determining a Disposition for a Label or Variant Label, step 3
DEFAULT_DISPOSITION = "allocatable"

# Invalid disposition which causes the label to be removed
# 8.2.  Determining Variants for a Label, step 5
INVALID_DISPOSITION = "invalid"

# Defaults actions
# 7.6.  Default Actions
DEFAULT_ACTIONS = (
    Action(disp='invalid', comment="Default action for invalid",
           any_variant=['invalid']),
    Action(disp='blocked', comment="Default action for blocked",
           any_variant=['blocked']),
    Action(disp='allocatable', comment="Default action for allocatable",
           any_variant=['allocatable']),
    Action(disp='activated', comment="Default action for activated",
           all_variants=['activated']),
    Action(disp='valid', comment="Default catch-all")
)
DEFAULT_ACTIONS_XML = (
    '<action disp="invalid" comment="Default action for invalid" any-variant="invalid"/>',
    '<action disp="blocked" comment="Default action for blocked" any-variant="blocked"/>',
    '<action disp="allocatable" comment="Default action for allocatable" any-variant="allocatable"/>',
    '<action disp="activated" comment="Default action for activated" all-variants="activated"/>',
    '<action disp="valid" comment="Default catch-all" />'
)

# Maximum number of variants to generate
MAX_NUMBER_GENERATED_VARIANTS = 1000

# From RFC1035, 2.3.4 Size limits
PROTOCOL_LABEL_MAX_LENGTH = 63


class LGR(object):
    """
    The main LGR object.
    """

    def __init__(self,
                 name='New File',
                 metadata=None,
                 reference_manager=None,
                 unicode_database=None,
                 allow_invalid_property=False):
        """
        Create an LGR object.

        :param str name: Name of the LGR.
        :param Metadata metadata: Optional metadata.
        :param ReferenceManager reference_manager: Optional reference manager.
        :param UnicodeDatabase unicode_database: Optional Unicode database.
                                                 If no database is used,
                                                 all Unicode-related checks
                                                 are skipped.
        :param allow_invalid_property: Whether an exception should be raised when cp_or_sequence is or contains an
                                       invalid IDNA2008 property
        """
        self.name = name or 'New File'

        if metadata is None:
            self.metadata = Metadata()
        else:
            self.metadata = metadata

        self.repertoire = Repertoire()

        self._unicode_database = unicode_database

        self.raise_on_invalid_property = not allow_invalid_property

        # Used to store types of variants used.
        # Not updated on variant deletion
        self.types = set()

        # Rules are ordered, so when adding a rule:
        # - store its name in self.rules array (ordered structure).
        # - store the rule in the self.rules_lookup dict (indexed by its name).
        self.rules = []
        self.rules_lookup = OrderedDict()
        # Until we know how to edit rules, keep the XML text here
        self.rules_xml = []

        # Classes are ordered, so when adding a class:
        # - store its name in self.classes array (ordered structure).
        # - store the rule in the self.classes_lookup dict (indexed by its name).
        self.classes = []
        self.classes_lookup = OrderedDict()
        # Until we know how to edit classes, keep the XML text here
        self.classes_xml = []

        self.actions = []
        self.actions_xml = []

        if reference_manager is None:
            self.reference_manager = ReferenceManager()
        else:
            self.reference_manager = reference_manager

    def __getstate__(self):
        """
        Called when pickling an LGR instance.
        """
        odict = self.__dict__.copy()  # copy the dict since we change it
        # Do not pickle the unicode database
        del odict['_unicode_database']
        return odict

    def __setstate__(self, idict):
        """
        Called when un-pickling an LGR instance.
        """
        self.__dict__.update(idict)
        # __init__ not called during un-pickling so we have to manually define
        # attributes which were deleted during pickling
        self.__dict__['_unicode_database'] = None

    @property
    def effective_actions(self):
        """
        The effective list of actions (i.e. including `DEFAULT_ACTIONS`) of the LGR
        """
        return self.actions + list(DEFAULT_ACTIONS)

    @property
    def effective_actions_xml(self):
        """
        The effective list of actions (i.e. including `DEFAULT_ACTIONS`)
        of the LGR, as XML string
        """
        return self.actions_xml + list(DEFAULT_ACTIONS_XML)

    @property
    def unicode_database(self):
        """
        Getter property for the Unicode database.

        :return: The currently used unicode database.
        """
        return self._unicode_database

    @unicode_database.setter
    def unicode_database(self, unidb):
        """
        Setter property for the Unicode database.
        Check that the unidb version is the same
        as the one defined in the LGR metadata.

        :param UnicodeDatabase unidb: New Unicode database to use.
        """
        unidb_version = unidb.get_unicode_version()
        if unidb_version != self.metadata.unicode_version:
            logger.warning("Unicode database version is '%s' "
                           "when LGR Unicode version is '%s'",
                           unidb_version, self.metadata.unicode_version)
        self._unicode_database = unidb

    def add_reference(self, value, comment=None, ref_id=None):
        """
        Add a reference to the reference list.

        :param value: Value of the reference.
        :param comment: Optional comment.
        :param ref_id: Optional reference id to use.
        :return: The id used for the reference.
        :raises ReferenceAlreadyExists: if ref_id is provided,
                                        and a reference with this id
                                        already exists.
        """
        return self.reference_manager.add_reference(value,
                                                    comment=comment,
                                                    ref_id=ref_id)

    def del_reference(self, ref_id):
        """
        Delete a reference from the reference list.
        Iterate through the list of defined code points to remove the reference.

        :param ref_id:
        :raises ReferenceNotDefined: if the ref_id is not defined.
        """
        self.repertoire.del_reference(ref_id)
        self.reference_manager.del_reference(ref_id)

    def del_tag(self, tag_id):
        """
        Delete a tag from the LGR.
        Iterate through the list of defined code points to remove the tag.
        Note: WLE rules are not touched by this function, so any class using a 'from-tag=`tag_id`'
        attribute will still be present after calling this method.

        :param tag_id: The tag name.
        """
        self.repertoire.del_tag(tag_id)
        self.classes_lookup.pop(TAG_CLASSNAME_PREFIX + tag_id, None)

    def add_cp(self, cp_or_sequence,
               comment=None, ref=None,
               tag=None,
               when=None, not_when=None,
               validating_repertoire=None,
               override_repertoire=False,
               force=False):
        """
        Add a code point (or code point sequence) to an LGR.

        Optionally check the validity of code point against a validating
        repertoire, and can ignore result of this check.

        :param cp_or_sequence: Code point or sequence to add to the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :param comment: Comment associated to the code point.
        :param ref: List of references associated to the code point.
        :param tag: List of tags associated to the code point.
        :param when: Condition to be satisfied by the code point.
        :param not_when: Condition to not be satisfied by the codepoint.
        :param validating_repertoire: If given, check that the code point is in
                                      this repertoire.
        :param override_repertoire: If True, insert code point into LGR
                                    even if the code point is not in
                                    the validating repertoire.
        :param force: If True, insert the code point in the LGR
                      the best way possible.
                      This implies override_repertoire=True.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInRepertoire: If code point is not in validating_repertoire
                                 and override_repertoire is False.
        :raises ReferenceNotDefined: If ref_id is provided and does not match
                                     existing reference in LGR.
        :raises CharInvalidContextRule: If code point has invalid context rules.

        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> lgr.repertoire[0x0061] is not None
        True
        >>> lgr.add_cp(0x0062)
        >>> lgr.repertoire[0x0062] is not None
        True
        >>> lgr.add_cp([0x0063, 0x002D])
        >>> lgr.repertoire[[0x0063, 0x002D]] is not None
        True
        """
        logger.debug("Add cp '%s' to LGR '%s'", cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)
        if (not force) and (when is not None) and (not_when is not None):
            logger.error("Cannot add code point '%s' with both 'when' "
                         "and 'not-when' attributes", format_cp(cp_or_sequence))
            raise CharInvalidContextRule(cp_or_sequence)

        if validating_repertoire is not None:
            for cp in cp_or_sequence:
                cp_valid = validating_repertoire.check_cp(cp)
                logger.debug('Result of check of CP %s against repertoire %s: %s',
                             format_cp(cp),
                             validating_repertoire,
                             cp_valid)
                if not cp_valid:
                    if not override_repertoire and not force:
                        raise NotInRepertoire(cp_or_sequence)
                    else:
                        logger.warning("Overriding repertoire '%s' "
                                       "for code point '%s'",
                                       validating_repertoire,
                                       format_cp(cp_or_sequence))

        # Reference handling
        references = []
        for ref_id in ref if ref is not None else []:
            if ref_id in self.reference_manager:
                references.append(ref_id)
            else:
                logger.warning("Reference id '%s' for code point '%s' "
                               "is not defined",
                               ref_id, cp_or_sequence)
                if not force:
                    raise ReferenceNotDefined(ref_id)

        ref_set = set(references)
        if len(ref_set) != len(references):
            # 4.3.1.  The ref Attribute
            # It is an error to repeat a reference identifier in
            # the same "ref" attribute.
            logger.error("Reference list '%s' for code point '%s' contains "
                         "duplicate reference id",
                         references, format_cp(cp_or_sequence))
            if not force:
                raise DuplicateReference(cp_or_sequence)

        # Tag handling
        tags = tag if tag is not None else []
        if len(cp_or_sequence) > 1 and len(tags) > 0:
            # From RFC7940, section 5.5.  Code Point Tagging
            # a "tag" attribute MUST NOT be present in a "char" element
            # defining a code point sequence.
            logger.warning("Code point sequence '%s' has invalid tag defined",
                           format_cp(cp_or_sequence))
            if not force:
                raise LGRFormatException(LGRFormatException.
                                         LGRFormatReason.SEQUENCE_NO_TAG)

        # RFC7940, section 5.5.  Code Point Tagging
        # It is an error to duplicate a value within the same "tag" attribute.
        duplicates = [t for t, count
                      in collections.Counter(tags).items() if count > 1]
        if len(duplicates) > 0:
            logger.warning("Code point '%s' has duplicate tags %s",
                           format_cp(cp_or_sequence), duplicates)
            if not force:
                raise LGRFormatException(LGRFormatException.
                                         LGRFormatReason.DUPLICATE_TAG)

        self.repertoire.add_char(cp_or_sequence,
                                 comment=comment,
                                 ref=references,
                                 tag=tags,
                                 when=when,
                                 not_when=not_when)

        # Add code point to tag classes
        self._add_cp_to_tag_classes(cp_or_sequence, tags)

    def check_cp(self, cp_or_sequence):
        """
        Check if a code point is present in LGR.

        :param cp_or_sequence: Code point or sequence to check presence of.
        :returns: True if code point is present in LGR, False otherwise.

        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> lgr.check_cp(0x0061)
        True
        >>> lgr.check_cp(0x0062)
        False
        >>> lgr.check_cp([0x0061, 0x0062])
        False
        """
        cp_or_sequence = self._check_convert_cp(cp_or_sequence)
        return cp_or_sequence in self.repertoire

    def del_cp(self, cp_or_sequence):
        """
        Delete a code point (or code point sequence) from an LGR.

        :param cp_or_sequence: Code point or sequence to add to the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInLGR: If code point is not in LGR.

        >>> lgr = LGR()
        >>> lgr.add_cp(0x0061)
        >>> lgr.del_cp(0x0061)
        >>> len(lgr.repertoire) == 0
        True
        """
        logger.debug("Delete cp '%s' from LGR '%s'", cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)

        char = self.repertoire.get_char(cp_or_sequence)
        self.repertoire.del_char(cp_or_sequence)
        self._del_cp_from_tag_classes(cp_or_sequence, char.tags)

    def add_range(self, first_cp, last_cp,
                  comment=None, ref=None,
                  tag=None,
                  when=None, not_when=None,
                  validating_repertoire=None,
                  override_repertoire=False,
                  force=False):
        """
        Add a range to an LGR.

        Optionally check the validity of code points in the range
        against a validating repertoire, and can ignore result of this check.

        :param first_cp: First code point of the range.
        :param last_cp: Last code point of the range.
        :param comment: Comment associated to the code point.
        :param ref: List of references associated to the code point.
        :param tag: List of tags associated to the code point.
        :param when: Condition to be satisfied by the code point.
        :param not_when: Condition to not be satisfied by the codepoint.
        :param validating_repertoire: If given, check that the code point is in
                                      this repertoire.
        :param override_repertoire: If True, insert code point into LGR
                                    even if the code point is not in
                                    the validating repertoire.
        :param force: If True, insert the code point in the LGR the best way possible.
                      This implies override_repertoire=True.
        :raises LGRApiInvalidParameter: If first_cp > last_cp.
        :raises NotInRepertoire: If one of the code point in the range
                                 is not in validating_repertoire
                                 and override_repertoire is False.
        :raises ReferenceNotDefined: If ref_id is provided and does not match
                                     existing reference in LGR.
        :raises RangeInvalidContextRule: If crangehas invalid context rules.

        >>> lgr = LGR()
        >>> lgr.add_range(0x0061, 0x007A)
        >>> 0x0061 in lgr.repertoire
        True
        >>> 0x007A in lgr.repertoire
        True
        """
        logger.debug("Add range '%s-%s' to LGR '%s'", first_cp, last_cp, self)

        if first_cp > last_cp:
            logger.error('First code point of range is greater than last')
            raise LGRApiInvalidParameter('first_cp')

        if (not force) and (when is not None) and (not_when is not None):
            logger.error("Cannot add range '%s-%s' with both 'when' "
                         "and 'not-when' attributes",
                         format_cp(first_cp), format_cp(last_cp))
            raise RangeInvalidContextRule(first_cp, last_cp)

        check_range = self.check_range(first_cp,
                                       last_cp,
                                       validating_repertoire)
        codepoints = []
        for (cp, status) in check_range:
            if status is None:
                codepoints.append(cp)
            elif isinstance(status, NotInRepertoire):
                logger.warning("CP '%s' is not in repertoire %s",
                               format_cp(cp), validating_repertoire)
                if not override_repertoire and not force:
                    raise status
                else:
                    logger.warning("Overriding repertoire '%s' "
                                   "for code point '%s'",
                                   validating_repertoire, format_cp(cp))
                    codepoints.append(cp)
            elif isinstance(status, CharInvalidIdnaProperty):
                logger.error("CP '%s' is not IDNA valid", format_cp(cp))
                if not self.raise_on_invalid_property:
                    codepoints.append(cp)
                elif not force:
                    raise status
            elif isinstance(status, CharAlreadyExists):
                logger.error("CP '%s' is already present in repertoire",
                             format_cp(cp))
                if not force:
                    raise status
            else:
                logger.critical("Unhandled status %s for CP '%s'",
                                status.__class__.__name__, format_cp(cp))
                raise LGRException()

        # References handling
        references = []
        for ref_id in ref if ref is not None else []:
            if ref_id in self.reference_manager:
                references.append(ref_id)
            else:
                logger.warning("Reference id '%s' for range '%s-%s' "
                               "is not defined",
                               ref_id, format_cp(first_cp), format_cp(last_cp))
                if not force:
                    raise ReferenceNotDefined(ref_id)

        ref_set = set(references)
        if len(ref_set) != len(references):
            # 4.3.1.  The ref Attribute
            # It is an error to repeat a reference identifier in
            # the same "ref" attribute.
            logger.error("Reference list '%s' for range '%s-%s' contains "
                         "duplicate reference id",
                         references, format_cp(first_cp), format_cp(last_cp))
            if not force:
                raise DuplicateReference(first_cp)

        # Tag handling
        tags = tag if tag is not None else []
        # From RFC7940, section 5.5.  Code Point Tagging
        # It is an error to duplicate a value within the same "tag" attribute.
        duplicates = [t for t, count
                      in collections.Counter(tags).items() if count > 1]
        if len(duplicates) > 0:
            logger.warning("Range '%s-%s' has duplicate tags %s",
                           format_cp(first_cp), format_cp(last_cp),
                           duplicates)
            if not force:
                raise LGRFormatException(LGRFormatException.
                                         LGRFormatReason.DUPLICATE_TAG)

        self._insert_list(codepoints,
                          comment=comment,
                          ref=references,
                          tag=tags,
                          when=when,
                          not_when=not_when)

        # Add code points to tag classes
        for cp in codepoints:
            self._add_cp_to_tag_classes(cp, tags)

    def del_range(self, first_cp, last_cp):
        """
        Delete a range from an LGR.

        :param first_cp: First code point of the range.
        :param last_cp: Last code point of the range.
        :raises LGRApiInvalidParameter: If first_cp > last_cp.
        :raises NotInLGR: If range is not in LGR.

        >>> lgr = LGR()
        >>> lgr.add_range(0x0061, 0x007A)
        >>> lgr.del_range(0x0061, 0x007A)
        >>> 0x0061 in lgr.repertoire
        False
        >>> 0x007A in lgr.repertoire
        False
        >>> len(lgr.repertoire)
        0
        """
        logger.debug("Delete range '%s-%s' from LGR '%s'",
                     first_cp, last_cp, self)

        if first_cp > last_cp:
            logger.error('First code point of range is greater than last')
            raise LGRApiInvalidParameter('first_cp')

        self.repertoire.del_range(first_cp, last_cp)

    def expand_ranges(self):
        """
        Expand all ranges to single code points.

        Iterate through the LGR and expand the encountered ranges.
        """
        logger.debug("Expand all ranges from LGR '%s'", self)
        for (first_cp, last_cp) in self.repertoire.ranges[:]:
            self.expand_range(first_cp, last_cp)

    def expand_range(self, first_cp, last_cp):
        """
        Expand a range to a list of single code points.

        This is a one-way operation: once expanded, the range will be lost.

        :param first_cp: First code point of the range.
        :param last_cp: Last code point of the range.
        :raises LGRApiInvalidParameter: If first_cp > last_cp.
        :raises NotInLGR: If range is not in LGR.

        >>> lgr = LGR()
        >>> lgr.add_range(0x0061, 0x007A)
        >>> lgr.expand_range(0x0061, 0x007A)
        """
        logger.debug("Expand range '%s-%s' from LGR '%s'",
                     first_cp, last_cp, self)

        if first_cp > last_cp:
            logger.error('First code point of range is greater than last')
            raise LGRApiInvalidParameter('first_cp')

        # Retrieve the first char as a reference for properties.
        range_char = self.get_char(first_cp)

        self.repertoire.del_range(first_cp, last_cp)

        for cp in range(first_cp, last_cp + 1):
            self.repertoire.add_char([cp],
                                     comment=range_char.comment,
                                     ref=range_char.references,
                                     tag=range_char.tags,
                                     when=range_char.when,
                                     not_when=range_char.not_when)

    def add_variant(self, cp_or_sequence,
                    variant_cp,
                    variant_type=None,
                    when=None, not_when=None,
                    comment=None,
                    ref=None,
                    validating_repertoire=None,
                    override_repertoire=False,
                    force=False):
        """
        Add a variant to a code point.

        Optionally check the validity of variant code point
        against a validating repertoire, and can ignore result of this check.

        :param cp_or_sequence: Code point or sequence to modify in the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :param variant_cp: Code point or sequence to use as variant.
        :param variant_type: Type of the variant, if any.
        :param when: Condition to be satisfied for the variant to exist.
        :param not_when: Condition to must be not satisfied for the variant.
        :param comment: Comment associated to the code point.
        :param ref: List of references associated to the code point.
        :param validating_repertoire: If given, check that the code point is in
                                      this repertoire.
        :param override_repertoire: If True, insert code point into LGR
                                    even if the code point is not in
                                    the validating repertoire.
        :param force: If True, insert the variant in the LGR the best way possible.
                      This implies override_repertoire=True.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInLGR: If cp_or_sequence is not in the current LGR.
        :raises NotInRepertoire: If variant_cp is not in validating_repertoire
                                 and override_repertoire is False.
        :raises ReferenceNotDefined: If ref_id is provided and does not match
                                     existing reference in LGR.
        :raises VariantInvalidContextRule: If variant has invalid context rules.

        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> lgr.add_variant([0x0061], [0x0062])
        >>> lgr.add_variant([0x0061], [0x0063])
        >>> lgr.add_variant([0x0062], [0x0062]) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NotInLGR:
        """
        logger.debug("Add variant '%s' for cp '%s' to LGR '%s'",
                     variant_cp, cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)
        var_cp_or_sequence = self._check_convert_cp(variant_cp)

        if (not force) and (when is not None) and (not_when is not None):
            logger.error("Cannot add variant '%s' to code point '%s' "
                         " with both 'when' and 'not-when' attributes",
                         format_cp(var_cp_or_sequence), format_cp(cp_or_sequence))
            raise VariantInvalidContextRule(cp_or_sequence, var_cp_or_sequence)

        if validating_repertoire is not None:
            for var_cp in var_cp_or_sequence:
                cp_valid = validating_repertoire.check_cp(var_cp)
                logger.debug('Result of check of CP %s against repertoire %s: %s',
                             format_cp(var_cp),
                             validating_repertoire,
                             cp_valid)
                if not cp_valid:
                    if not override_repertoire and not force:
                        raise NotInRepertoire(cp_or_sequence)
                    else:
                        logger.warning("Overriding repertoire '%s' for "
                                       "variant '%s' of code point '%s'",
                                       validating_repertoire,
                                       format_cp(var_cp_or_sequence),
                                       format_cp(cp_or_sequence))

        references = []
        for ref_id in ref if ref is not None else []:
            if ref_id in self.reference_manager:
                references.append(ref_id)
            else:
                logger.warning("Reference id '%s' for "
                               "variant '%s' of code point '%s' "
                               "is not defined",
                               ref_id,
                               format_cp(var_cp_or_sequence),
                               format_cp(cp_or_sequence))
                if not force:
                    raise ReferenceNotDefined(ref_id)

        ref_set = set(references)
        if len(ref_set) != len(references):
            # 4.3.1.  The ref Attribute
            # It is an error to repeat a reference identifier in
            # the same "ref" attribute.
            logger.error("Reference list '%s' for variant '%s' of "
                         "code point '%s' contains "
                         "duplicate reference id",
                         references,
                         format_cp(var_cp_or_sequence),
                         format_cp(cp_or_sequence))
            if not force:
                raise DuplicateReference(cp_or_sequence)

        self.repertoire.add_variant(cp_or_sequence, var_cp_or_sequence,
                                    variant_type=variant_type,
                                    when=when, not_when=not_when,
                                    comment=comment,
                                    ref=references)

        # Variant insertion went well, can store its type
        self.types.add(variant_type)

    def del_variant(self, cp_or_sequence, variant_cp,
                    when=None, not_when=None):
        """
        Delete a specific variant from an LGR.

        :param cp_or_sequence: Code point or sequence to modify in the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :param variant_cp: Code point or sequence to use as variant.
        :param when: Condition to be satisfied for the variant to exist.
        :param not_when: Condition to must be not satisfied for the variant.
        :returns: True if deleted.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInLGR: If cp_or_sequence is not in the current LGR.

        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> lgr.add_variant([0x0061], [0x0062])
        >>> lgr.del_variant([0x0061], [0x0062])
        True
        >>> lgr.del_variant([0x0062], [0x0031]) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NotInLGR:
        """
        logger.debug("Delete variant '%s' for cp '%s' from LGR '%s'",
                     variant_cp, cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)

        return self.repertoire.del_variant(cp_or_sequence, variant_cp,
                                           when, not_when)

    def get_variants(self, cp_or_sequence):
        """
        Iterate through the variants of a given code point.

        :param cp_or_sequence: Code point or sequence in the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :returns: Generator of Variant objects.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInLGR: If cp_or_sequence is not in the current LGR.

        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> lgr.add_variant([0x0061], [0x0062])
        >>> variants = lgr.get_variants([0x0061])
        >>> len(list(variants)) == 1
        True
        """
        logger.debug("Get variant for cp '%s' from LGR '%s'",
                     cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)
        return self.repertoire.get_variants(cp_or_sequence)

    def get_variant(self, cp_or_sequence, var_cp):
        """
        Retrieve a specific variant of a given code point.

        :param cp_or_sequence: Code point or sequence in the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :param var_cp: The desired variant code point.
        :returns: Generator of Variant objects.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInLGR: If cp_or_sequence is not in the current LGR.

        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> lgr.add_variant([0x0061], [0x0062])
        >>> lgr.add_variant([0x0061], [0x0063])
        >>> variant = lgr.get_variant([0x0061], (0x0063, ))
        >>> len(variant) == 1
        True
        """
        logger.debug("Get variant for cp '%s' from LGR '%s'",
                     cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)
        return self.repertoire.get_variant(cp_or_sequence, var_cp)

    def get_char(self, cp_or_sequence):
        """
        Return the char object associated to a given code point.

        :param cp_or_sequence: Code point or sequence to get from the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :returns: The CharBase object corresponding to cp_or_sequence.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises NotInLGR: If cp_or_sequence is not in the current LGR.

        >>> from lgr.char import CharBase
        >>> lgr = LGR()
        >>> lgr.add_cp([0x0061])
        >>> char = lgr.get_char([0x0061])
        >>> isinstance(char, CharBase)
        True
        """
        logger.debug("Get variant for cp '%s' from LGR '%s'",
                     cp_or_sequence, self)

        cp_or_sequence = self._check_convert_cp(cp_or_sequence)
        return self.repertoire.get_char(cp_or_sequence)

    def check_range(self, first_cp, last_cp,
                    validating_repertoire=None):
        """
        Check validity of all code points in a range.

        :param first_cp: First code point of range.
        :param last_cp: Last code point of range.
        :param validating_repertoire: If given, check that the code points are in
                                      this repertoire.
        :returns: List of all code points from the range, with a status:
                  [(0x0061, None), ..., (0x007B, CharInvalidIdnaProperty)]

        >>> from munidata.database import IDNADatabase
        >>> unidb = IDNADatabase('6.3.0')
        >>> lgr = LGR(unicode_database=unidb)
        >>> r = lgr.check_range(0x0061, 0x007B)
        >>> r[0][0] == 0x0061
        True
        >>> r[0][1] is None
        True
        >>> r[-1][0] == 0x007B
        True
        >>> isinstance(r[-1][1], CharInvalidIdnaProperty)
        True
        """
        logger.debug("Check range '%s-%s' to LGR '%s'",
                     first_cp, last_cp, self)

        if first_cp > last_cp:
            logger.error('First code point of range is greater than last')
            raise LGRApiInvalidParameter('first_cp')

        result = []
        for cp in range(first_cp, last_cp + 1):

            # Test validity of code point (IDNA)
            keep_raise = self.raise_on_invalid_property
            try:
                # we need the method to raise exception in that case
                self.raise_on_invalid_property = True
                # No need to force since it is the aim of this function
                cp_ = self._check_convert_cp(cp)
            except CharInvalidIdnaProperty as invalid:
                result.append((cp, invalid))
                continue
            finally:
                self.raise_on_invalid_property = keep_raise

            # Test validity of code point (reference repertoire)
            if validating_repertoire is not None:
                cp_valid = validating_repertoire.check_cp(cp)
                if not cp_valid:
                    result.append((cp, NotInRepertoire(cp)))
                    continue

            # Test presence of code point in repertoire
            if cp_ in self.repertoire:
                result.append((cp, CharAlreadyExists(cp_)))
                continue

            # Code point has been inserted into repertoire, no problem
            result.append((cp, None))

        return result

    def add_codepoints(self, codepoints, comment=None, ref=None, tag=None):
        """
        Utility function to add a list of code points in a LGR.

        The function will extract ranges from the list and add them to the LGR.
        All other code points will be added as single value code point.
        All code points will be checked upon insertion.
        All code points have the same properties.

        :param codepoints: List of code points.
        :param comment: Comment associated to the range.
        :param ref: List of references associated to the code point.
        :param tag: List of tags associated to the code point.

        >>> lgr = LGR()
        >>> lgr.add_codepoints(range(0x0061, 0x007A))
        """
        logger.debug('Add code points to LGR %s', self)

        if not codepoints:
            return

        ranges = collapse_codepoints(codepoints)
        for (first_cp, last_cp) in ranges:
            if first_cp == last_cp:
                # Single code point
                self.add_cp([first_cp], comment=comment,
                            ref=ref, tag=tag)
            else:
                self.add_range(first_cp, last_cp,
                               comment=comment,
                               ref=ref, tag=tag)

    def validate(self, options):
        """
        Validate and create a summary for the LGR.

        :param options: Dictionary of options to the validation function.
        """
        logger.debug('Validate LGR')
        # Let validation module handle that
        return validate_lgr(self, options)

    def add_rule(self, rule, force=False):
        """
        Add a rule to the LGR.

        :param rule: the rule to add to the LGR.
        :param force: If True, insert the rule in the LGR even if it does not
                      validate.
        """
        logger.debug("Add '%s'", rule)

        try:
            rule.validate([], self.rules_lookup, self.classes_lookup)
        except LGRFormatException as exc:
            level = logging.WARNING if force else logging.ERROR
            logger.log(level, "Invalid rule '%s'", rule.name)
            if not force:
                raise exc

        self.rules_lookup[rule.name] = rule
        self.rules.append(rule.name)

    def add_action(self, action, force=False):
        """
        Add an action to the LGR.

        :param action: The action to add to the LGR.
        :param force: If True, insert the action in the LGR even if it does not
                      validate.
        """
        logger.debug("Add '%s'", action)
        # TODO: implement action validity testing
        self.actions.append(action)

    def add_class(self, cls, force=False):
        """
        Add a class to the LGR.

        :param cls: The class to add to the LGR.
        :param force: If True, insert the class in the LGR even if it does not
                      validate.
        """
        logger.debug("Add '%s'", cls)
        try:
            cls.validate([], self.rules_lookup, self.classes_lookup)
        except LGRFormatException as exc:
            level = logging.WARNING if force else logging.ERROR
            logger.log(level, "Invalid rule '%s'", cls)
            if not force:
                raise exc
        self.classes_lookup[cls.name] = cls
        self.classes.append(cls.name)

    def test_label_eligible(self, label, is_variant=False, collect_log=True):
        """
        Test label eligibility against an LGR.

        Full test of eligibility, ie. test that each code point is in the LGR
        and test disposition of reflexive mappings.

        :param label: The label to test, as an array of codepoints.
        :param is_variant: Whether we are testing a variant label eligibility.
        :param collect_log: If False, do not collect rule processing log.
        :return: (result, label_parts, label_invalid_parts, disposition, action_idx, log)
                 with:

                     - result: True if the label is eligible according to the LGR,
                               False otherwise.
                     - label_parts: List of the code points valid in the LGR.
                     - label_invalid_parts: List of code points not valid in the LGR.
                     - disposition: Disposition of the label.
                     - action_idx: Index of the action
                                   which triggered the disposition,
                                   -1 if the label is not in the LGR.
                     - log: Log of the disposition computation,
                            empty if collect_log is False
        """
        if not label:
            raise LGRApiInvalidParameter('label')

        log_output = StringIO()
        if collect_log:
            # Configure log system to redirect logs to local attribute
            ch = logging.StreamHandler(log_output)
            ch.setLevel(logging.INFO)
            rule_logger.addHandler(ch)

        # Start by testing presence of code points in LGR
        (valid, label_parts, label_invalid_parts) = self._test_preliminary_eligibility(label)
        if not valid:
            rule_logger.error("Label '%s' is not in the LGR", format_cp(label))
            if collect_log:
                rule_logger.removeHandler(ch)
            return False, label_parts, label_invalid_parts, INVALID_DISPOSITION, -1, log_output.getvalue()

        # Compute label disposition by analyzing reflexive mappings
        (disposition, action_idx) = self._test_label_disposition(label, apply_reflexive_mapping=not is_variant)
        if disposition == INVALID_DISPOSITION:
            rule_logger.error("Invalid disposition for reflexive mapping, "
                              "triggered by action #%d", action_idx)
            if collect_log:
                rule_logger.removeHandler(ch)
            return False, [], [], disposition, action_idx, log_output.getvalue()

        if collect_log:
            rule_logger.removeHandler(ch)
        return True, label, [], disposition, action_idx, log_output.getvalue()

    def compute_label_disposition(self, label, include_invalid=False,
                                  collect_log=True, hide_mixed_script_variants=False,
                                  with_labels=None):
        """
        Given a label, compute its disposition and its variants.

        The original label (unpermuted or with reflexive variants) will be the
        last label returned.

        :param label: The label to compute the disposition of,
                      as a sequence of code points.
                      Label MUST be eligible.
        :param include_invalid: If True, also return variants with "invalid"
                                disposition, which are normally eliminated
                                during the generation process.
        :param collect_log: If False, do not collect rule processing log.
        :param hide_mixed_script_variants: Whether we hide mixed scripts variants.
        :param with_labels: Compute disposition of selected labels only, all if None
        :return: Generator of (variant_cp, variant_invalid_parts, disp, action_idx, disp_set, log)
                 with:
                     - variant_cp: The code point sequence of a variant.
                     - variant_invalid_parts: List of code points not valid in the LGR.
                     - disp: The disposition of the variant.
                     - variant_invalid_parts: List of code points not valid in the LGR.
                     - action_idx: The index of the action which triggered the disposition.
                     - disp_set: The disposition set generated for this label.
                     - log: The log of the generation of the label,
                             empty if collect_log is True.
        """
        # Implements process described in 8. Processing a Label Against an LGR

        if self._unicode_database is None:
            logger.error("You need to define the Unicode database "
                         "to use this function")
            raise LGRApiException()

        if len(label) > PROTOCOL_LABEL_MAX_LENGTH:
            logger.warning('Label is too long')
            raise LGRApiInvalidParameter('label')

        # Make sure the label is a sequence
        label = tuple(label)

        # 8.2 Determining Variants for a Label
        # Step 1 - 2 - 3
        variant_set = self._generate_label_variants(label, hide_mixed_script_variants=hide_mixed_script_variants)

        original_label = None
        # sometimes we have duplicated (e.g. twice the same characters)
        already_handled = set()

        # Step 4 - 8.3.  Determining a Disposition for a Label or Variant Label
        for (variant_cp, disp_set, only_variants) in variant_set:
            if variant_cp in already_handled:
                continue
            if with_labels and variant_cp not in with_labels:
                continue
            already_handled.add(variant_cp)
            # Configure log system to redirect logs to local attribute
            log_output = StringIO()
            if collect_log:
                ch = logging.StreamHandler(log_output)
                ch.setLevel(logging.DEBUG)
                rule_logger.addHandler(ch)

            # 8.3.  Determining a Disposition for a Label or Variant Label
            # Step 1
            eligible, _, variant_invalid_parts, _, idx, _ = self.test_label_eligible(variant_cp,
                                                                                     is_variant=variant_cp != label,
                                                                                     collect_log=collect_log)
            if not eligible:
                variant_disp = INVALID_DISPOSITION
            else:
                # 8.3.  Determining a Disposition for a Label or Variant Label
                # Step 2 - 3
                (variant_disp, idx) = self._apply_actions(variant_cp,
                                                          disp_set,
                                                          only_variants)

                if variant_disp is None:
                    # 8.3.  Determining a Disposition for a Label or Variant Label
                    # Step 4
                    variant_disp = DEFAULT_DISPOSITION

            if (variant_disp != INVALID_DISPOSITION) or include_invalid:
                if variant_cp == label:
                    # Skip original label, yield last
                    original_label = variant_cp, variant_disp, variant_invalid_parts, idx, disp_set, log_output.getvalue()
                else:
                    yield variant_cp, variant_disp, variant_invalid_parts, idx, disp_set, log_output.getvalue()

            if collect_log:
                rule_logger.removeHandler(ch)

        if not original_label:
            # TODO: already computed since label MUST be eligible
            rule_logger.debug('Add original label')
            (_, _, _, disposition, action_idx, log) = self.test_label_eligible(label, collect_log=collect_log)
            original_label = label, disposition, None, action_idx, set(), log

        yield original_label

    def compute_label_disposition_summary(self, label, include_invalid=False, hide_mixed_script_variants=False):
        """
        Given a label compute its disposition and variants along with a summary.

        :param label: The label to compute the disposition of,
                      as a sequence of code points.
                      Label MUST be eligible.
        :param include_invalid: If True, also return variants with "invalid"
                                disposition, which are normally eliminated
                                during the generation process.
        :param hide_mixed_script_variants: Whether we hide mixed scripts variants.
        :return: Generator of (variant_cp, variant_invalid_parts, disp, action_idx, disp_set, log)
                 with:

                     - variant_cp: The code point sequence of a variant.
                     - disp: The disposition of the variant.
                     - variant_invalid_parts: List of code points not valid in the LGR.
                     - action_idx: The index of the action
                                   which triggered the disposition.
                     - disp_set: The disposition set generated for this label.
                     - log: The log of the generation of the label.
        """

        # We have to resolve _ALL_ labels here...
        # This might cause some issues with memory/time computation.
        label_dispositions = list(self.compute_label_disposition(label,
                                                                 include_invalid=include_invalid,
                                                                 hide_mixed_script_variants=hide_mixed_script_variants))

        summary = collections.Counter([disp for (_, disp, _, _, _, _)
                                       in label_dispositions])
        return summary, label_dispositions

    def estimate_variant_number(self, label, hide_mixed_script_variants=False):
        """
        Given a label, return the estimated number of variants.

        This function basically takes a label and return the maximum number of projected variants.

        :param label: The label to compute the disposition of,
                      as a sequence of code points.
        :param hide_mixed_script_variants: Whether we count mixed scripts variants.
        :return: Estimated number of generated variants.
        """
        (_, _, _, chars) = self._test_preliminary_eligibility(label, generate_chars=True)
        variant_number = 1

        def vars_excl_reflexive(current_char):
            return [v for v in current_char.get_variants() if v.cp != current_char.cp]

        if hide_mixed_script_variants:
            try:
                mixed_script_filter = MixedScriptsVariantFilter(label, self.repertoire, unidb=self._unicode_database)
            except NotInLGR:
                return 0
            for char in chars:
                variant_number *= len(
                    [v for v in vars_excl_reflexive(char) if mixed_script_filter.cp_in_base_scripts(v.cp)]
                ) + 1  # Take into account original code point
            for script in mixed_script_filter.other_scripts:
                other_script_number = 1
                for char in chars:
                    other_script_number *= len(
                        [v for v in vars_excl_reflexive(char) if mixed_script_filter.cp_in_scripts(v.cp, {script})]
                    )
                variant_number += other_script_number
        else:
            for char in chars:
                variant_number *= len(vars_excl_reflexive(char)) + 1  # Take into account original code point
        return variant_number

    def generate_index_label(self, label):
        """
        Generate the "index label" of a given label.

        The "index label" is used to test for collisions between 2 labels.
        It associates to a code point an index of the set formed by the code point and its variants.

        For more details, see Section 8.5 of RFC7940.

        Pre-requires: Symmetric and transitive LGR.

        :param label: The label to compute the disposition of, as a sequence of code points.

        :return: The index label, as a list and the index computed with minimum code point algorithm if required.
        :raises NotInLgr: If the label is not in the LGR
                          (does not pass preliminary eligibility testing).
        :raises RuleError: If rule is invalid.
        """
        logger.debug("Generating index label for '%s'", format_cp(label))

        (result, _, not_in_lgr, chars) = self._test_preliminary_eligibility(label,
                                                                            generate_chars=True)
        if not result:
            logger.error('Label %s is not in LGR', format_cp(label))
            # If not result, there is at least on element in not_in_lgr.
            # See _test_preliminary_eligibility()
            raise NotInLGR(not_in_lgr[0][0])

        index_label = []
        for char in chars:
            logger.debug('Char CP: %s', format_cp(char.cp))
            # Index: smallest id of the char and its variants
            # FIXME: This index algorithm has some problems when dealing with sequences and should be fixed
            ids = [char.as_index()]
            for var in char.get_variants():
                var_char = self.repertoire.get_char(var.cp)
                logger.debug('Variant CP: %r', var_char)
                ids.append(var_char.as_index())
            logger.debug('List of variant ids: %s', ids)

            index_label.append(min(ids))

        logger.debug("Index label: '%s'", index_label)

        return tuple(index_label)

    def all_tags(self):
        """
        Returns all known tags used in this LGR.
        """
        prefix_len = len(TAG_CLASSNAME_PREFIX)
        out = []
        for clsname in self.classes_lookup:
            if clsname.startswith(TAG_CLASSNAME_PREFIX):
                out.append(clsname[prefix_len:])
        return out

    def get_rfc7940_validation(self, policy=None, verbose=False):
        """
        Return the result of RFC7940 compliance checks.

        The validation will be "PASS", "WARN", or "FAIL". The validation result
        will be based on tests that have been performed prior to this call.
        Each single test may either succeed or fail. Tests that have not been
        performed will be assumed to have failed.

        A policy may be given to control what tests should have been performed
        and how to evaluate the result. The result will be:
         - PASS if all test cases in the policy have been executed and any
                failed test case has policy "IGNORE"
         - WARN if all test cases have been executed, one or more failed test
                case has policy "WARNING", and all other failed test cases has
                policy "IGNORE"
         - FAIL otherwise
        If no policy is given, the result will be FAIL if any of the hitherto
        run tests have failed, PASS otherwise.

        :param policy: A dict. Each key is a string, which should be the label
                       of a test case that has been run. The value shall be
                       IGNORE if test case failure should be ignored,  WARNING
                       if test case failure should give a warning, and ERROR
                       if test case must succeed.
        :param verbose: If False, return only validation as a string. Otherwise
                        return a log with result of each test.
        :return: The validation as a string.
        """
        return self.metadata.rfc7940_checks.get_final_result(policy, verbose)

    def notify_error(self, test_label):
        """
        Notify that a test case against RFC7940 has failed.

        Called during parsing or validation of the LGR table if a test case
        is found to have failed.

        :param test_label: The label of the test case.
        """
        self.metadata.rfc7940_checks.error(test_label)

    def notify_tested(self, test_label):
        """
        Notify that a test case against RFC7940 has been executed.

        Called during parsing or validation of the LGR table after a test case
        has been thoroughly checked. If notify_error hasn't been called at least
        once with the same label, the test will be assummed to have succeeded.

        :param test_label: The label of the test case.
        """
        self.metadata.rfc7940_checks.tested(test_label)

    def get_tag_classes(self):
        """
        Return the list of "tag-classes" used in this LGR.

        :return: {tag name -> class} mapping.
        """
        prefix_len = len(TAG_CLASSNAME_PREFIX)
        out = {}
        for clsname, clz in self.classes_lookup.items():
            if clsname.startswith(TAG_CLASSNAME_PREFIX):
                out[clsname[prefix_len:]] = clz
        return out

    def populate_variants(self):
        """
        Add missing variants code points and fix symmetry and transitivity
        """
        logger.debug('Populate LGR variants')
        return populate_lgr(self)

    def _test_preliminary_eligibility(self, label, generate_chars=False):
        """
        Test label eligibility against an LGR.

        A label is eligible if each of its code point is in the LGR.

        :param label: The label to test, as an array of codepoints.
        :param generate_chars: Return list of corresponding char objects.
        :return: (result, label_parts, label_invalid_parts, chars), with:

                 * result: True if the label is eligible according to the LGR,
                           False otherwise.
                 * label_parts: List of the code points valid in the LGR.
                 * label_invalid_parts: List of (code point, rule_specs) not valid in the LGR, with:
                    * rule_specs: None if code point is not in the repertoire, list of rule names that does not comply
                                  for all characters starting with the code point.
                 * chars: List of the LGR chars included in label
                          (only if generate_chars=True).
        :raises RuleError: If rule is invalid.
        """
        rule_logger.debug("Testing label '%s'", format_cp(label))
        i = 0
        label_length = len(label)

        label_parts = []
        label_invalid_parts = []

        chars = []

        result = True

        while i < label_length:
            cp = label[i]
            rule_logger.debug("Code point: '%s'", format_cp(cp))

            try:
                # Get the list of all char starting with this codepoint
                char_list = self.repertoire.get_chars_from_prefix(cp)
            except NotInLGR:
                rule_logger.warning("No character in LGR starting with '%s'",
                                    format_cp(cp))
                result = False
                label_invalid_parts.append((cp, None))
                i += 1
                continue

            pending_rules_not_in_lgr = []

            valid = False
            for char in char_list:
                if isinstance(char, CharSequence):
                    if not char.is_prefix_of(label[i:]):
                        continue

                # Test when/not-when rules:
                if not self._test_context_rules(char, label, i):
                    pending_rules_not_in_lgr.append(char.when or char.not_when)
                    continue

                i += len(char)
                valid = True
                rule_logger.debug("Code point '%s' in LGR", format_cp(cp))
                label_parts += char.cp
                chars.append(char)
                break

            if not valid:
                rule_logger.warning("Code point '%s' does not comply with contextual rules: %s",
                                    format_cp(cp), ','.join(pending_rules_not_in_lgr))
                result = False
                label_invalid_parts.append((cp, pending_rules_not_in_lgr or None))
                i += 1

        if not generate_chars:
            return result, label_parts, label_invalid_parts
        else:
            return result, label_parts, label_invalid_parts, chars

    def _test_label_disposition(self, label, apply_reflexive_mapping=True):
        """
        Compute the final disposition of a label.

        This function iterates through the reflexive variants of a label,
        collects the disposition types, and apply the defined actions.

        :param label: Input label to test.
                      Must have passed the 'preliminary' eligibility test.
        :param apply_reflexive_mapping: Whether the reflexive mapping should be considereed for disposition
                                        (This should be True when evaluating a variant)
        :return: - original_disp: The final disposition of the original label.
                 - action_idx: The index of the action which triggered
                               the disposition.
        :raises RuleError: If a rule is invalid.
        """
        # Note: This function duplicate some code
        # from _test_preliminary_eligibility and both of them could be merged in
        # the same code but it feel cleaner to keep them separate.

        rule_logger.info("Testing disposition of label %s", format_cp(label))

        # Init to True so we can use simple test. Need a final check before use
        only_variants = True

        # Store all disposition of reflexive mappings
        disp_set = set()

        for i in range(len(label)):
            cp = label[i]
            rule_logger.debug("Code point: '%s'", format_cp(cp))

            try:
                # Get the list of all char starting with this codepoint
                char_list = self.repertoire.get_chars_from_prefix(cp)
            except NotInLGR:
                rule_logger.info("No character in LGR starting with '%s'", cp)
                # Don't care that code point is not in LGR:
                # We know that label is valid, so it must be a code point
                # sequence which was collected when considering the
                # first code point of the sequence.
                continue

            for char in char_list:
                if isinstance(char, CharSequence):
                    if not char.is_prefix_of(label[i:]):
                        continue

                # Test when/not-when rules:
                if not self._test_context_rules(char, label, i):
                    continue

                is_variant = False

                if apply_reflexive_mapping:
                    for var in char.get_reflexive_variants():
                        if not self._test_context_rules(var, label, i):
                            continue

                        rule_logger.debug('Reflexive variant %s is valid', var)
                        # Reflexive variant is valid, add disposition
                        disp_set.add(var.type)

                        is_variant = True

                # Label is composed of variants only if
                # * current char has a valid variant
                # * previous chars had variants
                only_variants &= is_variant

        # Variants where encountered only if disp set is not empty
        only_variants = only_variants if len(disp_set) > 0 else False

        rule_logger.info("Label '%s' gave reflexive mapping "
                          "with disposition set %s",
                          format_cp(label), disp_set)
        rule_logger.info("Label '%s' gave reflexive mapping "
                          "with only variants: %s",
                          format_cp(label), only_variants)

        return self._apply_actions(label, disp_set, only_variants)

    def _get_prefix_list(self, label, label_prefix):
        """
        Generate the list of characters with same prefix.

        Given a label and some other parameters, return the list
        of the characters in the LGR which can be used as base to generate
        the variants of a label.

        :param label: The label to generate the variants of.
        :param label_prefix: The prefix of the label.
        :return: list of valid prefix characters.
        """
        prefix_list = []
        for prefix in self.repertoire.get_chars_from_prefix(label[0],
                                                            only_variants=True):
            # Ensure prefix is valid for label
            if not prefix.is_prefix_of(label):
                continue

            # Generate "prefixed label":
            # label prefix + variant code point + label 'suffix'
            # label suffix is obtained by removing
            # the prefix code points from the label.
            prefixed_label = label_prefix + prefix.cp + tuple(label[len(prefix):])

            # Test when/not-when rules on prefixed_label
            if not self._test_context_rules(prefix,
                                            prefixed_label,
                                            len(label_prefix)):
                rule_logger.debug('No context rule')
                continue

            prefix_list.append(prefix)

        return prefix_list

    def _generate_label_variants(self, label,
                                 orig_label=None, label_prefix=None,
                                 has_variant=False,
                                 mixed_script_filter: BaseMixedScriptsVariantFilter = None,
                                 hide_mixed_script_variants=False):
        """
        Generate a list of all the variants for a given label.

        Takes a label as input, and output the _variants_ of the label.
        If there is no code point with at least one variant defined,
        then the output is empty.
        Output may contain the reflexive variant of a label, if any reflexive
        mapping is defined and valid in the label context.

        :param label: The label to generate the variants of,
                      as a sequence of code points.
        :param orig_label: The full original label,
                           used when evaluating when/not-when rules
                           (used for recursion).
        :param label_prefix: The prefix of the label (used for recursion).
        :param has_variant: True if the prefix has at least one variant
                            (used for recursion).
        :param mixed_script_filter: Filter for mixed script (used for recursion).
        :param hide_mixed_script_variants: Whether we hide mixed scripts variants.
        :return: A generator of (variant_cp, variant_disp, only_variants),
                 with:

                    * variant_cp: sequence of the variant code points.
                    * disp_set: set of the dispositions obtained
                                during the generation of the variant.
                    * only_variant: True if variant_cp only contains variant
                                    code points. Used for action triggering
                                    ('only-variants' attribute).
        :raises RuleError: If rule is invalid.
        """
        rule_logger.debug("Generate variants for label %s", format_cp(label))
        rule_logger.debug("Original label: %s", format_cp(orig_label))
        rule_logger.debug("Prefix: %s", format_cp(label_prefix))
        rule_logger.debug("Has Variant: %s", has_variant)

        # current `label` will be consumed by recursion,
        # so need to save the original.
        first_call = False
        if orig_label is None:
            first_call = True
            orig_label = label
        if label_prefix is None:
            label_prefix = tuple()

        if len(label) == 0:
            rule_logger.debug("Empty label")
            return

        if hide_mixed_script_variants and not mixed_script_filter:
            mixed_script_filter = MixedScriptsVariantFilter(label, self.repertoire, unidb=self._unicode_database)

        try:
            same_prefix = self._get_prefix_list(label, label_prefix)
        except NotInLGR:
            rule_logger.debug('Char is not in LGR,'
                              'assume we are handling a sequence')
            # This is not an error: we might be handling code points
            # belonging to a sequence which is being decomposed by the
            # variant generation process.
            # The sequence is part of the LGR,
            # but not the individual code points.
            same_prefix = []
        else:
            if len(same_prefix) == 0:
                # No code point in LGR with variants,
                # stick to first one found (longest in label)
                for cp in self.repertoire.get_chars_from_prefix(label[0]):
                    if cp.is_prefix_of(label):
                        same_prefix = [cp]
                        break

        for char in [ch for ch in same_prefix if isinstance(ch, CharSequence)]:
            # char is a sequence, if first code point of the sequence is in the LGR we need to consider it
            for cp in self.repertoire.get_chars_from_prefix(label[0]):
                if len(cp) < len(char) and cp.is_prefix_of(label):
                    same_prefix.append(cp)

        # Iterate through characters matching the start of the label
        for char in same_prefix:
            rule_logger.debug("Char %s", format_cp(char.cp))

            has_reflexive_mapping = False
            # List of character permutations,
            # including original character (see below)
            # Format: (cp, (type list), is variant?)
            char_perms = []

            for var in char.get_variants():
                script_filter: BaseMixedScriptsVariantFilter = mixed_script_filter
                rule_logger.debug("Variant %s", format_cp(var.cp))

                # Generate variant label:
                # label prefix + variant code point + label 'suffix'
                # label suffix is obtained by removing
                # the variant code point from the label.
                variant_label = label_prefix + var.cp + tuple(label[len(char):])

                if hide_mixed_script_variants:
                    if first_call and mixed_script_filter.cp_in_other_scripts(var.cp):
                        rule_logger.debug("Variant script is eligible for non mixed-scripts", format_cp(var.cp))
                        script_filter = mixed_script_filter.get_filter_for_other_script(
                            self.unicode_database.get_script(var.cp[0]))
                    elif not mixed_script_filter.cp_in_base_scripts(var.cp):
                        rule_logger.debug("Variant %s contains mixed-scripts", format_cp(var.cp))
                        continue
                # Test when/not-when rules - Use variant label
                if not self._test_context_rules(var,
                                                variant_label,
                                                len(label_prefix)):
                    rule_logger.debug("Variant %s is not in LGR", format_cp(var.cp))
                    continue
                rule_logger.debug("Variant %s is valid", format_cp(var.cp))

                if var.type is None:
                    var_disp = frozenset()
                else:
                    var_disp = frozenset([var.type])

                if var.cp == char.cp:
                    has_reflexive_mapping = True
                char_perms.append((var.cp, var_disp, True, script_filter))

            # Add original code point in permutation list
            # ONLY if the character has no defined reflexive mapping.
            # Otherwise, it is already part of the list,
            # with appropriate type:
            # From RFC7940, section 5.3.4.  Variants with Reflexive Mapping
            # In permuting the label to generate all possible variants,
            # the type associated with a reflexive variant mapping
            # is applied to any of the permuted labels containing
            # the original code point.
            # Also ignore char that are not part of the label in the current script if required
            if not has_reflexive_mapping and (not hide_mixed_script_variants or first_call or
                                              mixed_script_filter.cp_in_base_scripts(char.cp)):
                char_perms.insert(0, (char.cp, frozenset(), False, mixed_script_filter))

            if len(label) > len(char):
                for (cp, disp, is_variant, script_filter) in char_perms:
                    # Generate variants for reminder of label
                    for (perm_cps, perm_disp, perm_only_variants) in \
                            self._generate_label_variants(label[len(char):],
                                                          orig_label,
                                                          label_prefix + cp,
                                                          # Mark if prefix is part of a variant
                                                          is_variant | has_variant,
                                                          mixed_script_filter=script_filter,
                                                          hide_mixed_script_variants=hide_mixed_script_variants):
                        yield (cp + perm_cps,
                               # Construct new set of types
                               perm_disp | disp,
                               is_variant & perm_only_variants)
            elif has_variant or char.has_variant():
                # Do not output the same un-permuted label
                # TODO for consistency another or condition should be added:
                #          or orig_label != label_prefix + char.cp
                #      in order to include the original label in output in case the last char has no variants which
                #      won't be the case without this condition
                for (cp, disp, is_variant, _) in char_perms:
                    yield cp, disp, is_variant

    def _apply_actions(self, label, disp_set, only_variants):
        """
        Apply the defined action of an LGR to a label and its dispositions.

        Implement 8.3 Determining a Disposition for a Label or Variant Label,
        step 1.

        :param label: The label to process, as a sequence of code points.
        :param disp_set: Set of dispositions used to generate the label.
        :param only_variants: True if label only contains code point
                              from variant mapping.
        :return: The final label disposition and the action index
                 Index includes default actions, ie
                 if index > len(self.actions): action == DEFAULT_ACTION[index - len(actions)]
        :raises RuleError: If rule is invalid.
        """

        action_list = self.effective_actions
        idx = 0
        for action in action_list:
            rule_logger.info("Apply action %d (%s)",
                             action_list.index(action), action)
            disp = action.apply(label, disp_set, only_variants,
                                self.rules_lookup, self.classes_lookup,
                                self._unicode_database,)
            if disp is not None:
                rule_logger.info("Action %d (%s) triggered",
                                  action_list.index(action),
                                  action)
                return disp, idx

            idx += 1

        # Should not happen since last DEFAULT_ACTIONS is a catch-all
        rule_logger.warning("No action triggered by label '%s' "
                            "with disposition set '%s'", label, disp_set)
        return None, -1

    def _test_context_rules(self, char, orig_label, index):
        """
        Test if context rules apply to the character.

        :param char: The current character to test.
        :param orig_label: The original label the character is a part of.
        :return: True if context rules apply (or none defined), False otherwise.
        :raises RuleError: If rule is invalid.
        """
        when = char.when
        not_when = char.not_when

        if when is not None:
            rule = self.rules_lookup[when]
            if not rule.matches(orig_label,
                                self.rules_lookup,
                                self.classes_lookup,
                                self._unicode_database,
                                char.cp,
                                index):
                rule_logger.info("when rule '%s' does not validate for code point '%s'",
                                 when, format_cp(char.cp))
                return False
        elif not_when is not None:
            rule = self.rules_lookup[not_when]
            if rule.matches(orig_label,
                            self.rules_lookup,
                            self.classes_lookup,
                            self._unicode_database,
                            char.cp,
                            index):
                rule_logger.info("not-when rule '%s' validates for code point '%s'",
                                 not_when, format_cp(char.cp))
                return False

        return True

    def _check_convert_cp(self, cp_or_sequence, assert_in_script=False):
        """
        Check validity of code point input.

        Check the validity of a code point input, and convert it to iterable
        format used internally.

        :param cp_or_sequence: Code point or sequence to modify in the LGR.
                               Can be either:

                                   - An int (code point)
                                   - A list (non-empty)
        :param assert_in_script: If True, ensure that the added code point
                                 is in one of the LGR's scripts.
        :returns: Input argument to internally used format.
        :raises LGRApiInvalidParameter: If cp_or_sequence is empty list,
                                        or non-supported input type.
        :raises CharInvalidIdnaProperty: If cp_or_sequence is or contains
                                         an invalid IDNA2008 code point.
        :raises CharNotInScript: If cp_or_sequence is not in LGR's scripts.

        >>> from munidata.database import IDNADatabase
        >>> unidb = IDNADatabase('6.3.0')
        >>> lgr = LGR(unicode_database=unidb)
        >>> lgr._check_convert_cp([]) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        LGRApiInvalidParameter:
        >>> lgr._check_convert_cp(0x0061) == [0x0061]
        True
        >>> lgr._check_convert_cp(dict()) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        LGRApiInvalidParameter:
        >>> lgr._check_convert_cp(0) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        CharInvalidIdnaProperty:
        >>> lgr._check_convert_cp(3.14) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        LGRApiInvalidParameter:
        """
        if isinstance(cp_or_sequence, int):
            # If input is unique code point as int,
            # convert it to list
            cp_or_sequence = [cp_or_sequence]
        else:
            try:
                if len(cp_or_sequence) < 1:
                    # Iterable type must have at least one code point
                    logger.error("Code point list is empty")
                    raise LGRApiInvalidParameter('cp_or_sequence')
            except TypeError:
                # Invalid format for input argument
                logger.error("Invalid format for code point '%s'",
                             cp_or_sequence)
                raise LGRApiInvalidParameter('cp_or_sequence')

        if self.unicode_database is not None:
            _, invalid_cps = is_idna_valid_cp_or_sequence(cp_or_sequence, self.unicode_database, check_all=True)
            for cp in invalid_cps.keys():
                # Check IDNA properties - This check cannot be overridden
                logger.error("Code point %s is not IDNA-valid", format_cp(cp))
                if self.raise_on_invalid_property:
                    raise CharInvalidIdnaProperty(cp)
            in_script, _ = self.cp_in_script(cp_or_sequence)
            if assert_in_script:
                raise CharNotInScript(cp_or_sequence)

        return cp_or_sequence

    def cp_in_script(self, codepoints):
        """
        Given a code point or code point sequence, return if the code point is in
        one of the LGR's scripts and the code point script.

        Assume the LGR has a proper unicode_database set.

        :param codepoints: List of code points.
        :return: (in_script, cp_script) with:
                 - in_script: True if cp_or_sequence is in LGR's scripts, False otherwise.
                 - cp_scripts: cp_or_sequence's scripts.
        """
        in_script = True
        cp_scripts = set()
        lgr_scripts = self.metadata.get_scripts()
        for cp in codepoints:
            try:
                script = self.unicode_database.get_script(cp, alpha4=True)
                cp_scripts.add(script)
                if len(lgr_scripts) > 0 and script not in lgr_scripts:
                    logger.debug("Code point '%s' (script %s) not in LGR script '%s'",
                                 format_cp(cp), script, lgr_scripts)
                    in_script = False
            except NotImplementedError:
                # get_script() not implemented in all munidata's databases.
                pass

        return in_script, cp_scripts

    def _insert_list(self, codepoints, comment=None,
                     ref=None, tag=None,
                     when=None, not_when=None):
        """
        Utility function to insert a list of code points in a LGR.

        The function will extract ranges from the list and add them to the LGR.
        All other code points will be added as single value code point.
        This function is very similar to what add_codepoints() does
        but is more low-level and only intended for internal use.

        :param codepoints: List of code points.
        :param comment: Comment associated to the range.
        :param ref: List of references associated to the code point.
        :param tag: List of tags associated to the code point.
        :param when: Condition to be satisfied by the code point.
        :param not_when: Condition to not be satisfied by the codepoint.


        >>> lgr = LGR()
        >>> lgr._insert_list(range(0x0061, 0x007A))
        """
        logger.debug('Add code points to LGR %s', self)

        ranges = collapse_codepoints(codepoints)
        for (first_cp, last_cp) in ranges:
            if first_cp == last_cp:
                # Single code point
                self.repertoire.add_char([first_cp],
                                         comment=comment,
                                         ref=ref, tag=tag,
                                         when=when, not_when=not_when)
            else:
                self.repertoire.add_range(first_cp, last_cp,
                                          comment=comment,
                                          ref=ref, tag=tag,
                                          when=when, not_when=not_when,
                                          skip_check=True)

    def _add_cp_to_tag_classes(self, cp_or_sequence, tags):
        """
        Add a code point to tag classes.

        Tag classes are internal virtual classes used to list the code points
        by tags.

        :param cp_or_sequence: Sequence of code point to add to the classes.
        :param tags: List of tags associated to the code points.
        """
        for tag in tags:
            tag_classname = TAG_CLASSNAME_PREFIX + tag
            self.classes_lookup.setdefault(tag_classname,
                                           Class(name=tag,
                                                 comment="Virtual class for tag %s" % tag,
                                                 implicit=True)).add_codepoint(cp_or_sequence)

    def _del_cp_from_tag_classes(self, cp_or_sequence, tags):
        """
        Remove a code point from tag classes.

        Tag classes are internal virtual classes used to list the code points
        by tags.

        :param cp_or_sequence: Sequence of code point to remove from the classes.
        :param tags: List of tags associated to the code points.
        """
        for tag in tags:
            tag_classname = TAG_CLASSNAME_PREFIX + tag
            if tag_classname in self.classes_lookup:
                self.classes_lookup[tag_classname].del_codepoint(cp_or_sequence)

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


if __name__ == "__main__":
    import doctest

    logger.addHandler(logging.NullHandler())
    doctest.testmod()
