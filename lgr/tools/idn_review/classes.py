#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
classes -
"""
import logging
from enum import auto
from typing import Dict, Set, Tuple

from lgr.classes import TAG_CLASSNAME_PREFIX
from lgr.core import LGR
from lgr.tools.idn_review.utils import AutoName
from lgr.utils import cp_to_ulabel

logger = logging.getLogger(__name__)


class ClassReportResult(AutoName):
    MATCH = auto()
    SUBSET = auto()
    MANUAL_CHECK = auto()
    REVIEW = auto()


class ClassReport:

    def __init__(self, class_name: str, idn_table_cp, ref_lgr_cp, idn_table_repertoire: Set,
                 reference_lgr_repertoire: Set):
        self.class_name = class_name
        self.idn_table_cp = idn_table_cp
        self.ref_lgr_cp = ref_lgr_cp
        self.idn_table_repertoire = idn_table_repertoire
        self.reference_lgr_repertoire = reference_lgr_repertoire

    def compute_result_and_remark(self):
        if not self.idn_table_cp ^ self.ref_lgr_cp:
            return ClassReportResult.MATCH, "Classes and their members are matched"

        extra_idn = self.idn_table_cp - self.ref_lgr_cp
        extra_ref = self.ref_lgr_cp - self.idn_table_cp

        # as we may have many cases together (e.g. extra members on each side, either in or not in LGR) we sort the
        # cases per priority, therefore, do not change this order if not intended to change the cases
        # Sorting result when possible conflicts: REVIEW > MANUAL_CHECK > SUBSET

        if not self.idn_table_cp:
            # case with not idn_table_cp and all ref_lgr_cp out of IDN repertoire not handled here and already discarded
            assert self.ref_lgr_cp & self.idn_table_repertoire
            return (ClassReportResult.MANUAL_CHECK,
                    "Mismatch class (class does not exist in IDN Table; check for different class names)")

        if not self.ref_lgr_cp:
            if self.idn_table_cp & self.reference_lgr_repertoire:
                return (ClassReportResult.MANUAL_CHECK,
                        "Mismatch class (class does not exist in ref. LGR; check for different class names)")
            if self.idn_table_cp ^ self.reference_lgr_repertoire:
                return ClassReportResult.MANUAL_CHECK, "Mismatch class with only additional code points."

        result = None
        remark = []
        if extra_idn and extra_idn & self.reference_lgr_repertoire:
            result = ClassReportResult.REVIEW
            remark.append("Mismatch class members (extra member(s) in IDN Table)")
        if extra_ref and extra_ref & self.idn_table_repertoire:
            result = ClassReportResult.REVIEW
            remark.append("Mismatch class members (missing member(s) in IDN Table)")
        if result:
            return result, '\n'.join(remark)

        if extra_idn:
            return (ClassReportResult.MANUAL_CHECK,
                    "Mismatch class members (extra member(s) in IDN Table which are not in Ref. LGR repertoire)")

        if extra_ref:
            return ClassReportResult.SUBSET, "Extra members in Ref. LGR not in IDN Table"

    def to_dict(self) -> Dict:
        if not self.idn_table_cp and not (self.ref_lgr_cp & self.idn_table_repertoire):
            # class in Ref. LGR for code points not included in IDN table
            return {}

        result, remark = self.compute_result_and_remark()
        return {
            'name': self.class_name.replace(TAG_CLASSNAME_PREFIX, ''),
            'idn_members': sorted(cp_to_ulabel(cp) for cp in self.idn_table_cp),
            'ref_members': sorted(cp_to_ulabel(cp) for cp in self.ref_lgr_cp),
            'result': result.value,
            'remark': remark
        }


# TODO factorize with django renderer api
def get_repertoire_and_class_members(lgr) -> Tuple[Dict[str, Set], Set]:
    members = {}
    repertoire = lgr.unicode_database.get_set((c.cp[0] for c in lgr.repertoire.all_repertoire(include_sequences=False)),
                                              freeze=True)
    for clz_name in sorted(lgr.classes_lookup.keys(), key=lambda x: (x.startswith(TAG_CLASSNAME_PREFIX), x)):
        clz = lgr.classes_lookup[clz_name]
        if clz.implicit:
            # Class is implicit
            continue
        try:
            clz_members = clz.get_pattern(lgr.rules_lookup, lgr.classes_lookup,
                                          lgr.unicode_database, as_set=True) & repertoire
        except RuntimeError:
            clz_members = []
        members[clz_name] = clz_members

    return members, repertoire


def generate_classes_report(idn_table: LGR, reference_lgr: LGR):
    idn_table_members, idn_table_repertoire = get_repertoire_and_class_members(idn_table)
    ref_lgr_members, ref_lgr_repertoire = get_repertoire_and_class_members(reference_lgr)

    reports = []
    for clz_name in sorted(idn_table_members.keys() | ref_lgr_members.keys(),
                           key=lambda x: (x.startswith(TAG_CLASSNAME_PREFIX), x)):
        report = ClassReport(clz_name, idn_table_members.get(clz_name, set()), ref_lgr_members.get(clz_name, set()),
                             idn_table_repertoire, ref_lgr_repertoire).to_dict()
        if report:
            reports.append(report)

    return reports
