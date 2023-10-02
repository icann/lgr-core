# -*- coding: utf-8 -*-
"""
utils - List of utility functions for tools.
"""
from __future__ import unicode_literals

import argparse
import codecs
import io
import logging
import os
import sys
from io import BytesIO
from urllib.parse import urlparse
from urllib.request import urlopen

from lgr import text_type
from lgr.parser.xml_parser import XMLParser
from lgr.parser.xml_serializer import serialize_lgr_xml
from lgr.tools.merge_set import merge_lgr_set
from lgr.utils import cp_to_ulabel
from munidata import UnicodeDataVersionManager

logger = logging.getLogger(__name__)


def read_labels(input, unidb=None, do_raise=False, keep_commented=False, as_cp=False, return_exceptions=False):
    """
    Read a label file and format lines to get a list of correct labels

    :param input: Input label list as an iterator of Unicode strings.
    :param unidb: The UnicodeDatabase
    :param do_raise: Whether the label parsing exceptions are raised or not
    :param keep_commented: Whether commented labels are returned (still commented) or not
    :param as_cp: If True, returns a list of code points per label. Otherwise, unicode string.
    :param return_exceptions: If True, returns the exception instead of an error string
    :return: [(original label, parsed label, valid, error)]
    """
    def clean(l):
        try:
            l = l.lstrip(codecs.BOM_UTF8.decode('utf-8'))
        except:
            pass
        return l.strip()

    # remove comments
    for label in input:
        label = clean(label)
        if '#' in label:
            pos = label.find('#')
            if pos == 0:
                if keep_commented:
                    yield label, label, True, ''
                continue
            label = label[:pos].strip()
        if len(label) == 0:
            continue

        error = ''
        parsed_label = ''
        valid = True
        # transform U-label and A-label in unicode strings
        try:
            if unidb:
                parsed_label = parse_label_input(label, idna_decoder=unidb.idna_decode_label, as_cp=as_cp)
            else:
                parsed_label = parse_label_input(label, as_cp=as_cp)
        except BaseException as ex:
            if do_raise:
                raise
            valid = False
            error = ex if return_exceptions else text_type(ex)
        yield label, parsed_label, valid, error


def parse_single_cp_input(s):
    """
    Parses a single code points from user input

    :param s: input
    :return: code point

    >>> parse_single_cp_input('z') == ord('z')  # treat single character as a character
    True
    >>> parse_single_cp_input('1') == ord('1')  # treat single character as a character, even if it is numeric
    True
    >>> parse_single_cp_input('a') == ord('a')  # treat single character as a character, even if it looks like hex
    True

    >>> parse_single_cp_input('U+1')  # U+ always treated as hex
    1
    >>> parse_single_cp_input('u+1')  # U+ can be lowercase
    1
    >>> parse_single_cp_input(' u+1')  # leading space ok
    1
    >>> parse_single_cp_input('u+1 ')  # trailing space ok
    1
    >>> parse_single_cp_input(' u+1 ')  # leading and trailing spaces ok
    1
    >>> parse_single_cp_input('U+10')
    16
    >>> parse_single_cp_input('U+10ffff') == 0x10FFFF
    True
    >>> parse_single_cp_input('U+10FFFF') == 0x10FFFF
    True
    >>> parse_single_cp_input('U+110000')  # overflow
    Traceback (most recent call last):
    ...
    ValueError: code point value must be in the range [0, U+10FFFF]
    >>> parse_single_cp_input('U+')  # short # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for int() with base 16: ''
    >>> parse_single_cp_input('0061 0062')  # too many values # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for int() with base 16: '0061 0062'
    """
    s = s.strip()
    if len(s) == 1:
        # unicode char
        return ord(s)
    else:
        if s[:2].upper() == 'U+':
            # U+XXXX
            v = int(s[2:], 16)
        else:
            v = int(s, 16)

        # check bounds
        if v < 0 or v > 0x10FFFF:
            raise ValueError("code point value must be in the range [0, U+10FFFF]")

        return v


