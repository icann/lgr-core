#! /bin/env python
# -*- coding: utf-8 -*-
"""
variant_sets -
"""
import logging
from enum import Enum, auto
from typing import Dict, List, Tuple, Set

from lgr.char import Char, Variant, Repertoire
from lgr.core import LGR
from lgr.exceptions import NotInLGR, VariantAlreadyExists
from lgr.tools.idn_review.utils import IdnReviewResult
from lgr.validate import check_symmetry, check_transitivity

logger = logging.getLogger(__name__)


class VariantData:

    def __init__(self, in_lgr: bool):
        self._fwd = []
        self._rev = []
        self.in_lgr = in_lgr

    def add_variant(self, fwd: Variant, rev: List[Variant]):
        fwd_set = set(self._fwd)
        fwd_set.add(fwd)
        self._fwd = list(fwd_set)
        rev_set = set(self._rev)
        rev_set.update(rev)
        self._rev = list(rev_set)

    def has_variant(self) -> bool:
        return len(self._fwd) > 0

    def has_reverse(self) -> bool:
        return len(self._rev) > 0

    def get_var(self) -> Variant:
        return self._fwd[0] if self.has_variant() else None

    def get_rev_var(self) -> Variant:
        return self._rev[0] if self.has_reverse() else None

    def get_vars(self) -> Set[Variant]:
        return set(self._fwd)

    def get_rev_vars(self) -> Set[Variant]:
        return set(self._rev)

    def get_cp(self) -> tuple:
        return self._fwd[0].cp if self.has_variant() else ()

    def get_rev_cp(self) -> tuple:
        return self._rev[0].cp if self.has_reverse() else ()

    def in_repertoire(self, repertoire) -> bool:
        return self.has_variant() and self.get_cp() in repertoire and self.has_reverse() and self.get_rev_cp() in repertoire

    def get_types(self) -> str:
        return ' - '.join(sorted(c.type for c in self._fwd if c.type is not None))

    def get_rev_types(self) -> str:
        return ' - '.join(sorted(c.type for c in self._rev if c.type is not None))

    def get_when(self) -> str:
        for v in self.get_vars():
            if v.when:
                return v.when
        return None

    def get_not_when(self) -> str:
        for v in self.get_vars():
            if v.not_when:
                return v.not_when
        return None

    def get_rev_when(self) -> str:
        for v in self.get_rev_vars():
            if v.when:
                return v.when
        return None

    def get_rev_not_when(self) -> str:
        for v in self.get_rev_vars():
            if v.not_when:
                return v.not_when
        return None

    def get_when_type(self) -> str:
        for v in self.get_vars():
            if v.when:
                return v.type
        return ''

    def get_not_when_type(self) -> str:
        for v in self.get_vars():
            if v.not_when:
                return v.type
        return ''

    def get_rev_when_type(self) -> str:
        for v in self.get_rev_vars():
            if v.when:
                return v.type
        return ''

    def get_rev_not_when_type(self) -> str:
        for v in self.get_rev_vars():
            if v.not_when:
                return v.type
        return ''

    def get_non_conditional_type(self) -> str:
        for v in self.get_vars():
            if not v.when and not v.not_when:
                return v.type
        return ''

    def get_rev_non_conditional_type(self) -> str:
        for v in self.get_rev_vars():
            if not v.when and not v.not_when:
                return v.type
        return ''

    @classmethod
    def none(cls):
        return cls(False)


