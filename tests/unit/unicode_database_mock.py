#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
unicode_database_mock - 
"""
import inspect
import logging
import re
import unicodedata

import idna

from lgr.utils import cp_to_ulabel
from munidata.database import UnicodeDatabase
from picu.constants import U_LONG_PROPERTY_NAME

logger = logging.getLogger('unicode_database_mock')


class PatternMock:

    def __init__(self, pattern: re.Pattern):
        self.pattern = pattern
        for method in [member for member in [getattr(self.pattern, attr) for attr in dir(self.pattern)] if
                       inspect.ismethod(member)]:
            if method.__name__ != 'search':
                setattr(self, method.__name__, method)

    def search(self, *args, **kwargs):
        if 'index' in kwargs:
            kwargs['pos'] = kwargs.pop('index')
        return self.pattern.search(*args, **kwargs)


class UnicodeDatabaseMock(UnicodeDatabase):

    def get_unicode_version(self):
        return '10.0.0'
        # return unicodedata.unidata_version

    def get_char_name(self, cp):
        return unicodedata.name(cp_to_ulabel(cp))

    def get_char_age(self, cp):
        raise NotImplementedError

    def get_script(self, cp, alpha4=False):
        # TODO
        return 'Latn'

    def get_script_extensions(self, cp, alpha4=False):
        raise NotImplementedError

    def get_prop_value(self, cp, prop_name, prop_type=U_LONG_PROPERTY_NAME):
        raise NotImplementedError

    def is_combining_mark(self, cp):
        return unicodedata.combining(cp_to_ulabel(cp)) != 0

    def is_digit(self, cp):
        try:
            unicodedata.decimal(cp_to_ulabel(cp))
            return True
        except:
            return False

    def is_script_rtl(self, script):
        # XXX The list may not be accurate
        if script.lower() in {'arab', 'aran', 'xpeo', 'narb', 'sarb', 'thaa', 'hebr'}:
            return True
        return False

    def compile_regex(self, regex):
        c = re.compile(r'(?:\\x)?{([0-9]+)}')
        new_regex = regex
        while True:
            m = c.search(new_regex)
            if not m:
                break
            new_regex = new_regex[:m.start()] + cp_to_ulabel(int(m.group(1), 16)) + new_regex[m.end():]

        return PatternMock(re.compile(new_regex))

    def get_set(self, iterable=None, pattern=None, freeze=False):
        if pattern:
            raise NotImplementedError

        if freeze:
            set_cls = frozenset
        else:
            set_cls = set
        if not iterable:
            return set_cls()

        return set_cls(iterable)

    def idna_encode(self, input, options=None):
        return idna.encode(input)

    def idna_decode(self, input, options=None):
        return idna.decode(input)

    def idna_encode_label(self, input, options=None):
        return idna.encode(input)

    def idna_decode_label(self, input, options=None):
        return idna.decode(input)
