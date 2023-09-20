#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Tuple

from lgr.char import Char
from lgr.core import LGR


def check_idna2008_compliance(idn_table: LGR):
    unidb = idn_table.unicode_database
    repertoire: Dict[Tuple, Char] = {c.cp: c for c in idn_table.repertoire.all_repertoire()}
    invalid = []
    for cp, char in repertoire.items():
        if is_out_of_repertoire(char):
            continue
        for c in cp:
            prop = unidb.get_idna_prop(c)
            if prop in ['UNASSIGNED', 'DISALLOWED']:
                invalid.append({
                    'char': char,
                    'idna_property': prop,
                })
                break

    return invalid


def is_out_of_repertoire(char):
    for v in char.get_reflexive_variants():
        if v.type and v.type.lower().startswith('out-of-repertoire'):
            return True
    return False
