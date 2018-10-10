# -*- coding: utf-8 -*-
"""
metadata.py - Definition of Metadata object.
"""
from __future__ import unicode_literals

import re
import mimetypes
import datetime
from language_tags import tags as rfc5646
import logging
from collections import OrderedDict

from lgr.exceptions import (LGRFormatException,
                            ReferenceAlreadyExists,
                            ReferenceNotDefined)
from lgr.memoize import MethodAttributeMemoizer
from lgr.utils import script_iso15924_to_unicode

logger = logging.getLogger(__name__)

# Initializes mimetypes module
mimetypes.init()


def _validate_date(date, force):
    """
    Ensure the date is a valid ISO 8601 "full-date" string.

    :param str date: Date to validate, as a string.
    :param force: If True, do not raise exception on error.
    :return: date input.
    :raises LGRFormatException: If the date parameter
                                has an invalid format.

    >>> _validate_date('2015-06-25', False) == '2015-06-25'
    True
    >>> _validate_date('2015-13-26', False) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    LGRFormatException
    >>> _validate_date('2015', False) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    LGRFormatException
    """

    # Date shoud be date-fullyear "-" date-month "-" date-mday
    date_elements = date.split('-')
    if len(date_elements) == 3:
        try:
            date_elements = [int(d) for d in date_elements]
            date_object = datetime.date(date_elements[0],
                                        date_elements[1],
                                        date_elements[2])
            if date_object.isoformat() == date:
                return date
        except ValueError:
            logger.log(logging.WARNING if force else logging.ERROR,
                       "Invalid date format: '%s'", date)
            if force:
                return date
            else:
                raise LGRFormatException(LGRFormatException.
                                         LGRFormatReason.INVALID_DATE_TAG)

    logger.log(logging.WARNING if force else logging.ERROR,
               "Invalid date format: '%s'", date)
    if force:
        return date
    else:
        raise LGRFormatException(LGRFormatException.
                                 LGRFormatReason.INVALID_DATE_TAG)


class Version(object):
    """
    Version object.

    Used to store a version number and an optional comment.
    """

    def __init__(self, value, comment=None):
        self.value = value
        self.comment = comment

    def __unicode__(self):
        return self.value


class Scope(object):
    """
    Scope object.

    Used to store a scope value and an optional type.
    """

    def __init__(self, value, scope_type=None):
        self.value = value
        self.scope_type = scope_type

    def __unicode__(self):
        return '{}: {}'.format(self.scope_type, self.value)

    def __eq__(self, other):
        return (self.value == other.value) \
               and (self.scope_type == other.scope_type)

    def __hash__(self):
        return hash((self.value, self.scope_type))


class Description(object):
    """
    Description object.

    Used to store a description value and an optional type.

    3.3.5.  The description Element
    The element has an optional "type" attribute, which refers to the
    internet media type of the enclosed data.  Typical types would be
    "text/plain" or "text/html".  The attribute SHOULD be a valid MIME
    type.
    """

    def __init__(self, value, description_type=None):
        self.value = value
        if description_type not in mimetypes.types_map.values():
            logger.warning("Description type '%s' is not a valid MIME type",
                           description_type)
        self.description_type = description_type


