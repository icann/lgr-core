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
    def __init__(self, cp, rule=None):
        super(CharInvalidContextRule, self).__init__(cp)
        self.rule = rule


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


class ReferenceInvalidId(LGRException):
    """
    Raised when trying to create a reference invalid id.
    """
    def __init__(self, ref_id):
        super(ReferenceInvalidId, self).__init__()
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

    __str__ = __unicode__


class MissingLanguage(LGRException):
    """
    Raised when the LGR has no language while it is expected
    """
    def __init__(self, message):
        super(MissingLanguage, self).__init__(message)
        self.message = message


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


class LGRCrossScriptMissingDataException(LGRException):
    """
    Raise when cross script variant cannot be computed due to missing data in LGR
    """
    def __init__(self, missing_part):
        super(LGRCrossScriptMissingDataException, self).__init__()
        self.missing_part = missing_part


class LGRFormatTestResults(object):
    """
    Aggregator for results of test cases against RFC7940
    """
    test_desciption = dict(
        parse_xml = 'The LGR table can be parsed successfully',
        validity_end_expiry = 'The "validity-end" element (if present) in the metadata section is in future time',
        validity_start_end = 'The "validity-start" element in the metadata section is earlier in time than the "validity-end" element (if both are present)',
        validity_started = 'The "validity-start" element (if present) in the metadata section is in past time',
        metadata_description_type = 'The "type" attribute of the description element (if present) in the metadata section is a valid media type',
        metadata_scope_type = 'The "type" attribute of the scope element (if present) in the metadata section has a valid value',
        metadata_language = 'The value of each "language" element is a valid language tag as described in RFC5646',
        metadata_version_integer = 'The value of the "version" element (if present) in the metadata section is the decimal representation of a positive integer',
        data_variant_type = 'The value of the "type" attribute (if present) of each "variant" element is a non-empty value not starting with an underscore and not containing spaces',
        explicit_unicode_version = 'The Unicode version is set in the "version" element in the metadata section',
        valid_unicode_version = 'The Unicode version is a valid Unicode version 5.2.0 or higher',
        codepoint_valid = 'All code points in the LGR are included in the given Unicode version',
        char_ascending_order='All "char" elements are listed in ascending order of the "cp" attribute',
        char_strict_ascending_order = 'All "char" elements are listed in strictly ascending order of the "cp" attribute',
        ref_attribute_ascending = 'Reference identifiers given in the "ref" attribute are listed in ascending order (if all are integers)',
        standard_dispositions = 'All dispositions are registered Standard Dispositions',
        basic_symmetry = 'All variant relations are symmetric',
        strict_symmetry = 'All variant relations are symmetric and agree in their "when" or "not-when" attributes',
        basic_transitivity = 'All variant relations are transitive',
        strict_transitivity = 'All variant relations are transitivity and agree in their "when" or "not-when" attributes',
    );

    def __init__(self):
        self.test_result = dict()

    def error(self, test_label):
        """
        Notify that a test case has failed.

        :param test_label: The label of the test case.
        """
        self.add_test_result(test_label, False)

    def tested(self, test_label):
        """
        Notify that a test case has been executed.

        The test case will be considered to have failed if error has been called
        for the same test case; otherwise it will be considered to have
        succeeded.

        :param test_label: The label of the test case.
        """
        self.add_test_result(test_label, True)

    def add_test_result(self, test_label, success):
        # Ignore successful result if the test case has already been run
        """
        Notify that a test case has been executed.

        The test case will be considered to have failed if error has been called
        for the same test case or if the value of success is False; otherwise it
        will be considered to have succeeded.

        :param test_label: The label of the test case.
        """

        if not success or test_label not in self.test_result:
            self.test_result[test_label] = success

    def get_final_result(self, policy=None, verbose=False):
        """
        Calculate the validation result based on policy and test results.

        The final result will be:
         - PASS if all test cases in the policy have been executed and any failed
                test case has policy "IGNORE"
         - WARN if all test cases have been executed, one or more failed test case has
                policy "WARNING", and all other failed test cases has policy "IGNORE"
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
        if policy is None:
            if False in self.test_result.values():
                return "FAIL"
            return "PASS"

        info = ""
        got_warning = False
        got_error = False
        for test in policy:
            desc = LGRFormatTestResults.test_desciption.get(test, test)
            if test not in self.test_result:
                got_error = True
                if verbose:
                    info += "ERROR: " + desc + " - NOT EXECUTED\n"
            elif not self.test_result[test]:
                p = policy[test]
                if p == "IGNORE":
                    if verbose:
                        info += "IGNORE: " + desc + " - NOK\n"
                elif p == "WARNING":
                    got_warning = True
                    if verbose:
                        info += "WARNING: " + desc + " - NOK\n"
                else:
                    got_error = True
                    if verbose:
                        info += "ERROR: " + desc + " - NOK\n"
            else:
                if verbose:
                    info += "PASS: " + desc + " - OK\n"

        if verbose:
            info += "Validation result: "
        if got_error:
            info += "FAIL"
        elif got_warning:
            info += "WARN"
        else:
            info += "PASS"
        return info