def parse_codepoint_input(s):
    """
    Parses a code point or sequence of code points from user input

    :param s: input
    :return: list of code points

    >>> parse_codepoint_input('0061')
    [97]
    >>> parse_codepoint_input('0061 0062')
    [97, 98]
    >>> parse_codepoint_input('0061    0062')
    [97, 98]

    >>> parse_codepoint_input('a')
    [97]
    >>> parse_codepoint_input('a b')
    [97, 98]

    >>> parse_codepoint_input('U+0061 U+0062')
    [97, 98]
    >>> parse_codepoint_input('U+0061 0062')
    [97, 98]
    """
    return [parse_single_cp_input(x) for x in s.split()]


def parse_label_input(s, idna_decoder=lambda x: x.encode('utf-8').decode('idna'), as_cp=True):
    """
    Parses a label from user input, applying a bit of auto-detection smarts

    :param s: input string in A-label, U-label or space-separated hex sequences.
    :param idna_decoder: IDNA decode function.
    :param as_cp: If True, returns a list of code points. Otherwise, unicode string.
    :return: list of code points

    >>> parse_label_input('0061')  # treated as U-label - probably the only confusing result
    [48, 48, 54, 49]
    >>> parse_label_input('U+0061')  # this is how to signal that you want hex
    [97]
    >>> parse_label_input('abc')
    [97, 98, 99]
    >>> parse_label_input('a b c')
    [97, 98, 99]
    >>> parse_label_input('xn--m-0ga')  # "öm"
    [246, 109]
    """
    if s.lower().startswith('xn--'):
        if as_cp:
            return [ord(c) for c in idna_decoder(s.lower())]
        else:
            return idna_decoder(s.lower())
    elif ' ' in s or 'U+' in s.upper():
        try:
            label_cp = parse_codepoint_input(s)
        except:
            if ' ' in s:
                raise ValueError("Label '{}' contains spaces "
                                 "that are not PVALID for IDNA2008".format(s))
            raise
        if as_cp:
            return label_cp
        else:
            return cp_to_ulabel(label_cp)
    else:
        # treat as unicode
        if as_cp:
            return [ord(c) for c in s]
        else:
            return s


def merge_lgrs(input_lgrs, name=None, rng=None, unidb=None):
    """
    Merge LGRs to create a LGR set

    :param input_lgrs: The LGRs belonging to the set
    :param name: The merged LGR name
    :param rng: The RNG file to validate input LGRs
    :param unidb: The unicode database
    :return: The merged LGR and the LGRs in the set.
    """
    lgr_set = []
    for lgr_file in input_lgrs:
        lgr_parser = XMLParser(lgr_file)
        if unidb:
            lgr_parser.unicode_database = unidb

        if rng:
            validation_result = lgr_parser.validate_document(rng)
            if validation_result is not None:
                logger.error('Errors for RNG validation of LGR %s: %s',
                             lgr_file, validation_result)

        lgr = lgr_parser.parse_document()
        if lgr is None:
            logger.error("Error while parsing LGR file %s." % lgr_file)
            logger.error("Please check compliance with RNG.")
            return

        lgr_set.append(lgr)

    if not name:
        name = 'merged-lgr-set'

    merged_lgr = merge_lgr_set(lgr_set, name)
    if unidb:
        merged_lgr.unicode_database = unidb

    return merged_lgr, lgr_set


# Helpers for CLI tools


def write_output(s, test=True):
    if test:
        if sys.version_info.major > 2:
            print(s)
        else:
            print(s.encode('utf-8'))


def get_stdin():
    if sys.version_info.major > 2:
        # Python3 automagically convert to unicode
        return sys.stdin
    else:
        return codecs.getreader('utf8')(sys.stdin)


def download_file(source_url):
    base_url = urlparse(source_url).path
    filename = os.path.basename(base_url)
    with urlopen(source_url) as resp:
        logger.debug("Retrieve %s at URL %s", filename, source_url)
        data = BytesIO(resp.read())

    return filename, data


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
        log_level = logging.DEBUG if self.args.verbose else logging.INFO
        # "Disable" logging in test mode except if we ask to be verbose
        if hasattr(self.args, 'test') and self.args.test and not self.args.verbose:
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
