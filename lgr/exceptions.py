# -*- coding: utf-8 -*-
"""
exceptions.py - Define all exceptions used in the LGR module.
"""
from __future__ import unicode_literals


class LGRException(Exception):
    """
    Base class for all LGR-related exceptions.
    """

    def __str__(self):
        return self.__class__.__name__


class LGRApiException(LGRException):
    """
    Base class for all LGR-API-related exceptions.
    """
    pass


class LGRApiInvalidParameter(LGRApiException):
    """
    Raised when an API parameter is invalid or has an invalid format.
    """
    def __init__(self, parameter):
        super(LGRApiInvalidParameter, self).__init__()
        self.parameter = parameter


class LGRFormatException(LGRException):
    """
    Raised when encountering some element which does not follow the LGR format.
    """

    class LGRFormatReason(object):
        """
        List of reasons which can trigger the exception.
        """
        # From RFC7940, section 5. Code Points and Variants
        # A "range" element has no child elements.
        RANGE_NO_CHILD = 0
        # From RFC7940, section 5.5. Code Point Tagging:
        # It is an error to duplicate a value within the same "tag" attribute.
        DUPLICATE_TAG = 1
        # From RFC7940, section 5.5. Code Point Tagging:
        # a "tag" attribute MUST NOT be present in a "char" element
        # defining a code point sequence.
        SEQUENCE_NO_TAG = 2
        # From RFC7940, section 4.3.3. The "language" Element:
        # The value of the "language" element MUST be a valid language tag
        # as described in [RFC5646].
        INVALID_LANGUAGE_TAG = 3
        # From RFC7940, section 4.3.2. The "date" Element:
        # The contents of this element MUST be a valid ISO 8601 "full-
        # date" string as described in [RFC3339]
        INVALID_DATE_TAG = 4
        # From RFC7940, section 3.3.7. The "unicode-version" Element:
        # the version number used in creating the LGR
        # MUST be listed in the form x.y.z, where x, y, and z are positive,
        # decimal integers (see [Unicode-Versions]).
        INVALID_UNICODE_VERSION_TAG = 5
        # From RFC7940, section 6.2.1. Declaring and Invoking Named Classes
        # The "by-ref" attribute MUST NOT be used in
        # the same "class" element with any of these attributes: "name",
        # "from-tag", "property", or "ref".
        # From RFC7940, section 6.3.4. The "name" and "by-ref" Attributes
        # The "by-ref" attribute MUST NOT appear in the same element as the
        # "name" attribute or in an element that has any child elements.
        BY_REF_AND_OTHER = 6
        # From RFC7940, section 6.2.1. Declaring and Invoking Named Classes
        # It is an error to reference a named class for which the definition has
        # not been seen.
        INVALID_BY_REF = 7
        # From RFC7940, section 6.2.1. Declaring and Invoking Named Classes
        # The "name" attribute MUST be present if and only if the class
        # is a direct child element of the "rules" element.
        INVALID_TOP_LEVEL_NAME = 8
        # From RFC7940, section 6.2.5. Combined Classes
        # The elements from this table may be arbitrarily nested inside each
        # other, subject to the following restriction: a "complement" element
        # MUST contain precisely one "class" or one of the operator elements,
        # while an "intersection", "symmetric-difference" or "difference"
        # element MUST contain precisely two, and a "union" element MUST
        # contain two or more of these elements.
        INVALID_CHILDREN_NUMBER = 9
        # From RFC7940, section 7.1. The "match" and "not-match" Attributes
        # An action MUST NOT contain both a "match" and a "not-match"
        # attribute
        MATCH_NOT_MATCH = 10

    def __init__(self, reason):
        super(LGRFormatException, self).__init__()
        self.reason = reason


class CharLGRException(LGRException):
    """
    Base class for all character-related exceptions.
    """
    def __init__(self, cp):
        super(CharLGRException, self).__init__()
        self.cp = cp


class CharInvalidContextRule(CharLGRException):
    """
    Raised when adding a char with invalid context rule(s).
    """
    pass


class CharInvalidIdnaProperty(CharLGRException):
    """
    Raised when trying to manipulate a character which is not valid
    per IDNA 2008.
    """
    pass


class CharNotInScript(CharLGRException):
    """
    Raised when trying to add a character not in the defined script.
    """
    pass


class CharAlreadyExists(CharLGRException):
    """
    Raised when trying to add a character which already exists in a given LGR.
    """
    pass


class RangeException(LGRException):
    """
    Base class for all range-oriented exceptions.
    """
    def __init__(self, first_cp, last_cp):
        super(RangeException, self).__init__()
        self.first_cp = first_cp
        self.last_cp = last_cp


class RangeAlreadyExists(RangeException):
    """
    Raised when trying to add a range which already exists in a given LGR.
    """
    pass


class RangeInvalidContextRule(RangeException):
    """
    Raised when adding a range with invalid context rule(s).
    """
    pass


class VariantException(CharLGRException):
    """
    Base class for all variant-related exceptions.
    """
    def __init__(self, cp, variant):
        super(VariantException, self).__init__(cp)
        self.variant = variant


class VariantAlreadyExists(VariantException):
    """
    Raised when trying to add a variant which already exists for a given
    code point in a LGR.
    """
    pass


class VariantInvalidContextRule(VariantException):
    """
    Raised when adding a variant with invalid context rule(s).
    """
    pass


class NotInRepertoire(CharLGRException):
    """
    Raised when trying to add a character outside the validating repertoire.
    """
    pass


class NotInLGR(CharLGRException):
    """
    Raised when trying to perform some action on a character not in the LGR.
    """
    pass


class DuplicateReference(CharLGRException):
    """
    Raised when an character contains a duplicate reference id.
    """
    pass


class ReferenceNotDefined(LGRException):
    """
    Raised when trying to perform some action on an inexsting reference.
    """
    def __init__(self, ref_id):
        super(ReferenceNotDefined, self).__init__()
        self.ref_id = ref_id


class ReferenceAlreadyExists(LGRException):
    """
    Raised when trying to create a reference which already exists (same id).
    """
    def __init__(self, ref_id):
        super(ReferenceAlreadyExists, self).__init__()
        self.ref_id = ref_id


class InvalidSymmetry(LGRException):
    """
    Raised when symmetry is not ensured.
    """
    pass


class RuleError(LGRException):
    """
    Raised when a rule generates an error.
    """
    def __init__(self, rule_name, message):
        super(RuleError, self).__init__(message)
        self.rule_name = rule_name
        self.message = message

    def __unicode__(self):
        return '<rule %s>: %s' % (self.rule_name, self.message)


class LGRInvalidLabelException(LGRException):
    """
    Raised when a label is invalid in an LGR
    """
    def __init__(self, label, message):
        super(LGRInvalidLabelException, self).__init__()
        self.label = label
        self.message = message


class LGRLabelCollisionException(LGRException):
    """
    Raised when a label collide in an LGR set
    """
    def __init__(self):
        super(LGRLabelCollisionException, self).__init__()
