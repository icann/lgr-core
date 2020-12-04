#!/bin/env python
# -*- coding: utf-8 -*-
"""
lgr_cli.py - Small CLI tool to exercise the LGR API.

Can parse an LGR XML file, and make some checks/display some data.
"""
from __future__ import unicode_literals

import logging

from lgr import wide_unichr
from lgr.tools.utils import write_output, get_stdin
from lgr.utils import cp_to_ulabel
from tools.utils import LgrToolArgParser

logger = logging.getLogger("lgr_cli")


def check_label(lgr, label, invalid, test):
    from lgr.utils import format_cp
    label_cp = tuple([ord(c) for c in label])
    label_display = ' '.join("{:04X}".format(cp) for cp in label_cp)

    logger.info("- Code points: %s", label_display)

    (eligible, label_parts, label_invalid_parts, disp, action_idx, logs) = lgr.test_label_eligible(label_cp)
    logger.info("- Eligible: %s", eligible)
    logger.info("- Disposition: %s", disp)
    is_default_action = action_idx > len(lgr.actions)
    actual_index = action_idx if not is_default_action else action_idx - len(lgr.actions)
    action_name = "DefaultAction" if is_default_action else "Action"
    logger.info("- Action triggered: %s[%d]", action_name, actual_index)
    logger.info("- Logs: %s", logs)
    write_output("Validation: {} ({}): Result: {}".format(label, label_display, "valid" if eligible else "INVALID"),
                 test)

    if eligible:
        write_output("Disposition: {} ({}): Result: {} due to {}[{}]".format(label, label_display, disp,
                                                                             action_name, actual_index), test)

        summary, labels = lgr.compute_label_disposition_summary(label_cp,
                                                                include_invalid=invalid)
        logger.info("Summary: %s", summary)
        for (variant_cp, var_disp, variant_invalid_parts, action_idx, disp_set, logs) in labels:
            variant_u = cp_to_ulabel(variant_cp)
            variant_display = ' '.join("{:04X}".format(cp) for cp in variant_cp)
            logger.info("\tVariant '%s'", variant_u)
            logger.info("\t- Code points: %s", format_cp(variant_cp))
            logger.info("\t- Disposition: '%s'", var_disp)

            if variant_invalid_parts:
                logger.info("\t- Invalid code points from variant: %s",
                            ' '.join(("{:04X} ({})".format(cp,
                                                           "not in repertoire" if rules is None else ','.join(rules))
                                      for cp, rules in variant_invalid_parts)))

            is_default_action = action_idx > len(lgr.actions)
            actual_index = action_idx if not is_default_action else action_idx - len(lgr.actions)
            action_name = "DefaultAction" if is_default_action else "Action"
            logger.info("\t- Action triggered: %s[%d]", action_name, actual_index)
            disp_set_display = '{%s}' % ','.join(disp_set)
            write_output("Variant: ({}): [{}] ==> {} due to {}[{}]".format(variant_display, disp_set_display, var_disp,
                                                                           action_name, actual_index), test)

            logger.info("\t- Logs: %s", logs)
    else:
        logger.info("- Valid code points from label: %s",
                    ' '.join("{:04X}".format(cp) for cp in label_parts))
        logger.info("- Invalid code points from label: %s",
                    ' '.join(("{:04X} ({})".format(cp, "not in repertoire" if rules is None else ','.join(rules)) for
                              cp, rules in label_invalid_parts)))


def main():
    from lgr.parser.xml_parser import XMLParser

    parser = LgrToolArgParser(description='LGR CLI')
    parser.add_common_args()
    parser.add_argument('-m', '--msr', metavar='MSR',
                        help='Validating repertoire')
    parser.add_argument('-u', '--unicode', metavar='Unicode',
                        default='6.3.0', help='Unicode version')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Enable automatic test mode')
    parser.add_argument('-c', '--check', action='store_true',
                        help='Enable label checking')
    parser.add_argument('-i', '--invalid', action='store_true',
                        help='Do not filter out "invalid" labels')
    parser.add_xml_meta()
    parser.add_argument('label', metavar='LABEL', nargs='?')

    args = parser.parse_args()
    parser.setup_logger()

    unidb = parser.get_unidb()

    msr = None
    if args.msr is not None:
        msr_parser = XMLParser(args.msr)
        msr = msr_parser.parse_document()

    lgr = parser.parse_lgr()
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

    if args.check:
        if args.label:
            label_u = ''.join(wide_unichr(int(cphex, 16)) for cphex in args.label.split())
            check_label(lgr, label_u, args.invalid, args.test)
        else:
            for label in get_stdin().read().splitlines():
                logger.info("Label '%s'", label)
                check_label(lgr, label, args.invalid, args.test)


if __name__ == '__main__':
    main()