class VariantComparison:
    VARIANT_TYPES_ORDER = ['activated', 'optionally-activated', 'allocatable', 'optionally-allocatable', 'blocked']

    class Direction(Enum):
        FORWARD = auto()
        REVERSE = auto()

    class IdnRuleCheck(Enum):
        MATCH = auto()
        LESS_CONSERVATIVE = auto()
        MISSING = auto()
        DIFFERENT = auto()

    class IdnTypeCheck(Enum):
        MATCH = auto()
        LESS_CONSERVATIVE = auto()
        MORE_CONSERVATIVE = auto()
        UNKNOWN = auto()

    def __init__(self, idn_var_data: VariantData, ref_var_data: VariantData):
        self.idn_var_data = idn_var_data
        self.ref_var_data = ref_var_data

    def get_dest_char(self):
        return self.idn_var_data.get_var() or self.ref_var_data.get_var()

    def get_dest_cp(self):
        return self.idn_var_data.get_cp() or self.ref_var_data.get_cp()

    def check_symmetry(self) -> bool:
        if self.idn_var_data.has_variant() and self.ref_var_data.has_variant():
            return (self.idn_var_data.get_types() == self.idn_var_data.get_rev_types() and
                    self.ref_var_data.get_types() == self.ref_var_data.get_rev_types())
        if self.idn_var_data.has_variant():
            return self.idn_var_data.get_types() == self.idn_var_data.get_rev_types()
        if self.ref_var_data.has_variant():
            return self.ref_var_data.get_types() == self.ref_var_data.get_rev_types()

        return None  # should not happen

    def same_type(self, direction) -> bool:
        if direction == self.Direction.FORWARD:
            return self.idn_var_data.get_types() == self.ref_var_data.get_types()
        else:
            return self.idn_var_data.get_rev_types() == self.ref_var_data.get_rev_types()

    def check_rules(self, direction) -> IdnRuleCheck:
        if direction == self.Direction.FORWARD:
            idn_wle = {
                'when': self.idn_var_data.get_when(),
                'not-when': self.idn_var_data.get_not_when()
            }
            ref_wle = {
                'when': self.ref_var_data.get_when_type(),
                'not-when': self.ref_var_data.get_not_when()
            }
        else:
            idn_wle = {
                'when': self.idn_var_data.get_rev_when(),
                'not-when': self.idn_var_data.get_rev_not_when()
            }
            ref_wle = {
                'when': self.ref_var_data.get_rev_when(),
                'not-when': self.ref_var_data.get_rev_not_when()
            }

        if idn_wle == ref_wle:
            return self.IdnRuleCheck.MATCH
        # check multiple when/not-when
        if (idn_wle['when'] and idn_wle['not-when']) or (ref_wle['when'] and ref_wle['not-when']):
            return self.IdnRuleCheck.DIFFERENT
        if (idn_wle['when'] and not ref_wle['when']) or (idn_wle['not-when'] and not ref_wle['not-when']):
            return self.IdnRuleCheck.LESS_CONSERVATIVE
        if (not idn_wle['when'] and ref_wle['when']) or (not idn_wle['not-when'] and ref_wle['not-when']):
            return self.IdnRuleCheck.MISSING
        return self.IdnRuleCheck.DIFFERENT

    def check_type(self, direction) -> IdnTypeCheck:
        if direction == self.Direction.FORWARD:
            idn_type = {
                'when': self.idn_var_data.get_when_type(),
                'not-when': self.idn_var_data.get_not_when_type(),
                'none': self.idn_var_data.get_non_conditional_type()
            }
            ref_type = {
                'when': self.ref_var_data.get_when_type(),
                'not-when': self.ref_var_data.get_not_when_type(),
                'none': self.ref_var_data.get_non_conditional_type()
            }
        else:
            idn_type = {
                'when': self.idn_var_data.get_rev_when_type(),
                'not-when': self.idn_var_data.get_rev_not_when_type(),
                'none': self.idn_var_data.get_rev_non_conditional_type()
            }
            ref_type = {
                'when': self.ref_var_data.get_rev_when_type(),
                'not-when': self.ref_var_data.get_rev_not_when_type(),
                'none': self.ref_var_data.get_rev_non_conditional_type()
            }

        if idn_type == ref_type:
            return self.IdnTypeCheck.MATCH

        result = None
        for r in ['when', 'not-when', 'none']:
            if idn_type[r] == '' or ref_type[r] == '':
                # '' means not applicable, None mean no type but applicable
                continue
            try:
                if self.VARIANT_TYPES_ORDER.index(idn_type[r]) < self.VARIANT_TYPES_ORDER.index(ref_type[r]):
                    new_result = self.IdnTypeCheck.LESS_CONSERVATIVE
                else:
                    new_result = self.IdnTypeCheck.MORE_CONSERVATIVE

                if not result:
                    result = new_result
                elif result != new_result:
                    # we cannot find a consistency between variants
                    result = self.IdnTypeCheck.UNKNOWN
                    break
            except ValueError:
                result = self.IdnTypeCheck.UNKNOWN
                break

        # result may actually be None if we were not able to make a comparison because we did not have matches between
        # rules, this would lead to a rule related result
        return result


