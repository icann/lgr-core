#!/bin/env python2
# -*- coding: utf-8 -*-
"""
lgr_cli.py - Small CLI tool to exercise the LGR API.

Can parse an LGR XML file, and make some checks/display some data.
"""
import sys
import codecs
import argparse
import logging

from munidata import UnicodeDataVersionManager

from lgr.tools.utils import write_output

logger = logging.getLogger("lgr_cli")


def check_label(lgr, label, invalid, test):
    from lgr.utils import format_cp
    label_cp = tuple([ord(c) for c in label])
    label_display = u' '.join(u"{:04X}".format(cp) for cp in label_cp)

    logger.info("- Code points: %s", label_display)

    (eligible, label_part, not_in_lgr, disp, action_idx, logs) = lgr.test_label_eligible(label_cp)
    logger.info("- Eligible: %s", eligible)
    logger.info("- Disposition: %s", disp)
    is_default_action = action_idx > len(lgr.actions)
    actual_index = action_idx if not is_default_action else action_idx - len(lgr.actions)
    action_name = "DefaultAction" if is_default_action else "Action"
    logger.info("- Action triggered: %s[%d]", action_name, actual_index)
    logger.info("- Logs: %s", logs)

    write_output(u"Validation: {} ({}): Result: {}".format(label,
                                                           label_display,
                                                           "valid" if eligible else "INVALID"),
                 test)

    if eligible:
        write_output(u"Disposition: {} ({}): Result: {} due to {}[{}]".format(label, label_display, disp, action_name, actual_index),
                     test)

        summary, labels = lgr.compute_label_disposition_summary(label_cp,
                                                                include_invalid=invalid)
        logger.info("Summary: %s", summary)
        for (variant_cp, var_disp, action_idx, disp_set, logs) in labels:
            variant_u = ''.join([unichr(c) for c in variant_cp])
            variant_display = u' '.join(u"{:04X}".format(cp) for cp in variant_cp)
            logger.info("\tVariant '%s'", variant_u)
            logger.info("\t- Code points: %s", format_cp(variant_cp))
            logger.info("\t- Disposition: '%s'", var_disp)

            is_default_action = action_idx > len(lgr.actions)
            actual_index = action_idx if not is_default_action else action_idx - len(lgr.actions)
            action_name = "DefaultAction" if is_default_action else "Action"
            logger.info("\t- Action triggered: %s[%d]", action_name, actual_index)
            disp_set_display = '{%s}' % ','.join(disp_set)
            write_output(u"Variant: ({}): [{}] ==> {} due to {}[{}]".format(variant_display, disp_set_display, var_disp, action_name, actual_index),
                         test)

            logger.info("\t- Logs: %s", logs)
    else:
        logger.info("- Valid code points from label: %s",
                    u' '.join(u"{:04X}".format(cp) for cp in label_part))
        logger.info("- Invalid code points from label: %s",
                    u' '.join(u"{:04X}".format(cp) for cp in not_in_lgr))


def main():
    from lgr.parser.xml_parser import XMLParser

    parser = argparse.ArgumentParser(description='LGR CLI')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-r', '--rng', metavar='RNG',
                        help='RelaxNG XML schema')
    parser.add_argument('-m', '--msr', metavar='MSR',
                        help='Validating repertoire')
    parser.add_argument('-l', '--libs', metavar='LIBS',
                        help='ICU libraries')
    parser.add_argument('-u', '--unicode', metavar='Unicode',
                        default='6.3.0', help='Unicode version')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Enable automatic test mode')
    parser.add_argument('-c', '--check', action='store_true',
                        help='Enable label checking')
    parser.add_argument('-i', '--invalid', action='store_true',
                        help='Do not filter out "invalid" labels')
    parser.add_argument('xml', metavar='XML')
    parser.add_argument('label', metavar='LABEL', nargs='?')

    args = parser.parse_args()

    # "Disable" logging in test mode except if we ask to be verbose
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if args.test and not args.verbose:
        log_level = logging.ERROR
    logging.basicConfig(stream=sys.stderr, level=log_level,
                        format="%(levelname)s:%(name)s "
                        "[%(filename)s:%(lineno)s] %(message)s")

    lgr_parser = XMLParser(args.xml)

    unidb = None
    if args.libs is not None:
        libpath, i18n_libpath, libver = args.libs.split('#')
        manager = UnicodeDataVersionManager()
        unidb = manager.register(None, libpath, i18n_libpath, libver)

    if args.rng is not None:
        validation_result = lgr_parser.validate_document(args.rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation: %s', validation_result)

    msr = None
    if args.msr is not None:
        msr_parser = XMLParser(args.msr)
        msr = msr_parser.parse_document()

    if unidb is not None:
        lgr_parser.unicode_database = unidb

    lgr = lgr_parser.parse_document()
    if lgr is None:
        logger.error("Error while parsing LGR file.")
        logger.error("Please check compliance with RNG.")
        return

    options = {
        'validating_repertoire': msr,
        'unicode_version': args.unicode,
    }
    if unidb is not None:
        options['unidb'] = unidb

    if not args.test:
        summary = lgr.validate(options)
        logger.info('Result of validation: %s', summary)

    label_input = codecs.getreader('utf8')(sys.stdin)

    if args.check:
        if args.label:
            label_u = ''.join(unichr(int(cphex, 16)) for cphex in args.label.split())
            check_label(lgr, label_u, args.invalid, args.test)
        else:
            for label in label_input.read().splitlines():
                logger.info("Label '%s'", label)
                check_label(lgr, label, args.invalid, args.test)

if __name__ == '__main__':
    main()
