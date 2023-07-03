#! /bin/env python
# -*- coding: utf-8 -*-
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

    def __init__(self, pattern):
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
        from tests.unit.unidb_get_script_mock import script
        return script(cp)

    def get_script_extensions(self, cp, alpha4=False):
        raise NotImplementedError

    def get_prop_value(self, cp, prop_name, prop_type=U_LONG_PROPERTY_NAME):
        if prop_name == 'General_Category':
            return unicodedata.category(cp_to_ulabel(cp))
        raise NotImplementedError

    def is_combining_mark(self, cp):
        return unicodedata.category(cp_to_ulabel(cp)) in ['Mn', 'Mc']

    def is_digit(self, cp):
        try:
            unicodedata.decimal(cp_to_ulabel(cp))
            return True
        except:
            return False

    def is_rtl(self, cp):
        script = self.get_script(cp)
        return self.is_script_rtl(script)

    def is_script_rtl(self, script):
        # XXX The list may not be accurate
        if script.lower() in {'arab', 'aran', 'xpeo', 'narb', 'sarb', 'thaa', 'hebr', 'hebrew'}:
            return True
        return False

    def compile_regex(self, regex):
        # single hex code points
        c = re.compile(r'(?:\\x){([0-9A-F]+)}')
        new_regex = regex
        while True:
            m = c.search(new_regex)
            if not m:
                break
            new_regex = new_regex[:m.start()] + cp_to_ulabel(int(m.group(1), 16)) + new_regex[m.end():]

        # single code points
        c = re.compile(r'{([0-9]+)}')
        while True:
            m = c.search(new_regex)
            if not m:
                break
            new_regex = new_regex[:m.start()] + cp_to_ulabel(int(m.group(1))) + new_regex[m.end():]

        # list of code points {97, 99} -> [ac]
        c = re.compile(r'{([0-9]+, ?)+[0-9]+}')
        while True:
            m = c.search(new_regex)
            if not m:
                break
            new_regex = f"{new_regex[:m.start()]}[" \
                        f"{''.join([cp_to_ulabel(int(i.strip())) for i in new_regex[m.start() + 1:m.end() - 1].split(',')])}" \
                        f"]{new_regex[m.end():]}"

        return PatternMock(re.compile(new_regex))

    def _get_cp_in_category(self, category):
        cps = set()
        for cp in range(110000):
            if unicodedata.category(cp_to_ulabel(cp)) == category:
                cps.add(cp)
        return cps

    def get_set(self, iterable=None, pattern=None, freeze=False):
        if freeze:
            set_cls = frozenset
        else:
            set_cls = set

        if pattern:
            if pattern.startswith('\p{gc='):
                return set_cls(self._get_cp_in_category(pattern[6:8]))
            else:
                raise NotImplementedError

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
