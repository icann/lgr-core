# -*- coding: utf-8 -*-
"""
utils.py - Set of utility functions to be used in module.
"""
from __future__ import unicode_literals

import logging

from language_tags import tags
from pycountry import languages

from lgr import text_type, wide_unichr

logger = logging.getLogger(__name__)


VALID_IDNA_PROPERTY_VALUES = set([
    "PVALID",
    "CONTEXTJ",
    "CONTEXTO",
])



def cp_to_ulabel(cp_or_sequence):
    """
    Convert a code point or code point sequence to the corresponding U-label.

    :param cp_or_sequence: Code point/Code point sequence to convert to label.
    :returns: Label composed of the `cp_or_sequence`.

    >>> cp_to_ulabel(0x0061) == text_type('a')
    True
    >>> cp_to_ulabel([0x0061, 0x0062, 0x0063]) == text_type('abc')
    True
    >>> cp_to_ulabel(None) == text_type('None')
    True
    """
    if cp_or_sequence is None:
        return 'None'
    if isinstance(cp_or_sequence, int):
        cp_or_sequence = [cp_or_sequence]
    return ''.join((wide_unichr(c) for c in cp_or_sequence))


def cp_to_str(cp):
    """
    Convert a code point (int) to a string.
    """
    return "%04X" % cp


def format_cp(cp_or_sequence):
    """
    Convert a code point or code point sequence to a string.

    :param cp_or_sequence: Code point/Code point sequence to format.
    :returns: Formatted code point or code point sequence as a string.

    >>> format_cp(1) == text_type('U+0001')
    True
    >>> format_cp([1]) == text_type('U+0001')
    True
    >>> format_cp([1,2,3]) == text_type('U+0001 U+0002 U+0003')
    True
    >>> format_cp(None) == text_type('None')
    True
    """
    if cp_or_sequence is None:
        return 'None'
    if isinstance(cp_or_sequence, int):
        cp_or_sequence = [cp_or_sequence]
    return ' '.join(['U+{0}'.format(cp_to_str(c)) for c in cp_or_sequence])


def format_cp_collapsed(cp_or_sequence):
    """
    Convert a code point or code point sequence to a string.

    :param cp_or_sequence: Code point/Code point sequence to format.
    :returns: Formatted code point or code point sequence as a string.

    >>> format_cp_collapsed(1) == text_type('U+0001')
    True
    >>> format_cp_collapsed([1]) == text_type('U+0001')
    True
    >>> format_cp_collapsed([1,3]) == text_type('U+0001 U+0003')
    True
    >>> format_cp_collapsed([1,2,3]) == text_type('U+0001-U+0003')
    True
    >>> format_cp(None) == text_type('None')
    True
    >>> format_cp_collapsed([1,2,3,5,6,10,12,13,14,15]) == text_type('U+0001-U+0003 U+0005 U+0006 U+000A U+000C-U+000F')
    True
    """
    if cp_or_sequence is None:
        return 'None'

    if isinstance(cp_or_sequence, int):
        cp_or_sequence = [cp_or_sequence]

    collapsed = collapse_codepoints(cp_or_sequence)
    formatted = []
    for start, end in collapsed:
        if start == end:
            formatted.append('U+{0}'.format(cp_to_str(start)))
        elif end == start + 1:
            formatted.extend(['U+{0}'.format(cp_to_str(start)), 'U+{0}'.format(cp_to_str(end))])
        else:
            formatted.append('-'.join(['U+{0}'.format(cp_to_str(start)), 'U+{0}'.format(cp_to_str(end))]))

    return ' '.join(formatted)


def collapse_codepoints(codepoints):
    """
    Convert a list of code points in a list of ranges.

    Given a list of code points, extract the ranges with the maximal length from
    consecutive code points.

    :param: codepoints: List of code points.
    :returns: List of ranges (first_cp, last_cp)

    >>> ranges = collapse_codepoints([1,2,3,4,7,10,11,12,15])
    >>> ranges == [(1,4), (7, 7), (10, 12), (15,15)]
    True
    """
    result = []
    # Sort list
    codepoints = sorted(codepoints)
    first_cp = codepoints[0]
    last_cp = codepoints[0]
    for cp in codepoints[1:]:
        if cp == last_cp + 1:
            # Code point is continuous of last one, extend range
            last_cp = cp
        else:
            # Code point is not successor of last one, create new range
            result.append((first_cp, last_cp))
            first_cp = cp
            last_cp = cp

    result.append((first_cp, last_cp))

    return result


def script_iso15924_to_unicode(script):
    """
    Convert ISO 15924 script code to a list of corresponding Unicode scripts.

    This function aims to map the ISO 15924 script codes to the corresponding
    Unicode scripts.

    :param script: ISO15924 script.
    :return: List of Unicode scripts.
    """
    if script == 'Aran':
        return ['Arab']
    elif script == 'Geok':
        return ['Geor']
    elif script in ['Hans', 'Hant']:
        return ['Hani']
    elif script == 'Hrkt':
        return ['Hira', 'Kana']
    elif script == 'Jpan':
        return ['Hani', 'Hira', 'Kana']
    elif script == 'Kore':
        return ['Hani', 'Hang']
    elif script in ['Latf', 'Latg']:
        return ['Latn']
    elif script in ['Syre', 'Syrj', 'Syrn']:
        return ['Syrc']
    return [script]


def let_user_choose(first, second, separator='|'):
    """
    This function append both value (as string) inserting a separator inbetween.
    :param first: First value.
    :param second: Second value.
    :param separator: Optional separator.
    :return: first + separator + second.

    >>> let_user_choose("first", "second") == "first|second"
    True
    >>> let_user_choose(1,2) == "1|2"
    True
    >>> let_user_choose((1,2,3), (4,5,6)) == "(1, 2, 3)|(4, 5, 6)"
    True
    >>> let_user_choose(None, "second") == "second"
    True
    >>> let_user_choose("first", None) == "first"
    True
    >>> let_user_choose("same", "same") == "same"
    True
    """
    if first is None:
        return second
    if second is None:
        return first
    if first == second:
        return first
    return '{0!s}{1!s}{2!s}'.format(first, separator, second)


if __name__ == "__main__":
    import doctest

    logger.addHandler(logging.NullHandler())
    doctest.testmod()


def tag_to_language_script(tag, use_suppress_script=False):
    if '-' in tag:
        # replace 3 char language isocode by 2 char isocode
        # XXX Assume lang-script format
        splitted = tag.split('-', 1)
        lang = splitted[0]
        try:
            lang_lookup = languages.lookup(lang)
            lang_2 = lang_lookup.alpha_2
        except (LookupError, AttributeError):
            lang_2 = lang

        splitted[0] = lang_2
        tag = '-'.join(splitted)

    tag = tags.tag(tag)
    script = str(tag.script) if tag.script else ''
    language = tag.language
    if use_suppress_script and language and not script:
        suppress_script = language.data.get('record', {}).get('Suppress-Script')
        script = suppress_script
    language = str(tag.language) if tag.language else ''
    if language.lower() == 'und':
        language = ''

    # hard-code suppress-script for zh language
    if language == 'zh' and not script:
        script = 'Hani'
    return language, script


def is_idna_valid_cp_or_sequence(cp_or_sequence, udata, check_all=False):
    all_invalid = dict()
    for cp in cp_or_sequence:
        prop = udata.get_idna_prop(cp)
        if prop not in VALID_IDNA_PROPERTY_VALUES:
            all_invalid[cp] = prop
            if not check_all:
                return False, all_invalid
    return len(all_invalid) == 0, all_invalid
