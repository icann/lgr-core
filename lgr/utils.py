# -*- coding: utf-8 -*-
"""
utils.py - Set of utility functions to be used in module.
"""
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


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

    >>> format_cp(1)
    u'U+0001'
    >>> format_cp([1])
    u'U+0001'
    >>> format_cp([1,2,3])
    u'U+0001 U+0002 U+0003'
    >>> format_cp(None)
    u'None'
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

    >>> format_cp_collapsed(1)
    u'U+0001'
    >>> format_cp_collapsed([1])
    u'U+0001'
    >>> format_cp_collapsed([1,3])
    u'U+0001 U+0003'
    >>> format_cp_collapsed([1,2,3])
    u'U+0001-U+0003'
    >>> format_cp(None)
    u'None'
    >>> format_cp_collapsed([1,2,3,5,6,10,12,13,14,15])
    u'U+0001-U+0003 U+0005 U+0006 U+000A U+000C-U+000F'
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