class VariantReport:

    def __init__(self, idn_table_char: Char, reference_lgr_char: Char,
                 idn_table_var_data: VariantData, reference_lgr_var_data: VariantData,
                 idn_variant_set_missing: bool, reference_lgr_variant_set_missing: bool,
                 idn_table_repertoire: Repertoire):
        self.idn_table_char = idn_table_char
        self.reference_lgr_char = reference_lgr_char
        self.idn_table_var_data = idn_table_var_data
        self.reference_lgr_var_data = reference_lgr_var_data
        self.idn_variant_set_missing = idn_variant_set_missing
        self.reference_lgr_variant_set_missing = reference_lgr_variant_set_missing
        self.idn_table_repertoire = idn_table_repertoire
        self.variant_compare = VariantComparison(idn_table_var_data, reference_lgr_var_data)

    def to_dict(self) -> Dict:
        src_char = self.idn_table_char or self.reference_lgr_char
        in_repertoire = self.reference_lgr_var_data.in_repertoire(self.idn_table_repertoire)
        result_fwd, remark_fwd = self.get_result_and_remark(VariantComparison.Direction.FORWARD, in_repertoire)
        result_rev, remark_rev = self.get_result_and_remark(VariantComparison.Direction.REVERSE, in_repertoire)
        return {
            'source_cp': src_char.cp,
            'source_glyph': str(src_char),
            'dest_cp': self.variant_compare.get_dest_cp(),
            'dest_glyph': str(self.variant_compare.get_dest_char()),
            'fwd_type_idn': self.idn_table_var_data.get_types(),
            'fwd_type_ref': self.reference_lgr_var_data.get_types(),
            'reverse': self.idn_table_var_data.has_reverse() or self.reference_lgr_var_data.has_reverse(),
            'rev_type_idn': self.idn_table_var_data.get_rev_types(),
            'rev_type_ref': self.reference_lgr_var_data.get_rev_types(),
            'dest_in_idn': self.idn_table_var_data.in_lgr,
            'dest_in_ref': self.reference_lgr_var_data.in_lgr,
            'symmetric': self.variant_compare.check_symmetry(),
            'result_fwd': result_fwd,
            'result_rev': result_rev,
            'remark_fwd': remark_fwd,
            'remark_rev': remark_rev,
        }

    def get_result_and_remark(self, direction: VariantComparison.Direction, in_idn_repertoire: bool) -> Tuple[str, str]:
        if self.idn_variant_set_missing:
            return IdnReviewResult.REVIEW.name, "Variant set exists in the reference LGR"

        if self.reference_lgr_variant_set_missing:
            return IdnReviewResult.MANUAL_CHECK.name, "Variant set only exists in the IDN Table"

        if not self.idn_table_var_data.has_variant():
            if in_idn_repertoire:
                return IdnReviewResult.REVIEW.name, "Variant member exists in the reference LGR"
            return IdnReviewResult.NOTE.name, "Not applicable"

        if not self.reference_lgr_var_data.has_variant():
            return IdnReviewResult.MANUAL_CHECK.name, "Variant member exists in IDN Table but not in the reference LGR"

        rules_check = self.variant_compare.check_rules(direction)
        type_check = self.variant_compare.check_type(direction)

        if rules_check == VariantComparison.IdnRuleCheck.LESS_CONSERVATIVE:
            result = IdnReviewResult.REVIEW.name
            remark = "IDN Table variant generation is less conservative as it only applies with some conditions"
            if type_check == VariantComparison.IdnTypeCheck.LESS_CONSERVATIVE:
                remark += "\nVariant type in the IDN Table is less conservative compared to the Ref. LGR"
            elif type_check == VariantComparison.IdnTypeCheck.UNKNOWN:
                remark += "\nUnknown variant type"
            return result, remark

        if type_check == VariantComparison.IdnTypeCheck.LESS_CONSERVATIVE:
            return (IdnReviewResult.REVIEW.name,
                    "Variant type in the IDN Table is less conservative compared to the Ref. LGR")
        if type_check == VariantComparison.IdnTypeCheck.UNKNOWN:
            return IdnReviewResult.REVIEW.name, "Unknown variant type"

        if rules_check == VariantComparison.IdnRuleCheck.MISSING:
            return (IdnReviewResult.MANUAL_CHECK.name,
                    "Variant condition rules are mismatched. The IDN Table misses the rule. "
                    "If the rule is not needed for the proper variant index calculation, then this is ok")
        if rules_check == VariantComparison.IdnRuleCheck.DIFFERENT:
            return IdnReviewResult.MANUAL_CHECK.name, "Variant contextual rules are different"

        if type_check == VariantComparison.IdnTypeCheck.MORE_CONSERVATIVE:
            return (IdnReviewResult.NOTE.name,
                    "Variant types are mismatched. IDN Table is more conservative comparing to the Reference LGR")

        assert type_check in [VariantComparison.IdnTypeCheck.MATCH, None] and rules_check == VariantComparison.IdnRuleCheck.MATCH
        return IdnReviewResult.MATCH.name, "Exact match (including type, conditional variant rule)"


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
            # XXX case not handled: missing variant sets but repertoires are not the same 10.7.10
            return None, None

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
                                  len(self.idn_table_variant_set) == 0,
                                  len(self.reference_lgr_variant_set) == 0,
                                  self.idn_repertoire).to_dict())

        return variant_reports, tuple(sorted(relevant_repertoire))

    @staticmethod
    def get_variant_data(repertoire: Repertoire, char: Char, reversed_variants: dict) -> Dict[Tuple, VariantData]:
        variants = {}
        for var in char.get_variants():
            in_lgr = True
            if var.cp in reversed_variants.get(char.cp, []):
                continue
            var_var = []
            try:
                var_var = repertoire.get_variant(var.cp, char.cp) or []
                reversed_variants.setdefault(var.cp, []).append(char.cp)
            except NotInLGR:
                in_lgr = False
            variants.setdefault(var.cp, VariantData(in_lgr)).add_variant(var, var_var)
        return variants

    def checks(self):
        symmetry_ok = None
        transitivity_ok = None
        if self.idn_table_variant_set:
            lgr = LGR()
            for cp in self.idn_table_variant_set:
                lgr.add_cp(cp)
                char: Char = self.idn_repertoire.get_char(cp)
                for var in char.get_variants():
                    try:
                        lgr.add_variant(cp, var.cp)
                    except VariantAlreadyExists:
                        # multiple contextual rules
                        continue

            symmetry_ok, _ = check_symmetry(lgr, None)
            transitivity_ok, _ = check_transitivity(lgr, None)
        return symmetry_ok, transitivity_ok

    def to_dict(self) -> Dict:
        symmetry_ok, transitivity_ok = self.checks()

        var_report, relevant_repertoire = self.generate_variant_set_report()
        if not relevant_repertoire:  # TODO remove that once case is handled
            return {}

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