class Metadata(object):
    """
    LGR metadata encapsulation object.
    """

    def __init__(self, error_policy=None):
        self.version = None
        self.date = None
        self.languages = []
        self.scopes = []
        self.validity_start = None
        self.validity_end = None
        self.unicode_version = '6.3.0'
        self.description = None
        if error_policy is None:
            self.error_policy = ErrorPolicy()
        else:
            self.error_policy = error_policy

    # Note: This method is memoized since it is called very often during the
    # LGR._check_convert_cp(), which ensure the CP is part of the declared
    # scripts.
    # Not caching results of this function results in the MSR taking ~90sec to
    # be parsed instead of ~1sec.
    # The cache depends on the value of the "languages" attribute.
    @MethodAttributeMemoizer("languages")
    def get_scripts(self):
        """
        Retrieve the scripts defined in the metadata.

        :return: The list alpha4 scripts of defined languages.
        """
        scripts = []
        for language in self.languages:
            lang_tag = rfc5646.tag(language)
            if lang_tag.valid:
                iso_script_tag = lang_tag.script
                if iso_script_tag is not None:
                    iso_script = iso_script_tag.format
                    scripts += script_iso15924_to_unicode(iso_script)
        return scripts

    def add_language(self, language, force=False):
        """
        Add a language handled by the LGR to the metadata list.

        Ensure the language is a valid RFC 5646 language tag.

        3.3.3.  The language Element
        The value of the "language"
        element MUST be a valid language tag as described in [RFC5646].

        :param str language: A new language of the LGR.
        :param bool force: If True, add the language even if format is invalid.
        :raises LGRFormatException: if the language parameter
                                    has an invalid format.
        """
        try:
            if not rfc5646.check(language):
                logger.log(logging.WARNING if force else logging.ERROR,
                           "Invalid language: '%s'", language)
                self.error_policy.error("metadata_language")
                if not force:
                    raise LGRFormatException(LGRFormatException.
                                             LGRFormatReason.INVALID_LANGUAGE_TAG)
            self.error_policy.tested("metadata_language")
            self.languages.append(language)
        except UnicodeEncodeError:
            # Can't skip this one
            logger.error("Invalid non-ASCII language tag '%s'", language)
            self.error_policy.error("metadata_language")
            raise LGRFormatException(LGRFormatException.
                                     LGRFormatReason.INVALID_LANGUAGE_TAG)

    def set_languages(self, languages, force=False):
        """
        Convenience function to update the languages in the metadata.

        :param iterable languages: a collection of language tags as described in [RFC5646].
        :param bool force: If True, add the languages even if format is invalid.
        :raises LGRFormatException: if the language parameter
                                    has an invalid format.
        """
        # check all languages
        found_error = False
        for language in languages:
            try:
                if not rfc5646.check(language):
                    logger.log(logging.WARNING if force else logging.ERROR,
                               "Invalid language: '%s'", language)
                    found_error = True
            except UnicodeEncodeError:
                # Can't skip this one
                logger.error("Invalid non-ASCII language tag '%s'", language)
                languages.remove(language)

        if found_error and not force:
            raise LGRFormatException(LGRFormatException.
                                     LGRFormatReason.INVALID_LANGUAGE_TAG)
        else:
            self.languages = list(languages)

    def set_date(self, date, force=False):
        """
        Set the date of the LGR.

        Ensure the date is a valid ISO 8601 "full-date" string.

        3.3.2.  The date Element
        The contents of this element MUST be a valid ISO 8601 "full-
        date" string as described in [RFC3339].

        :param str date: Date to use, as a string.
        :param bool force: If True, set the date even if format is invalid.
        :raises LGRFormatException: If the date parameter
                                    has an invalid format.
        """
        self.date = _validate_date(date, force)

    def set_validity_start(self, date, force=False):
        """
        Set the validity-start of the LGR.

        Ensure the date is a valid ISO 8601 "full-date" string.

        3.3.6.  The validity-start and validity-end Elements
        The dates MUST confirm to the "full-date" format described in section
        5.6 of [RFC3339].

        :param str date: Date to use, as a string.
        :param bool force: If True, set the date even if format is invalid.
        :raises LGRFormatException: If the date parameter
                                    has an invalid format.
        """
        self.validity_start = _validate_date(date, force)

    def set_validity_end(self, date, force=False):
        """
        Set the validity-end of the LGR.

        Ensure the date is a valid ISO 8601 "full-date" string.

        3.3.6.  The validity-start and validity-end Elements
        The dates MUST confirm to the "full-date" format described in section
        5.6 of [RFC3339].

        :param str date: Date to use, as a string.
        :param bool force: If True, set the date even if format is invalid.
        :raises LGRFormatException: If the date parameter
                                    has an invalid format.
        """
        self.validity_end = _validate_date(date, force)

    def set_unicode_version(self, unicode_version, force=False):
        """
        Set the unicode-version of the LGR.

        Ensure the unicode_version is a valid x.y.z string.

        3.3.7.  The unicode-version Element
        the version number used in creating the LGR
        MUST be listed in the form x.y.z, where x, y, and z are positive,
        decimal integers (see [Unicode-Versions]).

        :param str unicode_version: The Unicode version.
        :param bool force: If True, set the date even if format is invalid.
        :raises LGRFormatException: If the unicode_version parameter
                                    has an invalid format.
        """

        if re.match(r'\d{1,}\.\d{1,}\.\d{1,}', unicode_version) is None:
            logger.log(logging.WARNING if force else logging.ERROR,
                       "Invalid Unicode version: '%s'", unicode_version)
            if not force:
                raise LGRFormatException(LGRFormatException.
                                         LGRFormatReason.
                                         INVALID_UNICODE_VERSION_TAG)

        self.unicode_version = unicode_version


