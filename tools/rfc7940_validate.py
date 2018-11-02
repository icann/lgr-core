#!env python
# -*- coding: utf-8 -*-
"""
rfc7940_validate.py - Check compliance with rfc7940.

Parse an LGR XML file, and report rfc7940 compliance.
"""
import sys
import argparse
import logging

import lgr
import munidata

logger = logging.getLogger("rfc7940_validate")

def main():
    from lgr.parser.xml_parser import XMLParser

    parser = argparse.ArgumentParser(description='check rfc7940 compliance')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Be quiet (no details, no log)')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries')
    parser.add_argument('-u', '--unicode', metavar='Unicode',
                        default='6.3.0', help='Unicode version')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Enable automatic test mode')
    parser.add_argument('xml', metavar='XML')

    args = parser.parse_args()

    # "Disable" logging in test mode except if we ask to be verbose
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if args.test and not args.verbose:
        log_level = logging.ERROR
    if args.quiet:
        log_level = logging.CRITICAL
    logging.basicConfig(stream=sys.stderr, level=log_level,
                        format="%(levelname)s:%(name)s [%(filename)s:%(lineno)s] %(message)s")

    lgr_parser = XMLParser(args.xml, force_mode=False)

    unidb = None
    if args.libs is not None:
        libpath, i18n_libpath, libver = args.libs.split('#')
        manager = munidata.UnicodeDataVersionManager()
        unidb = manager.register(None, libpath, i18n_libpath, libver)

    if unidb is not None:
        lgr_parser.unicode_database = unidb

    try:
        lgr = lgr_parser.parse_document()
    except:
        lgr = None

    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    options = {
        'unicode_version': args.unicode,
        'rfc7940': True
    }
    if unidb is not None:
        options['unidb'] = unidb

    if args.rng is not None:
        options['rng_filepath'] = args.rng
        validation_result = lgr_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation: %s', validation_result)

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
    )

    full_report = not args.quiet

    final_result = lgr.get_rfc7940_validation(policy, verbose=full_report)

    sys.stdout.write(final_result)
    sys.stdout.write("\n")

if __name__ == '__main__':
    main()
