#!/bin/env python
# -*- coding: utf-8 -*-
"""
rfc7940_validate.py - Check compliance with rfc7940.

Parse an LGR XML file, and report rfc7940 compliance.
"""
import logging
import sys

from lgr.tools.utils import LgrToolArgParser

logger = logging.getLogger("rfc7940_validate")


def main():
    parser = LgrToolArgParser(description='check rfc7940 compliance')
    parser.add_common_args()
    parser.add_argument('-u', '--unicode', metavar='Unicode',
                        default='6.3.0', help='Unicode version')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Enable automatic test mode')
    parser.add_xml_meta()

    args = parser.parse_args()
    parser.setup_logger()

    lgr = parser.parse_lgr()
    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        sys.stdout.write("FAIL\n")
        return

    options = {
        'unicode_version': args.unicode,
        'rfc7940': True
    }
    if parser.get_unidb() is not None:
        options['unidb'] = parser.get_unidb()

    if args.rng is not None:
        options['rng_filepath'] = args.rng

    if not args.test:
        summary = lgr.validate(options)
        logger.info('Result of validation: %s', summary)

    policy = dict(
        validity_end_expiry="ERROR",
        validity_start_end="ERROR",
        validity_started="ERROR",
        metadata_description_type="ERROR",
        metadata_scope_type="ERROR",
        metadata_language="ERROR",
        metadata_version_integer="WARNING",
        data_variant_type="ERROR",
        codepoint_valid="ERROR",
        char_ascending_order="WARNING",
        char_strict_ascending_order="IGNORE",
        ref_attribute_ascending="WARNING",
        standard_dispositions="ERROR",
        basic_symmetry="WARNING",
        strict_symmetry="WARNING",
        basic_transitivity="WARNING",
        parse_xml="ERROR",
        schema="ERROR",
    )

    full_report = not args.quiet

    final_result = lgr.get_rfc7940_validation(policy, verbose=full_report)

    sys.stdout.write(final_result)
    sys.stdout.write("\n")


if __name__ == '__main__':
    main()
