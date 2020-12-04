#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
utils - tool utils
"""
import argparse
import logging
import sys

from lgr.parser.xml_parser import XMLParser
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
