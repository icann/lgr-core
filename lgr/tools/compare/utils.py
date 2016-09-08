# -*- coding: utf-8 -*-
"""
utils.py - Definition of utility functions.
"""
from collections import namedtuple

from lgr.utils import format_cp


VariantProperties = namedtuple('VariantProperties', ['cp', 'type',
                                                     'when', 'not_when',
                                                     'comment'])


def display_variant(variant):
    """
    Nicely display a variant.

    :param variant: The variant to display.
    """
    return "Variant {}: type={} - when={} - not-when={} - comment={}".format(
        format_cp(variant.cp), variant.type,
        variant.when, variant.not_when,
        variant.comment)


def compare_objects(first, second, cmp_fct):
    """
    Compare two objects, possibly None.

    :param first: First object.
    :param second: Second object.
    :param cmp_fct: A comparison function.
    :return: The "greatest" object according to `cmp_fct`,
             None if both values are None.

    >>> compare_objects(1, 2, max)
    2
    >>> compare_objects(1, 2, min)
    1
    >>> compare_objects(None, None, max) is None
    True
    >>> compare_objects(1, None, min)
    1
    >>> compare_objects(None, 1, min)
    1
    """
    if first is None:
        return second
    if second is None:
        return first

    return cmp_fct(first, second)