class ReferenceManager(OrderedDict):
    """
    LGR references manager.

    Store and delete references.
    References are indexed by their id, which is stored as a string.

    RFC7940 section 4.3.8.  The "references" Element specifies that:

        It is RECOMMENDED that the "id" attribute be a zero-based integer.

    so if no ref_id is given, generate one int-based id, converted to string.
    """

    def __init__(self, *args, **kwargs):
        super(ReferenceManager, self).__init__(*args, **kwargs)
        # Keep track of the next id to generate
        self.next_id = 0

    def __contains__(self, k):
        return super(ReferenceManager, self).__contains__(str(k))

    def __getitem__(self, k):
        return super(ReferenceManager, self).__getitem__(str(k))

    def __setitem__(self, k, v):
        return super(ReferenceManager, self).__setitem__(str(k), v)

    def __delitem__(self, k):
        return super(ReferenceManager, self).__delitem__(str(k))

    def add_reference(self, value, comment=None, ref_id=None):
        """
        Add a reference to the manager.

        :param value: Value of the reference.
        :param comment: Optional comment.
        :param ref_id: Optional reference id to use.
        :return str: The id used for the reference as string.
        :raises ReferenceAlreadyExists: if ref_id is provided,
                                        and a reference with this id
                                        already exists.

        >>> mgr = ReferenceManager()
        >>> mgr.add_reference("Test") == '0'
        True
        >>> mgr.add_reference("Test 2", ref_id=42) == '42'
        True
        >>> mgr.add_reference("Test Existing", ref_id=0) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ReferenceAlreadyExists
        """
        # Construct reference object (simple dict)
        reference = {
            'value': value
        }
        if comment is not None:
            reference['comment'] = comment

        if ref_id is not None:
            # Check if ref_id already exists
            if ref_id in self:
                logger.error("Reference '%s' already exists", ref_id)
                raise ReferenceAlreadyExists(ref_id)
        else:
            # Compute next id
            next_id = self.next_id
            while str(next_id) in sorted(self):
                next_id += 1
            self.next_id = next_id
            ref_id = next_id

        logger.debug("Insert new reference '%s' with id '%s'",
                     value, ref_id)

        self[ref_id] = reference

        return str(ref_id)

    def del_reference(self, ref_id):
        """
        Delete a reference from the list.

        :param ref_id: Id of the reference to delete.
        :raises ReferenceNotDefined: If the ref_id is not defined.

        >>> mgr = ReferenceManager()
        >>> ref_id = mgr.add_reference("Test 1")
        >>> mgr.del_reference(ref_id)
        >>> mgr.add_reference("Test 2", ref_id=ref_id) == '0'
        True
        """
        if ref_id not in self:
            logger.error("Reference '%s' does not exist", ref_id)
            raise ReferenceNotDefined(ref_id)

        del self[ref_id]

        # Update next id if needed - only for int-based ids
        try:
            ref_id = int(ref_id)
            if ref_id < self.next_id:
                self.next_id = ref_id
        except ValueError:
            pass

    def update_reference(self, ref_id, value=None, comment=None):
        """
        Update a reference.

        :param ref_id: Reference id to update.
        :param value: Value of the reference.
        :param comment: Comment of the reference.

        :raises ReferenceNotDefined: If the ref_id is not defined.
        """
        if ref_id not in self:
            logger.error("Reference '%s' does not exist", ref_id)
            raise ReferenceNotDefined(ref_id)

        ref = self[ref_id]
        if value is not None:
            ref['value'] = value
        if comment is not None:
            ref['comment'] = comment
