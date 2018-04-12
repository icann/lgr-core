# -*- coding: utf-8 -*-
"""
lgr_stats.py - Compute some stats for an LGR.
"""
from __future__ import unicode_literals

import logging

from lgr.char import Char, CharSequence, RangeChar
from lgr.utils import format_cp


logger = logging.getLogger(__name__)


def generate_stats(lgr):
    """
    Given an LGR, generate the stats.

    :param lgr: The LGR to use.
    :return: Dictionary containing various stats.
    """
    stats = {
        'codepoint_number': 0,

        'range_number': 0,
        'largest_range': None,
        'largest_range_len': 0,

        'sequence_number': 0,
        'largest_sequence': None,
        'largest_sequence_len': 0,

        'codepoints_with_variants': 0,
        'variant_number': 0,
        'variants_by_type': {},
        'largest_variant_set': 0,

        'average_variants': 0,

        'codepoints_by_tag': {},

        'rule_number': len(lgr.rules),
    }

    for char in lgr.repertoire:

        # Range len set to 1 by default (for single code point and sequences)
        range_len = 1
        if isinstance(char, RangeChar):
            range_len = char.last_cp - char.first_cp + 1
            stats['codepoint_number'] += range_len
            stats['range_number'] += 1
            if range_len > stats['largest_range_len']:
                stats['largest_range_len'] = range_len
                stats['largest_range'] = char
        elif isinstance(char, CharSequence):
            stats['codepoint_number'] += 1
            stats['sequence_number'] += 1
            sequence_len = len(char.cp)
            if sequence_len > stats['largest_sequence_len']:
                stats['largest_sequence_len'] = sequence_len
                stats['largest_sequence'] = char
        elif isinstance(char, Char):
            stats['codepoint_number'] += 1

        for t in char.tags:
            if t in stats['codepoints_by_tag']:
                stats['codepoints_by_tag'][t] += range_len
            else:
                stats['codepoints_by_tag'][t] = range_len

        variants = list(char.get_variants())
        # Original char might not be in the variants (no identity mapping)
        variants_len = len(frozenset(v.cp for v in variants + ([char] if len(variants) > 0 else [])))
        stats['variant_number'] += variants_len
        stats['largest_variant_set'] = max(stats['largest_variant_set'], variants_len)
        if variants_len > 0:
            stats['codepoints_with_variants'] += 1

        for var in variants:
            if var.type in stats['variants_by_type']:
                stats['variants_by_type'][var.type] += 1
            else:
                stats['variants_by_type'][var.type] = 1

    if stats['codepoints_with_variants'] != 0:
        stats['average_variants'] = round(stats['variant_number'] / stats['codepoints_with_variants'], 1)

    return stats


def compute_stats(lgr, options):
    """
    Compute statistics for an LGR.

    :param lgr: The LGR to use.
    :param options: Not used.
    """
    stats = generate_stats(lgr)
    result = {
        'description': 'Generate stats',
        'stats': stats
    }

    if logger.isEnabledFor(logging.DEBUG):
        # General summary
        output = """
General summary:
\tNumber of code points: {codepoint_number}.

\tNumber of ranges: {range_number}.
\tLargest range: {largest_range} (length: {largest_range_len}).

\tNumber of sequences: {sequence_number}.
\tLargest sequence: {largest_sequence} (length: {largest_sequence_len}).
""".format(**stats)

        # Variants
        output += """
Variants:
\tTotal number of variants: {variant_number}.
\tAverage number of variants per code point: {average_variants}.
\tLargest variant set: {largest_variant_set}.

""".format(**stats)

        for (variant_type, number) in stats['variants_by_type'].items():
            output += "\tNumber of variants for type '{0}': {1}.\n"\
                    .format(variant_type, number)

        # Tags
        output += """
Tags:
"""
        for (tag_name, number) in stats['codepoints_by_tag'].items():
            output += "\tNumber of code points for tag '{0}': {1}.\n"\
                    .format(tag_name, number)

        # Rules summary
        output += "\nRules:\n"
        output += "\tNumber of rules defined: {0}.\n".format(stats['rule_number'])

        logger.debug(output)

    return True, result
