#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
utils - tool utils
"""
import argparse
import io
import logging
import sys

from lgr.parser.xml_serializer import serialize_lgr_xml

from lgr.parser.xml_parser import XMLParser
from lgr.tools.utils import merge_lgrs
from munidata import UnicodeDataVersionManager

logger = logging.getLogger(__name__)


def parse_lgr(xml, rng=None, unidb=None):
    lgr_parser = XMLParser(xml)
    if unidb:
        lgr_parser.unicode_database = unidb

    if rng is not None:
        validation_result = lgr_parser.validate_document(rng)
        if validation_result is not None:
            logger.error('Errors for RNG validation of LGR file %s: %s', xml, validation_result)
            return

    lgr = lgr_parser.parse_document()
    return lgr


class LgrToolArgParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(LgrToolArgParser, self).__init__(*args, **kwargs)
        self.args = None
        self.unidb = None

    def add_common_args(self):
        self.add_logging_args()
        self.add_libs_arg()
        self.add_rng_arg()

    def add_logging_args(self):
        self.add_argument('-v', '--verbose', action='store_true',
                          help='be verbose')
        self.add_argument('-q', '--quiet', action='store_true',
                          help='Be quiet (no details, no log)')

    def add_libs_arg(self, required=True):
        self.add_argument('-l', '--libs', metavar='LIBS',
                          help='ICU libraries', required=required)

    def add_unicode_arg(self):
        self.add_argument('-u', '--unicode', metavar='Unicode',
                          default='6.3.0', help='Unicode version', )

    def add_rng_arg(self):
        self.add_argument('-r', '--rng', metavar='RNG',
                          help='RelaxNG XML schema')

    def add_xml_meta(self):
        self.add_argument('xml', metavar='XML')

    def parse_args(self, *args, **kwargs):
        if not self.args:
            self.args = super(LgrToolArgParser, self).parse_args(*args, **kwargs)

        return self.args

    def setup_logger(self):
        if not self.args:
            self.parse_args()
        # "Disable" logging in test mode except if we ask to be verbose
        log_level = logging.DEBUG if self.args.verbose else logging.INFO
        if self.args.test and not self.args.verbose:
            log_level = logging.ERROR
        if self.args.quiet:
            log_level = logging.CRITICAL
        logging.basicConfig(stream=sys.stderr, level=log_level,
                            format="%(levelname)s:%(name)s [%(filename)s:%(lineno)s] %(message)s")

    def parse_lgr(self):
        if not self.args:
            self.parse_args()

        return parse_lgr(self.args.xml or self.args.lgr_xml, self.args.rng, self.get_unidb())

    def get_unidb(self):
        if not self.args:
            self.parse_args()
        if self.args.libs and not self.unidb:
            libpath, i18n_libpath, libver = self.args.libs.split('#')
            manager = UnicodeDataVersionManager()
            self.unidb = manager.register(None, libpath, i18n_libpath, libver)
        return self.unidb


class LgrSetToolArgParser(LgrToolArgParser):

    def __init__(self, *args, **kwargs):
        super(LgrSetToolArgParser, self).__init__(*args, **kwargs)
        self.merged_lgr = None
        self.script_lgr = None
        self.set_labels = None
        self.lgr = None

    def add_xml_set_args(self):
        self.add_argument('-x', '--lgr-xml', metavar='LGR_XML', action='append', required=True,
                          help='The LGR or LGR set if used multiple times')
        self.add_argument('-s', '--lgr-script', metavar='LGR_SCRIPT',
                          help='If LGR is a set, the script used to validate input labels')
        self.add_argument('-f', '--set-labels', metavar='SET_LABELS',
                          help='If LGR is a set, the file containing the label of the LGR set')

    def process_set(self, optional_set_labels):
        if len(self.args.lgr_xml) > 1:
            if not self.args.lgr_script:
                logger.error('For LGR set, lgr script is required')
                return

            if not optional_set_labels and not self.args.set_labels:
                logger.error('For LGR set, LGR set labels file is required')
                return

            self.merged_lgr, lgr_set = merge_lgrs(self.args.lgr_xml,
                                                  rng=self.args.rng,
                                                  unidb=self.get_unidb())
            if not self.merged_lgr:
                logger.error('Error while creating the merged LGR')
                return

            self.set_labels = io.StringIO()
            if self.args.set_labels:
                with io.open(self.args.set_labels, 'r', encoding='utf-8') as set_labels_input:
                    self.set_labels = io.StringIO(set_labels_input.read())

            self.script_lgr = None
            for lgr_s in lgr_set:
                try:
                    if lgr_s.metadata.languages[0] == self.args.lgr_script:
                        if self.script_lgr:
                            logger.warning('Script %s is provided in more than one LGR of the set, '
                                           'will only evaluate with %s', self.args.lgr_script, lgr_s.name)
                        self.script_lgr = lgr_s
                except (AttributeError, IndexError):
                    pass

            if not self.script_lgr:
                logger.error('Cannot find script %s in any of the LGR provided as input', self.args.lgr_script)
                return
        else:
            self.lgr = parse_lgr(self.args.lgr_mxml[0], self.args.rng, self.get_unidb())
            if self.lgr is None:
                logger.error("Error while parsing LGR file.")
                logger.error("Please check compliance with RNG.")
                return

        return True


class LgrDumpTool(LgrToolArgParser):

    def __init__(self, rfc_parser_cls, *args, **kwargs):
        super(LgrDumpTool, self).__init__(*args, **kwargs)
        self.rfc_parser_cls = rfc_parser_cls

    def run(self):
        self.add_logging_args()
        self.add_argument('-o', '--output', metavar='OUTPUT',
                            help='Optional output file')
        self.add_argument('file', metavar='FILE')

        self.parse_args()
        self.setup_logger()

        rfc_parser = self.rfc_parser_cls(self.args.file)
        lgr = rfc_parser.parse_document()

        if self.args.output is not None:
            xml = serialize_lgr_xml(lgr, pretty_print=True)
            with io.open(self.args.output, mode='wb') as output:
                output.write(xml)
        else:
            print(serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False))