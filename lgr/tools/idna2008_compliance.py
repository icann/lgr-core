#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lgr.core import LGR
from lgr.tools.idn_review.utils import cp_report


def check_idna2008_compliance(idn_table: LGR):
    unidb = idn_table.unicode_database
    return cp_report(unidb, [char for char in idn_table.repertoire.all_repertoire() if
                             not is_out_of_repertoire(char) and contains_invalid_cp(char, unidb)])


def is_out_of_repertoire(char):
    for v in char.get_reflexive_variants():
        if v.type and v.type.lower().startswith('out-of-repertoire'):
            return True
    return False


def contains_invalid_cp(char, unidb):
    for c in char.cp:
        prop = unidb.get_idna_prop(c)
        if prop in ['UNASSIGNED', 'DISALLOWED']:
            return True
    return False