def get_additional_codepoints(idn_table, idn_table_variant_sets, reference_lgr) -> List[Dict]:
    """
    Get code points from IDN table not in reference LGR that are not handled in the report (i.e. not in a variant set)
    """
    unidb = idn_table.unicode_database
    variants_flat = set(zip(*[v for v in idn_table_variant_sets.values()]))
    return [{
        'cp': char.cp,
        'glyph': str(char),
        'name': " ".join(unidb.get_char_name(cp) for cp in char.cp),
    } for char in idn_table.repertoire if
        char.cp not in variants_flat and char not in reference_lgr.repertoire]


def generate_variant_sets_report(idn_table: LGR, reference_lgr: LGR) -> Dict:
    idn_table_variant_sets = {s[0]: s for s in idn_table.repertoire.get_variant_sets()}
    reference_lgr_variant_sets = {s[0]: s for s in reference_lgr.repertoire.get_variant_sets()}

    # if some variant sets from IDN table or Ref. LGR are included respectively in Ref. LGR or IDN table but does not
    # have the same index, try to update the indexes to make them match
    only_in_idn = [k for k in idn_table_variant_sets.keys() if k not in reference_lgr_variant_sets.keys()]
    only_in_ref = [k for k in reference_lgr_variant_sets.keys() if k not in idn_table_variant_sets.keys()]
    for idn_set_id in only_in_idn:
        idn_cps = idn_table_variant_sets[idn_set_id]
        for ref_set_id in only_in_ref:
            ref_cps = reference_lgr_variant_sets[ref_set_id]
            if set(idn_cps) <= set(ref_cps) or set(idn_cps) >= set(ref_cps):
                new_set_id = min(idn_set_id, ref_set_id)
                if new_set_id not in idn_table_variant_sets:
                    idn_table_variant_sets[new_set_id] = idn_table_variant_sets.pop(idn_set_id)
                if new_set_id not in reference_lgr_variant_sets:
                    reference_lgr_variant_sets[new_set_id] = reference_lgr_variant_sets.pop(reference_lgr_variant_sets)

    reports = []
    for set_id in sorted(idn_table_variant_sets.keys() | reference_lgr_variant_sets.keys()):
        idn_table_variant_set = idn_table_variant_sets.get(set_id, ())
        reference_lgr_variant_set = reference_lgr_variant_sets.get(set_id, ())
        report = VariantSetsReport(idn_table_variant_set, reference_lgr_variant_set, idn_table.repertoire,
                                   reference_lgr.repertoire).to_dict()
        if report:
            reports.append(report)

    return {
        'reports': reports,
        'additional': get_additional_codepoints(idn_table, idn_table_variant_sets, reference_lgr)
    }
