#! /bin/env python
# -*- coding: utf-8 -*-
"""
utils - 
"""
import logging
from enum import IntEnum
from types import DynamicClassAttribute

logger = logging.getLogger(__name__)


class IdnReviewResult(IntEnum):
    MATCH = 0
    SUBSET = 1
    NOTE = 2
    MANUAL_CHECK = 3
    REVIEW = 4

    @DynamicClassAttribute
    def name(self):
        return super(IdnReviewResult, self).name.replace('_', ' ')


def cp_report(unidb, repertoire):
    return [{
        'cp': char.cp,
        'glyph': str(char),
        'name': " ".join(unidb.get_char_name(cp) for cp in char.cp),
        'idna_property': ' '.join(unidb.get_idna_prop(cp) for cp in char.cp),
        'category': ' '.join(unidb.get_prop_value(cp, 'General_Category') for cp in char.cp)
    } for char in repertoire]
