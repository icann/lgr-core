#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
variant_sets -
"""
import logging
from typing import Dict, List, Tuple

from lgr.char import Char, Variant, Repertoire
from lgr.core import LGR
from lgr.exceptions import NotInLGR
from lgr.tools.idn_review.utils import IdnReviewResult
from lgr.validate import check_symmetry, check_transitivity

logger = logging.getLogger(__name__)


class VariantData:
    NONE = (None, None, False)

    def __init__(self, fwd: Variant, rev: List[Variant], in_lgr: bool):
        self.fwd = fwd
        self.rev = rev
        self.in_lgr = in_lgr

    @classmethod
    def none(cls):
        return cls(None, [None], False)


class VariantReport:
    VARIANT_TYPES_ORDER = ['activated', 'allocatable', 'optionally-allocatable', 'blocked']

    def __init__(self, idn_table_char: Char, reference_lgr_char: Char,
                 idn_table_var_data: VariantData, reference_lgr_var_data: VariantData,
                 idn_variant_set_missing: bool, idn_table_repertoire: Repertoire):
        self.idn_table_char = idn_table_char
        self.reference_lgr_char = reference_lgr_char
        self.idn_table_var_data = idn_table_var_data
        self.reference_lgr_var_data = reference_lgr_var_data
        self.idn_variant_set_missing = idn_variant_set_missing
        self.idn_table_repertoire = idn_table_repertoire

    def to_dict(self) -> Dict:
        # XXX: reference_lgr_char == None is not handled
        src_char = self.idn_table_char or self.reference_lgr_char
        dest_char = self.idn_table_var_data.fwd or self.reference_lgr_var_data.fwd
        in_repertoire = (self.reference_lgr_var_data.fwd and
                         self.reference_lgr_var_data.fwd.cp in self.idn_table_repertoire and
                         self.reference_lgr_var_data.rev[0] and
                         self.reference_lgr_var_data.rev[0].cp in self.idn_table_repertoire)
        result_fwd, remark_fwd = self.get_result_and_remark(self.idn_table_var_data.fwd,
                                                            self.reference_lgr_var_data.fwd,
                                                            self.idn_variant_set_missing,
                                                            in_repertoire)
        # TODO rev is a list, handle conditional variants
        result_rev, remark_rev = self.get_result_and_remark(self.idn_table_var_data.rev[0],
                                                            self.reference_lgr_var_data.rev[0],
                                                            self.idn_variant_set_missing,
                                                            in_repertoire)
        return {
            'source_cp': src_char.cp,
            'source_glyph': str(src_char),
            'dest_cp': dest_char.cp,
            'dest_glyph': str(dest_char),
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
            'symmetric': self.check_var_symmetry(),
            'result_fwd': result_fwd,
            'result_rev': result_rev,
            'remark_fwd': remark_fwd,
            'remark_rev': remark_rev,
        }

    @staticmethod
    def get_variant_type(variant: Variant):
        return variant.type or '' if variant else ''

    def check_var_symmetry(self):
        if self.idn_table_var_data.fwd and self.reference_lgr_var_data:
            return (self.idn_table_var_data.rev[0] and
                    self.idn_table_var_data.fwd.type == self.idn_table_var_data.rev[0].type and
                    self.reference_lgr_var_data.rev[0] and
                    self.reference_lgr_var_data.fwd.type == self.reference_lgr_var_data.rev[0].type)
        if self.idn_table_var_data.fwd:
            return (self.idn_table_var_data.rev[0] and
                    self.idn_table_var_data.fwd.type == self.idn_table_var_data.rev[0].type)
        if self.reference_lgr_var_data.fwd:
            return (self.reference_lgr_var_data.rev[0] and
                    self.reference_lgr_var_data.fwd.type == self.reference_lgr_var_data.rev[0].type)

        return None  # should not happen

    @classmethod
    def get_result_and_remark(cls, idn_var: Variant, ref_var: Variant,
                              idn_variant_set_missing: bool, in_idn_repertoire: bool) -> Tuple[str, str]:
        if idn_variant_set_missing:
            return IdnReviewResult.REVIEW.name, "Variant set exists in the reference LGR"

        if not idn_var:
            if in_idn_repertoire:
                return IdnReviewResult.REVIEW.name, "Variant member exists in the reference LGR"
            return IdnReviewResult.NOTE.name, "Not applicable"

        if idn_var.type == ref_var.type:
            if idn_var == ref_var:
                return IdnReviewResult.MATCH.name, "Exact match (including type, conditional variant rule)"
            if (idn_var.when and not ref_var.when) or (idn_var.not_when and not ref_var.not_when):
                return (IdnReviewResult.REVIEW.name,
                        "IDN Table variant generation is less conservative as it only applies with some conditions")
            if (not idn_var.when and ref_var.when) or (not idn_var.not_when and ref_var.not_when):
                return (IdnReviewResult.MANUAL_CHECK.name,
                        "Variant condition rules are mismatched. The IDN Table misses the rule. "
                        "If the rule is not needed for the proper variant index calculation, then this is ok")
        else:
            try:
                if cls.VARIANT_TYPES_ORDER.index(idn_var.type) < cls.VARIANT_TYPES_ORDER.index(ref_var.type):
                    return (IdnReviewResult.REVIEW.name,
                            "Variant type in the IDN Table is less conservative comparing to the Reference LGR")
                else:
                    return (IdnReviewResult.NOTE.name,
                            "Variant types are mismatched. "
                            "IDN Table is more conservative comparing to the Reference LGR")
            except ValueError:
                return IdnReviewResult.REVIEW.name, "Unknown variant type"


class VariantSetsReport:

    def __init__(self, idn_table_variant_set, reference_lgr_variant_set,
                 idn_repertoire: Repertoire, reference_lgr_repertoire: Repertoire):
        self.idn_table_variant_set = idn_table_variant_set
        self.reference_lgr_variant_set = reference_lgr_variant_set
        self.idn_repertoire = idn_repertoire
        self.reference_lgr_repertoire = reference_lgr_repertoire

    def generate_variant_set_report(self):
        variant_reports = []
        idn_reversed_variants = {}
        lgr_reversed_variants = {}
        relevant_repertoire = set()

        if not self.idn_table_variant_set and not self.same_repertoire():
            # XXX case not handled: missing variant sets but repertoires are not the same
            return

        for cp in sorted(set(self.idn_table_variant_set) | set(self.reference_lgr_variant_set)):
            idn_table_vars = {}
            reference_lgr_vars = {}
            try:
                idn_table_char: Char = self.idn_repertoire.get_char(cp)
                relevant_repertoire.add(cp)
            except NotInLGR:
                idn_table_char = None
            try:
                reference_lgr_char: Char = self.reference_lgr_repertoire.get_char(cp)
            except NotInLGR:
                reference_lgr_char = None
            if idn_table_char:
                idn_table_vars = self.get_variant_data(self.idn_repertoire, idn_table_char, idn_reversed_variants)
            if reference_lgr_char:
                reference_lgr_vars = self.get_variant_data(self.reference_lgr_repertoire, reference_lgr_char,
                                                           lgr_reversed_variants)

            for var_cp in idn_table_vars.keys() | reference_lgr_vars.keys():
                variant_reports.append(
                    VariantReport(idn_table_char, reference_lgr_char,
                                  idn_table_vars.get(var_cp, VariantData.none()),
                                  reference_lgr_vars.get(var_cp, VariantData.none()),
                                  len(self.idn_table_variant_set) == 0, self.idn_repertoire).to_dict())

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
            'idn_table': self.idn_table_variant_set,
            'ref_lgr': self.reference_lgr_variant_set,
            'relevant_idn_table_repertoire': relevant_repertoire,
            'symmetry_check': symmetry_ok,
            'transitivity_check': transitivity_ok,
            'report': sorted(var_report or [], key=lambda x: x['dest_cp'])
        }

    def same_repertoire(self):
        """
        Check if all code points from the reference LGR variant sets are in IDN table repertoire
        """
        for cp in self.reference_lgr_variant_set:
            if cp not in self.idn_repertoire:
                return False
        return True


def generate_variant_sets_report(idn_table: LGR, reference_lgr: LGR) -> List[Dict]:
    idn_table_variant_sets = {s[0]: s for s in idn_table.repertoire.get_variant_sets()}
    reference_lgr_variant_sets = {s[0]: s for s in reference_lgr.repertoire.get_variant_sets()}

    reports = []
    for set_id in idn_table_variant_sets.keys() | reference_lgr_variant_sets.keys():
        idn_table_variant_set = idn_table_variant_sets.get(set_id, ())
        reference_lgr_variant_set = reference_lgr_variant_sets.get(set_id, ())
        report = VariantSetsReport(idn_table_variant_set, reference_lgr_variant_set, idn_table.repertoire,
                                   reference_lgr.repertoire).to_dict()
        if report:
            reports.append(report)

    return reports
