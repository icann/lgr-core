#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
whole_label_evaluation_rules - 
"""
import logging
from enum import auto
from typing import Dict, Set, Tuple, List

from lgr.char import Char
from lgr.core import LGR
from lgr.rule import Rule
from lgr.tools.idn_review.utils import AutoName

logger = logging.getLogger(__name__)


class WholeLabelEvaluationRuleResult(AutoName):
    MATCH = auto()
    SUBSET = auto()
    MANUAL_CHECK = auto()


class WholeLabelEvaluationRuleReport:

    def __init__(self, idn_table: LGR, idn_table_rule: Rule, reference_lgr_rule: Rule, idn_table_context: Set,
                 reference_lgr_context: Set):
        self.idn_table = idn_table
        self.idn_table_rule = idn_table_rule
        self.reference_lgr_rule = reference_lgr_rule
        self.idn_table_context = idn_table_context
        self.reference_lgr_context = reference_lgr_context
        self.idn_table_repertoire = set(c.cp for c in self.idn_table.repertoire)

    def compare_wle(self) -> Tuple[WholeLabelEvaluationRuleResult, str]:
        # compare rule regex for rule equality
        if not self.idn_table_rule:
            if not (self.idn_table_repertoire & self.reference_lgr_context):
                return (WholeLabelEvaluationRuleResult.SUBSET,
                        "Match as a subset (for the rules missing in IDN Table, "
                        "applicable code points in Ref. LGR are not in IDN Table)")
            return WholeLabelEvaluationRuleResult.MANUAL_CHECK, "Mismatch (WLE rule only exists in Ref. LGR)"
        if not self.reference_lgr_rule:
            return WholeLabelEvaluationRuleResult.MANUAL_CHECK, "Mismatch (WLE rule only exists in IDN Table)"

        if str(self.idn_table_rule) == str(self.reference_lgr_rule):
            if not (self.idn_table_context ^ self.reference_lgr_context):
                return WholeLabelEvaluationRuleResult.MATCH, "Exact Match (matched names and content)"

        return WholeLabelEvaluationRuleResult.MANUAL_CHECK, "Mismatch class (content mismatch)"

    def to_dict(self) -> Dict:
        result, remark = self.compare_wle()
        return {
            'rule_name': self.idn_table_rule.name if self.idn_table_rule else self.reference_lgr_rule.name,
            'in_idn': self.idn_table_rule is not None,
            'in_lgr': self.reference_lgr_rule is not None,
            'result': result.value,
            'remark': remark
        }


class WholeLabelEvaluationRulesCheck:

    ASCII_RANGE_MAX = 0xFF

    def __init__(self, idn_table: LGR, reference_lgr: LGR):
        self.idn_table = idn_table
        self.reference_lgr = reference_lgr
        self.idn_table_context_rules: Dict[str, Set] = dict()
        self.idn_table_char_without_rule: Set[Char] = set()
        self.reference_lgr_context_rules: Dict[str, Set] = dict()
        self.combining_mark = None
        self.has_hyphen = 0x002D in self.idn_table.repertoire
        self.digits = set()
        self.has_multiple_digits_sets = False
        self.ascii_cp = set()
        self.get_context_rules()
        self.is_rtl()

    def is_rtl(self):
        for script in self.idn_table.metadata.get_scripts():
            if self.idn_table.unicode_database.is_script_rtl(script):
                return True
        return False

    def get_context_rules(self):
        digit_sets = set()
        for char in self.idn_table.repertoire:
            if len(char.cp) == 1:
                cp = char.cp[0]
                if cp < self.ASCII_RANGE_MAX:
                    self.ascii_cp.add(str(char))
                if self.idn_table.unicode_database.is_digit(cp):
                    script = self.idn_table.unicode_database.get_script(cp)
                    if str(cp) not in self.digits:
                        self.digits.add(str(cp))
                    digit_sets.add(script)
                if not self.combining_mark and self.idn_table.unicode_database.is_combining_mark(cp):
                    self.combining_mark = str(char)
            if char.when:
                self.idn_table_context_rules.setdefault(char.when, set()).add(char.cp)
            elif char.not_when:
                self.idn_table_context_rules.setdefault(char.not_when, set()).add(char.cp)
            else:
                self.idn_table_char_without_rule.add(char)

        self.has_multiple_digits_sets = len(digit_sets) > 1

        for char in self.reference_lgr.repertoire:
            if char.when:
                self.reference_lgr_context_rules.setdefault(char.when, set()).add(char.cp)
            if char.not_when:
                self.reference_lgr_context_rules.setdefault(char.not_when, set()).add(char.cp)

    def get_label(self, startswith=None, contains=None, pos=None, endswith=None):
        avoid_chars = set()
        label = startswith or ''
        for seq in [startswith, contains, endswith]:
            if seq:
                avoid_chars.add(c for c in seq)

        count = 0
        for char in self.idn_table.repertoire:
            if str(char) not in avoid_chars:
                label += str(char)
                count += 1
            if contains and ((pos and count == pos) or count) > 5:
                label += contains
            if count > 8:
                break
        if endswith:
            label += endswith

        return label

    def combining_mark_report(self) -> Dict:
        result = False
        if self.combining_mark is not None:
            result = self.test_label(self.get_label(startswith=self.combining_mark), "error")

        return {
            'applicable': self.combining_mark is not None,
            'exists': result
        }

    def consecutive_hyphens_report(self) -> Dict:
        result = False
        if self.has_hyphen:
            result = self.test_label(self.get_label(startswith='-'), "error")
            result &= self.test_label(self.get_label(contains='--', pos=3), "error")
            result &= self.test_label(self.get_label(endswith='-'), "error")

        return {
            'applicable': self.has_hyphen,
            'exists': result
        }

    def rtl_report(self) -> Dict:
        is_rtl = self.is_rtl()
        result = False
        if is_rtl and self.digits:
            result = self.test_label(self.get_label(startswith=self.digits[0]), "error")
        return {
            'applicable': is_rtl,
            'exists': result
        }

    def digits_set_report(self) -> Dict:
        result = False
        if self.has_multiple_digits_sets:
            result = self.test_label(self.get_label(contains=''.join(self.digits)), "error")
        return {
            'applicable': self.has_multiple_digits_sets,
            'exists': result
        }

    def ascii_cp_report(self) -> Dict:
        result = False
        if self.ascii_cp:
            result = self.test_label(''.join(list(self.ascii_cp)[:min(len(self.ascii_cp), 6)]), "error")
        return {
            'applicable': len(self.ascii_cp) > 0,
            'exists': result
        }

    def test_label(self, label, expected_error):
        label_cp = tuple([ord(c) for c in label])
        result, a, b, c, d, e = self.idn_table.test_label_eligible(label_cp)
        return result

    def additional_cp_report(self) -> List[Dict]:
        additional_cp = []
        for char in sorted(self.idn_table_char_without_rule, key=lambda x: x.cp):
            additional_cp.append({
                'cp': char.cp,
                'glyph': str(char),
                'name': " ".join(self.idn_table.unicode_database.get_char_name(cp) for cp in char.cp)
            })
        return additional_cp


def generate_whole_label_evaluation_rules_report(idn_table: LGR, reference_lgr: LGR) -> Dict:
    check = WholeLabelEvaluationRulesCheck(idn_table, reference_lgr)
    reports = []
    for rule_name in sorted(idn_table.rules_lookup.keys() | reference_lgr.rules_lookup.keys()):
        report = WholeLabelEvaluationRuleReport(idn_table, idn_table.rules_lookup.get(rule_name),
                                                reference_lgr.rules_lookup.get(rule_name),
                                                check.idn_table_context_rules.get(rule_name, set()),
                                                check.reference_lgr_context_rules.get(rule_name, set()))
        reports.append(report.to_dict())

    return {
        'comparison': reports,
        'additional_cp': check.additional_cp_report(),
        'additional_general_rules': {
            'combining_mark': check.combining_mark_report(),
            'consecutive_hyphens': check.consecutive_hyphens_report(),
            'rtl': check.rtl_report(),
            'digits_set': check.digits_set_report(),
            'ascii_cp': check.ascii_cp_report()
        }
    }
