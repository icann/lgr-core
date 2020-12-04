#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
utils - 
"""
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.replace('_', ' ')
