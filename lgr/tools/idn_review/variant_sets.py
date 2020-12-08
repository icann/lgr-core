#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
variant_sets -
"""
import logging
from enum import auto
from typing import Dict, List

from lgr.char import Char, Variant, Repertoire
from lgr.core import LGR
from lgr.exceptions import NotInLGR
from lgr.tools.idn_review.utils import AutoName
from lgr.validate import check_symmetry, check_transitivity

logger = logging.getLogger(__name__)


class VariantSetsResult(AutoName):
    MATCH = auto()
    NOTE = auto()


class VariantData:

    def __init__(self, fwd: Variant, rev: Variant, in_lgr: bool):
        self.fwd = fwd
        self.rev = rev
        self.in_lgr = in_lgr


class VariantReport:

    def __init__(self, idn_table_char: Char, reference_lgr_char: Char,
                 idn_table_var_data: VariantData, reference_lgr_var_data: VariantData):
        self.idn_table_char = idn_table_char
        self.reference_lgr_char = reference_lgr_char
        self.idn_table_var_data = idn_table_var_data
        self.reference_lgr_var_data = reference_lgr_var_data

    def to_dict(self) -> Dict:
        return {
            'source_cp': " ".join("U+%04X" % c for c in self.idn_table_char.cp),
            'source_glyph': str(self.idn_table_char),
            'dest_cp': " ".join("U+%04X" % c for c in self.idn_table_var_data.fwd.cp),
            'dest_glyph': str(self.idn_table_var_data.fwd),
            'fwd_type_idn': self.get_variant_type(self.idn_table_var_data.fwd),
            'fwd_type_ref': self.get_variant_type(self.reference_lgr_var_data.fwd),
            'reverse': self.idn_table_var_data.rev is not None,
            # TODO rev is a list, handle conditional variants
            'rev_type_idn': self.get_variant_type(self.idn_table_var_data.rev[0]),
            # TODO rev is a list, handle conditional variants
            'rev_type_ref': self.get_variant_type(self.reference_lgr_var_data.rev[0]),
            'dest_in_idn': self.idn_table_var_data.in_lgr,
            'dest_in_ref': self.reference_lgr_var_data.in_lgr,
            # TODO rev is a list, handle conditional variants
            'symmetric': self.idn_table_var_data.rev and self.idn_table_var_data.fwd.type == self.idn_table_var_data.rev[0].type,
            'result_fwd': self.get_result(self.idn_table_var_data.fwd, self.reference_lgr_var_data.fwd),
            'result_rev': self.get_result(self.idn_table_var_data.rev, self.reference_lgr_var_data.rev),
            'remark_fwd': self.get_remark(self.idn_table_var_data.fwd, self.reference_lgr_var_data.fwd),
            'remark_rev': self.get_remark(self.idn_table_var_data.rev, self.reference_lgr_var_data.rev)
        }

    @staticmethod
    def get_variant_type(variant: Variant):
        return variant.type or '' if variant else ''

    @staticmethod
    def get_result(idn_var, ref_var) -> str:
        if idn_var == ref_var:
            return VariantSetsResult.MATCH.name

    @staticmethod
    def get_remark(idn_var, ref_var) -> str:
        if idn_var == ref_var:
            return "Exact match (including type, conditional variant rule)"


class VariantSetsReport:

    def __init__(self, set_nbr: int, idn_table_variant_set, reference_lgr_variant_set,
                 idn_repertoire: Repertoire, reference_lgr_repertoire: Repertoire):
        self.set_nbr = set_nbr
        self.idn_table_variant_set = idn_table_variant_set
        self.reference_lgr_variant_set = reference_lgr_variant_set
        self.idn_repertoire = idn_repertoire
        self.reference_lgr_repertoire = reference_lgr_repertoire

    def generate_variant_set_report(self):
        variant_reports = []
        idn_reversed_variants = {}
        lgr_reversed_variants = {}
        relevant_repertoire = set()
        for cp in set(self.idn_table_variant_set) | set(self.reference_lgr_variant_set):
            idn_table_vars = {}
            reference_lgr_vars = {}
            try:
                idn_table_char: Char = self.idn_repertoire.get_char(cp)
            except NotInLGR:
                idn_table_char = None
            try:
                reference_lgr_char: Char = self.reference_lgr_repertoire.get_char(cp)
                relevant_repertoire.add(cp)
            except NotInLGR:
                reference_lgr_char = None
            if idn_table_char:
                idn_table_vars = self.get_variant_data(self.idn_repertoire, idn_table_char, idn_reversed_variants)
            if reference_lgr_char:
                reference_lgr_vars = self.get_variant_data(self.reference_lgr_repertoire, reference_lgr_char,
                                                           lgr_reversed_variants)

            for var_cp in idn_table_vars.keys() - reference_lgr_vars.keys():
                variant_reports.append(
                    VariantReport(idn_table_char, reference_lgr_char, idn_table_vars[var_cp], None).to_dict())

            for var_cp in reference_lgr_vars.keys() - idn_table_vars.keys():
                variant_reports.append(
                    VariantReport(idn_table_char, reference_lgr_char, None, reference_lgr_vars[var_cp]).to_dict())

            for var_cp in idn_table_vars.keys() & reference_lgr_vars.keys():
                variant_reports.append(
                    VariantReport(idn_table_char, reference_lgr_char,
                                  idn_table_vars[var_cp], reference_lgr_vars[var_cp]).to_dict())

        return variant_reports, tuple(sorted(relevant_repertoire))

    @staticmethod
    def get_variant_data(repertoire: Repertoire, char: Char, reversed_variants: dict) -> dict:
        variants = {}
        for var in char.get_variants():
            in_lgr = True
            if var.cp in reversed_variants.get(char.cp, []):
                continue
            try:
                var_var = repertoire.get_variant(var.cp, char.cp)
            except NotInLGR:
                in_lgr = False
                var_var = [None]
            else:
                if not var_var:
                    var_var = [None]
                reversed_variants.setdefault(var.cp, []).append(char.cp)
            # TODO need to handle if 2 conditional variants with same cp
            variants[var.cp] = VariantData(var, var_var, in_lgr)
        return variants

    def to_dict(self) -> Dict:
        lgr = LGR()
        for cp in self.idn_table_variant_set:
            lgr.add_cp(cp)
            char: Char = self.idn_repertoire.get_char(cp)
            for var in char.get_variants():
                lgr.add_variant(cp, var.cp)

        symmetry_ok, _ = check_symmetry(lgr, None)
        transitivity_ok, _ = check_transitivity(lgr, None)

        var_report, relevant_repertoire = self.generate_variant_set_report()
        return {
            'set_number': self.set_nbr,
            'idn_table': self.idn_table_variant_set,
            'ref_lgr': self.reference_lgr_variant_set,
            'relevant_idn_table_repertoire': relevant_repertoire,
            'symmetry_check': symmetry_ok,
            'transitivity_check': transitivity_ok,
            'report': var_report
        }


def generate_variant_sets_report(idn_table: LGR, reference_lgr: LGR) -> List[Dict]:
    idn_table_variant_sets = {s[0]: s for s in idn_table.repertoire.get_variant_sets()}
    reference_lgr_variant_sets = {s[0]: s for s in reference_lgr.repertoire.get_variant_sets()}

    reports = []
    for set_id in idn_table_variant_sets.keys() - reference_lgr_variant_sets.keys():
        idn_table_variant_set = idn_table_variant_sets[set_id]

    for set_id in reference_lgr_variant_sets.keys() - idn_table_variant_sets.keys():
        reference_lgr_variant_set = reference_lgr_variant_sets[set_id]

    for set_id in idn_table_variant_sets.keys() & reference_lgr_variant_sets.keys():
        idn_table_variant_set = idn_table_variant_sets[set_id]
        reference_lgr_variant_set = reference_lgr_variant_sets[set_id]
        report = VariantSetsReport(set_id, idn_table_variant_set, reference_lgr_variant_set, idn_table.repertoire,
                                   reference_lgr.repertoire).to_dict()
        reports.append(report)

    return reports
