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
