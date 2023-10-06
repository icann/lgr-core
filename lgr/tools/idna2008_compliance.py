#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lgr.core import LGR
from lgr.tools.idn_review.utils import cp_report
from lgr.utils import is_idna_valid_cp_or_sequence


def check_idna2008_compliance(idn_table: LGR):
    unidb = idn_table.unicode_database
    report = cp_report(unidb, [char for char in idn_table.repertoire.all_repertoire() if
                               not is_out_of_repertoire(char) and not is_idna_valid_cp_or_sequence(char.cp, unidb)[0]])
    for data in report:
        data['idna2003_compliant'] = True
        for c in data['cp']:
            if unidb.is_idna2003_disallowed(c):
                data['idna2003_compliant'] = False
                break
    return report


def is_out_of_repertoire(char):
    for v in char.get_reflexive_variants():
        if v.type and v.type.lower().startswith('out-of-repertoire'):
            return True
    return False
