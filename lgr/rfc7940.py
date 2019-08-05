# -*- coding: utf-8 -*-
# Author: Viagénie
"""
rfc7940.py - Test an LGR against RFC7940.
"""
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class LGRFormatTestResults(object):
    """
    Aggregator for results of test cases against RFC7940
    """
    test_desciption = dict(
        parse_xml='The LGR table can be parsed successfully',
        validity_end_expiry='The "validity-end" element (if present) in the metadata section is in future time',
        validity_start_end='The "validity-start" element in the metadata section is earlier in time than the "validity-end" element (if both are present)',
        validity_started='The "validity-start" element (if present) in the metadata section is in past time',
        metadata_description_type='The "type" attribute of the description element (if present) in the metadata section is a valid media type',
        metadata_scope_type='The "type" attribute of the scope element (if present) in the metadata section has a valid value',
        metadata_language='The value of each "language" element is a valid language tag as described in RFC5646',
        metadata_version_integer='The value of the "version" element (if present) in the metadata section is the decimal representation of a positive integer',
        data_variant_type='The value of the "type" attribute (if present) of each "variant" element is a non-empty value not starting with an underscore and not containing spaces',
        explicit_unicode_version='The Unicode version is set in the "version" element in the metadata section',
        valid_unicode_version='The Unicode version is a valid Unicode version 5.2.0 or higher',
        codepoint_valid='All code points in the LGR are included in the given Unicode version',
        char_ascending_order='All "char" elements are listed in ascending order of the "cp" attribute',
        char_strict_ascending_order='All "char" elements are listed in strictly ascending order of the "cp" attribute',
        ref_attribute_ascending='Reference identifiers given in the "ref" attribute are listed in ascending order (if all are integers)',
        standard_dispositions='All dispositions are registered Standard Dispositions',
        basic_symmetry='All variant relations are symmetric',
        strict_symmetry='All variant relations are symmetric and agree in their "when" or "not-when" attributes',
        basic_transitivity='All variant relations are transitive',
        strict_transitivity='All variant relations are transitivity and agree in their "when" or "not-when" attributes',
    )

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
