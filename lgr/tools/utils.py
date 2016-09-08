# -*- coding: utf-8 -*-
"""
utils - List of utility functions for tools.
"""
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


def read_labels(input, unidb):
    """
    Read a label file and format lines to get a list of correct labels

    :param input: The name of the file containing the labels
    :param unidb: The UnicodeDatabase
    :return: The list of labels
    """
    # Compute index label
    labels = map(lambda x: x.strip(), input)

    # remove comments
    for label in labels:
        if '#' in label:
            pos = label.find('#')
            if pos == 0:
                continue
            label = label[:pos].strip()
        if len(label) == 0:
            continue

        # transform U-label and A-label in unicode strings
        try:
            label = parse_label_input(label, unidb.idna_decode_label, False)
        except BaseException as ex:
            label = "{}: {}".format(label, unicode(ex))
        yield label


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
    >>> parse_single_cp_input('U+')  # short
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for int() with base 16: ''
    >>> parse_single_cp_input('0061 0062')  # too many values
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


def parse_label_input(s, idna_decoder=lambda x: x.decode('idna'), as_cp=True):
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
            return ''.join([unichr(c) for c in label_cp])
    else:
        # treat as unicode
        if as_cp:
            return [ord(c) for c in s]
        else:
            return s
