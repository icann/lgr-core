#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
variant_sets -
"""
import logging
from enum import auto

from lgr.char import Char, Variant, Repertoire
from lgr.core import LGR
from lgr.exceptions import NotInLGR
from lgr.tools.idn_review.utils import AutoName

logger = logging.getLogger(__name__)


class VariantSetsResult(AutoName):
    MATCH = auto()
    NOTE = auto()


class VariantReport:

    def __init__(self, idn_table_char: Char, reference_lgr_char: Char,
                 idn_table_var: Variant, reference_lgr_var: Variant,
                 idn_table_var_var: Variant, reference_lgr_var_var: Variant,
                 var_in_idn_table: bool, var_in_reference_lgr: bool):
        self.idn_table_char = idn_table_char
        self.reference_lgr_char = reference_lgr_char
        self.idn_table_var = idn_table_var
        self.reference_lgr_var = reference_lgr_var
        self.idn_table_var_var = idn_table_var_var
        self.reference_lgr_var_var = reference_lgr_var_var
        self.var_in_idn_table = var_in_idn_table
        self.var_in_reference_lgr = var_in_reference_lgr

    def to_dict(self):
        return {
            'source_cp': tuple([ord(c) for c in self.idn_table_char.cp]),
            # 'source_glyph': render_glyph(char),
            'dest_cp': tuple([ord(c) for c in self.idn_table_var.cp]),
            # 'dest_glyph': render_glyph(var),
            'fwd_type_idn': self.get_variant_type(self.idn_table_var),
            'fwd_type_ref': self.get_variant_type(self.reference_lgr_var),
            'reverse': self.idn_table_var_var is not None,
            'rev_type_idn': self.get_variant_type(self.idn_table_var_var),
            'rev_type_ref': self.get_variant_type(self.reference_lgr_var_var),
            'dest_in_idn': self.var_in_idn_table,
            'dest_in_ref': self.var_in_reference_lgr,
            'symmetric': self.idn_table_var_var and self.idn_table_var_var.type == self.idn_table_var_var.type,
            'result_fwd': self.get_result(self.idn_table_var, self.reference_lgr_var),
            'result_rev': self.get_result(self.idn_table_var_var, self.reference_lgr_var_var),
            'remark_fwd': self.get_remark(self.idn_table_var, self.reference_lgr_var),
            'remark_rev': self.get_remark(self.idn_table_var_var, self.reference_lgr_var_var)
        }

    @staticmethod
    def get_variant_type(variant: Variant):
        return variant.type or '' if variant else ''

    @staticmethod
    def get_result(idn_var, ref_var) -> VariantSetsResult:
        if idn_var == ref_var:
            return VariantSetsResult.MATCH

    @staticmethod
    def get_remark(idn_var, ref_var) -> str:
        if idn_var == ref_var:
            return "Exact match (including type, conditional variant rule)"


class VariantSetsReport:

    def __init__(self, set_nbr: int, idn_table_variant_set, reference_lgr_variant_set, idn_repertoire: Repertoire,
                 reference_lgr_repertoire: Repertoire, symmetry_ok: bool, transitivity_ok: bool):
        self.set_nbr = set_nbr
        self.idn_table_variant_set = idn_table_variant_set
        self.reference_lgr_variant_set = reference_lgr_variant_set
        self.idn_repertoire = idn_repertoire
        self.reference_lgr_repertoire = reference_lgr_repertoire
        self.symmetry_ok = symmetry_ok
        self.transitivity_ok = transitivity_ok

    def generate_variant_set_report(self):
        variant_reports = []
        members = set()
        reversed_variants = {}
        for cp in self.idn_table_variant_set | self.reference_lgr_variant_set:
            try:
                idn_table_char: Char = self.idn_repertoire.get_char(cp)
            except NotInLGR:
                idn_table_char = None
            try:
                reference_lgr_char: Char = self.reference_lgr_repertoire.get_char(cp)
            except NotInLGR:
                reference_lgr_char = None
            if idn_table_char:
                for idn_table_var in idn_table_char.get_variants():
                    in_idn_table = True
                    members.add(idn_table_var.cp)
                    if idn_table_var.cp in reversed_variants.get(idn_table_char.cp, []):
                        continue
                    try:
                        idn_table_var_var = self.idn_repertoire.get_variant(idn_table_var.cp, idn_table_char.cp)
                    except NotInLGR:
                        in_idn_table = False
                        idn_table_var_var = [None]
                    else:
                        if not idn_table_var_var:
                            idn_table_var_var = [None]
                        reversed_variants.setdefault(idn_table_var.cp, []).append(idn_table_char.cp)
                    reference_lgr_var = None
                    reference_lgr_var_var = [None]
                    in_lgr_ref = True
                    if reference_lgr_char:
                        reference_lgr_var = reference_lgr_char.get_variant(idn_table_var.cp)
                        if reference_lgr_var:
                            try:
                                reference_lgr_var_var = self.reference_lgr_repertoire.get_variant(reference_lgr_var.cp,
                                                                                                  reference_lgr_char.cp)
                            except NotInLGR:
                                in_lgr_ref = False
                                reference_lgr_var_var = [None]
                            else:
                                if not reference_lgr_var_var:
                                    reference_lgr_var_var = [None]
                    for idn_table_vv in idn_table_var_var:
                        reference_lgr_vv = self.get_reference_var(reference_lgr_var_var, idn_table_vv)
                        variant_reports.append(
                            VariantReport(idn_table_char, reference_lgr_char, idn_table_var, reference_lgr_var,
                                          idn_table_vv, reference_lgr_vv, in_idn_table, in_lgr_ref))

    @staticmethod
    def get_reference_var(reference_lgr_vars, idn_table_var):
        for var in set(reference_lgr_vars):
            if var in set(idn_table_var):
                return var
        return reference_lgr_vars[0]

    def to_dict(self):
        return {
            'set_number': self.set_nbr,
            'idn_table': self.idn_table_variant_set,
            'ref_lgr': self.reference_lgr_variant_set,
            'relevant_idn_table_repertoire': self.idn_repertoire,
            'symmetry_check': self.symmetry_ok,
            'transitivity_check': self.transitivity_ok
        }


def generate_variant_sets_report(idn_table: LGR, reference_lgr: LGR) -> dict:
    idn_table_variant_sets = idn_table.repertoire.get_variant_sets()
    reference_lgr_variant_sets = reference_lgr.repertoire.get_variant_sets()

    for set_id in idn_table_variant_sets.keys() - reference_lgr_variant_sets.keys():
        idn_table_variant_set = idn_table_variant_sets[set_id]

    for set_id in reference_lgr_variant_sets.keys() - idn_table_variant_sets.keys():
        reference_lgr_variant_set = reference_lgr_variant_sets[set_id]

    for set_id in idn_table_variant_sets.keys() & reference_lgr_variant_sets.keys():
        idn_table_variant_set = idn_table_variant_sets[set_id]
        reference_lgr_variant_set = reference_lgr_variant_sets[set_id]
        report = VariantSetsReport(set_id, idn_table_variant_set, reference_lgr_variant_set, idn_table.lgr.repertoire,
                                   reference_lgr.repertoire,
                                   TODO, TODO)
