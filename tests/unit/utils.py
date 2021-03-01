#! /bin/env python
# -*- coding: utf-8 -*-
"""
utils - 
"""
import logging
import os

from lgr.parser.xml_parser import XMLParser

logger = logging.getLogger('utils')


def load_lgr(folder, name, unidb=None):
    parser = XMLParser(os.path.join(os.path.dirname(__file__), '..', 'inputs', folder, name))
    if unidb:
        parser.unicode_database = unidb
    return parser.parse_document()
