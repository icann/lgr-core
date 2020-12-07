#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
utils - 
"""
import logging
import os

from lgr.parser.xml_parser import XMLParser

logger = logging.getLogger('utils')


def load_lgr(folder, name):
    parser = XMLParser(os.path.join(os.path.dirname(__file__), '..', 'inputs', folder, name))
    return parser.parse_document()