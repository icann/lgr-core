#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
repertoire - 
"""
import logging
from enum import auto
from typing import Set, Tuple, Dict, List

from lgr.char import Char
from lgr.core import LGR
from lgr.tools.idn_review.utils import AutoName
from munidata.database import UnicodeDatabase

logger = logging.getLogger(__name__)


class RepertoireResult(AutoName):
    MATCH = auto()
    SUBSET = auto()
    NOTE = auto()
    REVIEW = auto()
    MANUAL_CHECK = auto()


class RepertoireReport:

    def __init__(self, idn_table_char: Char, reference_lgr_char: Char, reference_lgr_tags: Set[str],
                 reference_lgr_rules_names: Set[str], unidb: UnicodeDatabase):
        self.idn_table_char = idn_table_char
        self.reference_lgr_char = reference_lgr_char
        self.reference_lgr_tags = reference_lgr_tags
        self.reference_lgr_rules_names = reference_lgr_rules_names
        self.unidb = unidb

    def compare_char(self) -> Tuple[RepertoireResult, str]:
        if not self.idn_table_char:
            return RepertoireResult.SUBSET, "Match as a subset of repertoire"
        if not self.reference_lgr_char:
            return (RepertoireResult.MANUAL_CHECK,
                    "The code point only exists in the IDN Table but not in the reference LGR")

        # here we merge NOTE and REVIEW on rules and tags but REVIEW is prioritized over NOTE for result
        result = None
        remark = ''
        # check tags
        for tag in set(t for t in set(self.idn_table_char.tags) ^ set(self.reference_lgr_char.tags) if
                       not t.startswith('sc:')):
            if tag not in self.idn_table_char.tags:
                result = RepertoireResult.REVIEW
                remark = "Tags do not match"
                break
            if tag not in self.reference_lgr_char.tags:
                if tag in self.reference_lgr_tags:
                    result = RepertoireResult.REVIEW
                    remark = "Tags do not match"
                    break  # stop here as we have a REVIEW that is prioritized over NOTE
                elif not result:
                    result = RepertoireResult.NOTE
                    remark = "Tags not required in Reference LGR"
                    # continue in case we have a REVIEW later
        # check rule
        idn_rule_name = self.idn_table_char.when or self.idn_table_char.not_when
        ref_rule_name = self.reference_lgr_char.when or self.reference_lgr_char.not_when
        if idn_rule_name != ref_rule_name:
            if remark:
                remark += '\n'
            if result != RepertoireResult.REVIEW:
                if idn_rule_name and idn_rule_name not in self.reference_lgr_rules_names:
                    result = RepertoireResult.NOTE
                    remark += "Rules not required in Reference LGR"
                    return result, remark
                else:
                    # reset remarks as we will get a REVIEW result
                    remark = ''
            result = RepertoireResult.REVIEW
            remark += "Rules do not match"

        if not result:
            # tags and rules match
            return RepertoireResult.MATCH, "Matches code point (including tags, context rule)"

        return result, remark

    def to_dict(self) -> Dict:
        result, remark = self.compare_char()
        char = self.idn_table_char or self.reference_lgr_char
        return {
            'cp': char.cp,
            'glyph': str(char),
            'name': " ".join(self.unidb.get_char_name(cp) for cp in char.cp),
            'idn_table': self.idn_table_char is not None,
            'reference_lgr': self.reference_lgr_char is not None,
            'result': result.value,
            'remark': remark
        }


def generate_repertoire_report(idn_table: LGR, reference_lgr: LGR) -> List[Dict]:
    idn_table_repertoire: Dict[Tuple, Char] = {c.cp: c for c in idn_table.repertoire.all_repertoire(expand_ranges=True)}
    reference_lgr_repertoire = {c.cp: c for c in reference_lgr.repertoire.all_repertoire(expand_ranges=True)}

    reports = []
    for cp in sorted(idn_table_repertoire.keys() | reference_lgr_repertoire.keys()):
        idn_char = idn_table_repertoire.get(cp)
        ref_char = reference_lgr_repertoire.get(cp)
        unidb = idn_table.unicode_database if idn_char else reference_lgr.unicode_database
        report = RepertoireReport(idn_char, ref_char,
                                  set(t for t in reference_lgr.all_tags() if not t.startswith('sc:')),
                                  set(reference_lgr.rules_lookup.keys()), unidb)
        reports.append(report.to_dict())

    return reports
