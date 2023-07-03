#! /bin/env python
# -*- coding: utf-8 -*-
"""
whole_label_evaluation_rules - 
"""
import logging
from typing import Dict, Set, Tuple, List

from language_tags import tags

from lgr.char import Char, CharSequence
from lgr.core import LGR
from lgr.exceptions import NotInLGR
from lgr.rule import Rule
from lgr.tools.idn_review.utils import IdnReviewResult, cp_report

logger = logging.getLogger(__name__)

SAME_SCRIPTS = {
    'Aran': 'Arab',
    'Cyrs': 'Cyrl',
    'ace': 'zh',
    'yue': 'zh',
    'wuu': 'zh',
    'gan': 'zh',
    'och': 'zh',
    'cjy': 'zh',
    'hak': 'zh',
    'hsn': 'zh',
    'cpx': 'zh',
    'czh': 'zh',
    'mnp': 'zh',
    'nan': 'zh',
    'cdo': 'zh',
    'cmn': 'zh',
    'lzh': 'zh',
    'zhx': 'zh',
    'czo': 'zh',
    'ltc': 'zh',
    'csl': 'zh',
    'cpi': 'zh',
    'kvk': 'ko',
    'oko': 'ko',
    'okm': 'ko',
    'ka': 'Knda',
    'kan': 'Knda',
    'he': 'Hebr',
    'iw': 'Hebr',
    'hbo': 'Hebr',
    'ojp': 'ja',
    'jpx': 'ja',
    'jsl': 'ja',
    'Jpan': 'ja',
    'Kana': 'ja',
    'Hira': 'ja',
    'Latg': 'Latn',
    'Latf': 'Latn'
}

COMBINING_MARK_LABELS = {
    'Arab': [],  # Arabic script
    'Armn': [],  # Armenian script
    'Beng': [[0x09C1, 0x09AE, 0x09AE]],  # Bengali script
    'Cyrl': [],  # Cyrillic script
    'Deva': [[0x0948, 0x092C, 0x092C]],  # Devanagari script
    'Ethi': [],  # Ethiopic script
    'Geor': [],  # Georgian script
    'Grek': [],  # Greek script
    'Gujr': [[0x0ABC, 0x0AAC]],  # Gujarati script
    'Guru': [[0x0A02, 0x0A20]],  # Gurmukhi script
    'zh': [],  # Chinese language
    'Knda': [[0x0C83, 0x0C96]],  # kannada
    'ko': [],  # Korean language
    'Hebr': [],  # Hebrew
    'ja': [],  # Japanese language
    'Khmr': [[0x17B7, 0x178A]],  # Khmer script
    'Laoo': [[0x0EB4, 0x0E9D, 0x0E9D]],  # Lao script
    'Latn': [],  # Latin script
    'Mlym': [[0x0D02, 0x0D1C]],  # Malayalam script
    'Mymr': [[0x1032, 0x1005]],  # Myanmar script
    'Orya': [[0x0B03, 0x0B15]],  # Oriya script
    'Sinh': [[0x0D82, 0x0DA8]],  # Sinala script
    'Taml': [[0x0BBE, 0x0B9A]],  # Tamil script
    'Telu': [[0x0C03, 0x0C16]],  # Telugu script
    'Thaa': [[0x07A6, 0x0786]],  # Thaana script
    'Thai': [[0x0E37, 0x0E01]],  # Thai script
    'Tibt': [[0x0F80, 0x0F40]],  # Tibetan script
}

CONSECUTIVE_HYPHEN_LABELS = {
    'Arab': [[0x002D, 0x062A, 0x062A], [0x062A, 0x062A, 0x002D],
             [0x062A, 0x062A, 0x002D, 0x002D, 0x062A, 0x062A]],  # Arabic script
    'Armn': [[0x002D, 0x0561, 0x0561], [0x0561, 0x0561, 0x002D],
             [0x0561, 0x0561, 0x002D, 0x002D, 0x0561, 0x0561]],  # Armenian script
    'Beng': [[0x002D, 0x09AE, 0x09AE], [0x09AE, 0x09AE, 0x002D],
             [0x09AE, 0x09AE, 0x002D, 0x002D, 0x09AE, 0x09AE]],  # Bengali script
    'Cyrl': [[0x002D, 0x0434, 0x0434], [0x0434, 0x0434, 0x002D],
             [0x0434, 0x0434, 0x002D, 0x002D, 0x0434, 0x0434]],  # Cyrillic script
    'Deva': [[0x002D, 0x092C, 0x092C], [0x092C, 0x092C, 0x002D],
             [0x092C, 0x092C, 0x002D, 0x002D, 0x092C, 0x092C]],  # Devanagari script
    'Ethi': [[0x002D, 0x1228, 0x1228], [0x1228, 0x1228, 0x002D],
             [0x1228, 0x1228, 0x002D, 0x002D, 0x1228, 0x1228]],  # Ethiopic script
    'Geor': [[0x002D, 0x10D1, 0x10D1], [0x10D1, 0x10D1, 0x002D],
             [0x10D1, 0x10D1, 0x002D, 0x002D, 0x10D1, 0x10D1]],  # Georgian script
    'Grek': [[0x002D, 0x03C0, 0x03C0], [0x03C0, 0x03C0, 0x002D],
             [0x03C0, 0x03C0, 0x002D, 0x002D, 0x03C0, 0x03C0]],  # Greek script
    'Gujr': [[0x002D, 0x0AAC, 0x0AAC], [0x0AAC, 0x0AAC, 0x002D],
             [0x0AAC, 0x0AAC, 0x002D, 0x002D, 0x0AAC, 0x0AAC]],  # Gujarati script
    'Guru': [[0x002D, 0x0A20, 0x0A20], [0x0A20, 0x0A20, 0x002D],
             [0x0A20, 0x0A20, 0x002D, 0x002D, 0x0A20, 0x0A20]],  # Gurmukhi script
    'zh': [[0x002D, 0x4E24, 0x4E24], [0x4E24, 0x4E24, 0x002D],
           [0x4E24, 0x4E24, 0x002D, 0x002D, 0x4E24, 0x4E24]],  # Chinese language
    'Knda': [[0x002D, 0x0C95, 0x0C95], [0x0C95, 0x0C95, 0x002D],  # kannada
             [0x0C95, 0x0C95, 0x002D, 0x002D, 0x0C95, 0x0C95]],
    'ko': [[0x002D, 0xAC00, 0xAC00], [0xAC00, 0xAC00, 0x002D],
           [0xAC00, 0xAC00, 0x002D, 0x002D, 0xAC00, 0xAC00]],  # Korean language
    'Hebr': [[0x002D, 0x05D1, 0x05D1], [0x05D1, 0x05D1, 0x002D],
             [0x05D1, 0x05D1, 0x002D, 0x002D, 0x05D1, 0x05D1]],  # Hebrew
    'ja': [[0x002D, 0x3064, 0x3064], [0x3064, 0x3064, 0x002D],
           [0x3064, 0x3064, 0x002D, 0x002D, 0x3064, 0x3064]],  # Japanese language
    'Khmr': [[0x002D, 0x178A, 0x178A], [0x178A, 0x178A, 0x002D],
             [0x178A, 0x178A, 0x002D, 0x002D, 0x178A, 0x178A]],  # Khmer script
    'Laoo': [[0x002D, 0x0E9D, 0x0E9D], [0x0E9D, 0x0E9D, 0x002D],
             [0x0E9D, 0x0E9D, 0x002D, 0x002D, 0x0E9D]],  # Lao script
    'Latn': [[0x002D, 0x006D, 0x006D], [0x006D, 0x006D, 0x002D],
             [0x006D, 0x006D, 0x002D, 0x002D, 0x006D, 0x006D]],  # Latin script
    'Mlym': [[0x002D, 0x0D1C, 0x0D1C], [0x0D1C, 0x0D1C, 0x002D],
             [0x0D1C, 0x0D1C, 0x002D, 0x002D, 0x0D1C, 0x0D1C]],  # Malayalam script
    'Mymr': [[0x002D, 0x1005, 0x1005], [0x1005, 0x1005, 0x002D],
             [0x1005, 0x1005, 0x002D, 0x002D, 0x1005, 0x1005]],  # Myanmar script
    'Orya': [[0x002D, 0x0B15, 0x0B15], [0x0B15, 0x0B15, 0x002D],
             [0x0B15, 0x0B15, 0x002D, 0x002D, 0x0B15, 0x0B15]],  # Oriya script
    'Sinh': [[0x002D, 0x0DA8, 0x0DA8], [0x0DA8, 0x0DA8, 0x002D],
             [0x0DA8, 0x0DA8, 0x002D, 0x002D, 0x0DA8, 0x0DA8]],  # Sinala script
    'Taml': [[0x002D, 0x0B9A, 0x0B9A], [0x0B9A, 0x0B9A, 0x002D],
             [0x0B9A, 0x0B9A, 0x002D, 0x002D, 0x0B9A, 0x0B9A]],  # Tamil script
    'Telu': [[0x002D, 0x0C16, 0x0C16], [0x0C16, 0x0C16, 0x002D],
             [0x0C16, 0x0C16, 0x002D, 0x002D, 0x0C16, 0x0C16]],  # Telugu script
    'Thaa': [[0x002D, 0x0786, 0x0786], [0x0786, 0x0786, 0x002D],
             [0x0786, 0x0786, 0x002D, 0x002D, 0x0786, 0x0786]],  # Thaana script
    'Thai': [[0x002D, 0x0E01, 0x0E01], [0x0E01, 0x0E01, 0x002D],
             [0x0E01, 0x0E01, 0x002D, 0x002D, 0x0E01, 0x0E01]],  # Thai script
    'Tibt': [[0x002D, 0x0F40, 0x0F40], [0x0F40, 0x0F40, 0x002D],
             [0x0F40, 0x0F40, 0x002D, 0x002D, 0x0F40, 0x0F40]],  # Tibetan script
}

BEGIN_DIGIT_LABELS = {
    'Arab': [[0x0032, 0x062A, 0x062A], [0x0660, 0x062A, 0x062A], [0x06F5, 0x062A, 0x062A]],  # Arabic script
    'Armn': [],  # Armenian script
    'Beng': [],  # Bengali script
    'Cyrl': [],  # Cyrillic script
    'Deva': [],  # Devanagari script
    'Ethi': [],  # Ethiopic script
    'Geor': [],  # Georgian script
    'Grek': [],  # Greek script
    'Gujr': [],  # Gujarati script
    'Guru': [],  # Gurmukhi script
    'zh': [],  # Chinese language
    'ko': [],  # Korean language
    'Knda': [],  # kannada
    'Hebr': [[0x0033, 0x05D1, 0x05D1]],  # Hebrew
    'ja': [],  # Japanese language
    'Khmr': [],  # Khmer script
    'Laoo': [],  # Lao script
    'Latn': [],  # Latin script
    'Mlym': [],  # Malayalam script
    'Mymr': [],  # Myanmar script
    'Orya': [],  # Oriya script
    # '': [],  # Sinala script
    'Taml': [],  # Tamil script
    'Telu': [],  # Telugu script
    'Thaa': [[0x0034, 0x0786]],  # Thaana script
    'Thai': [],  # Thai script
    'Tibt': [],  # Tibetan script
}

MULTIPLE_DIGIT_SETS_LABELS = {
    'Arab': [[0x062A, 0x062A, 0x0032, 0x0662], [0x062A, 0x062A, 0x0032, 0x06F5],
             [0x062A, 0x062A, 0x0662, 0x06F5]],  # Arabic script
    'Armn': [],  # Armenian script
    'Beng': [[0x09AE, 0x09AE, 0x0032, 0x09E9]],  # Bengali script
    'Cyrl': [],  # Cyrillic script
    'Deva': [[0x092D, 0x0032, 0x0966]],  # Devanagari script
    'Ethi': [],  # Ethiopic script
    'Geor': [],  # Georgian script
    'Grek': [],  # Greek script
    'Gujr': [[0x0AAC, 0x0032, 0x0AEE]],  # Gujarati script
    'Guru': [],  # Gurmukhi script
    'zh': [],  # Chinese language
    'ko': [],  # Korean language
    'Knda': [[0x0C85, 0x0CE7, 0x0031]],  # kannada
    'Hebr': [],  # Hebrew
    'ja': [],  # Japanese language
    'Khmr': [[0x178A, 0x0032, 0x17E5]],  # Khmer script
    'Laoo': [[0x0E9D, 0x0ED9, 0x0033]],  # Lao script
    'Latn': [],  # Latin script
    'Mlym': [],  # Malayalam script
    'Mymr': [[0x1005, 0x1042, 0x0035], [0x1005, 0x0035, 0x1095], [0x1005, 0x1042, 0x1095]],  # Myanmar script
    'Orya': [],  # Oriya script
    'Sinh': [],  # Sinala script
    'Taml': [],  # Tamil script
    'Telu': [],  # Telugu script
    'Thaa': [],  # Thaana script
    'Thai': [[0x0E01, 0x0E53, 0x0033]],  # Thai script
    'Tibt': [[0x0F40, 0x0033, 0x0F27]],  # Tibetan script
}

JAPANESE_CONTEXTJ_LABELS = {
    'Arab': [],  # Arabic script
    'Armn': [],  # Armenian script
    'Beng': [],  # Bengali script
    'Cyrl': [],  # Cyrillic script
    'Deva': [],  # Devanagari script
    'Ethi': [],  # Ethiopic script
    'Geor': [],  # Georgian script
    'Grek': [],  # Greek script
    'Gujr': [],  # Gujarati script
    'Guru': [],  # Gurmukhi script
    'zh': [],  # Chinese language
    'ko': [],  # Korean language
    'Knda': [],  # kannada
    'Hebr': [],  # Hebrew
    'ja': [[0x0062, 0x30FB, 0x0061]],  # Japanese language
    'Khmr': [],  # Khmer script
    'Laoo': [],  # Lao script
    'Latn': [],  # Latin script
    'Mlym': [],  # Malayalam script
    'Mymr': [],  # Myanmar script
    'Orya': [],  # Oriya script
    'Sinh': [],  # Sinala script
    'Taml': [],  # Tamil script
    'Telu': [],  # Telugu script
    'Thaa': [],  # Thaana script
    'Thai': [],  # Thai script
    'Tibt': [],  # Tibetan script
}

ARABIC_NO_EXTENDED_END_LABELS = {
    'Arab': [['''TODO''']],  # Arabic script
    'Armn': [],  # Armenian script
    'Beng': [],  # Bengali script
    'Cyrl': [],  # Cyrillic script
    'Deva': [],  # Devanagari script
    'Ethi': [],  # Ethiopic script
    'Geor': [],  # Georgian script
    'Grek': [],  # Greek script
    'Gujr': [],  # Gujarati script
    'Guru': [],  # Gurmukhi script
    'zh': [],  # Chinese language
    'ko': [],  # Korean language
    'Knda': [],  # kannada
    'Hebr': [],  # Hebrew
    'ja': [],  # Japanese language
    'Khmr': [],  # Khmer script
    'Laoo': [],  # Lao script
    'Latn': [],  # Latin script
    'Mlym': [],  # Malayalam script
    'Mymr': [],  # Myanmar script
    'Orya': [],  # Oriya script
    'Sinh': [],  # Sinala script
    'Taml': [],  # Tamil script
    'Telu': [],  # Telugu script
    'Thaa': [],  # Thaana script
    'Thai': [],  # Thai script
    'Tibt': [],  # Tibetan script
}


class WholeLabelEvaluationRuleReport:

    def __init__(self, idn_table: LGR, idn_table_rule: Rule, reference_lgr_rule: Rule, idn_table_context: Set,
                 reference_lgr_context: Set):
        self.idn_table = idn_table
        self.idn_table_rule = idn_table_rule
        self.reference_lgr_rule = reference_lgr_rule
        self.idn_table_context = idn_table_context
        self.reference_lgr_context = reference_lgr_context
        self.idn_table_repertoire = set(c.cp for c in self.idn_table.repertoire)

    def compare_wle(self) -> Tuple[IdnReviewResult, str]:
        # compare rule regex for rule equality
        if not self.idn_table_rule:
            if self.reference_lgr_context and not (self.idn_table_repertoire & self.reference_lgr_context):
                return (IdnReviewResult.SUBSET,
                        "Match as a subset (for the rules missing in IDN Table, "
                        "applicable code points in Ref. LGR are not in IDN Table)")
            return IdnReviewResult.MANUAL_CHECK, "Mismatch (WLE rule only exists in Ref. LGR)"
        if not self.reference_lgr_rule:
            return IdnReviewResult.MANUAL_CHECK, "Mismatch (WLE rule only exists in IDN Table)"

        if str(self.idn_table_rule) == str(self.reference_lgr_rule):
            if not (self.idn_table_context ^ self.reference_lgr_context):
                return IdnReviewResult.MATCH, "Exact Match (matched names and content)"

        return IdnReviewResult.MANUAL_CHECK, "Check the content of the rule"

    def to_dict(self) -> Dict:
        result, remark = self.compare_wle()
        return {
            'name': self.idn_table_rule.name if self.idn_table_rule else self.reference_lgr_rule.name,
            'idn_table': self.idn_table_rule is not None,
            'reference_lgr': self.reference_lgr_rule is not None,
            'result': result.name,
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
        self.combining_mark = False
        self.has_hyphen = 0x002D in self.idn_table.repertoire
        self.has_digits = False
        self.has_multiple_digits_sets = False
        self.is_rtl = False
        self.check_rtl()
        self.language_tags = []
        self.get_language_tags(self.idn_table)
        if not self.language_tags and self.reference_lgr:
            self.get_language_tags(self.reference_lgr)
        self.get_context_rules()

    def check_rtl(self):
        self.is_rtl = False
        for script in self.idn_table.metadata.get_scripts(allow_invalid=True):
            if self.idn_table.unicode_database.is_script_rtl(script):
                self.is_rtl = True

    def get_language_tags(self, table):
        """
        Retrieve language and scripts
        """
        for language_tag in sorted(table.metadata.languages):
            tag = tags.tag(language_tag)
            if tag.language:
                self.language_tags.append(tag.language.format)
        self.language_tags.extend(table.metadata.get_scripts(allow_invalid=True))

    def get_context_rules(self):
        nbr_digits = 0
        for char in self.idn_table.repertoire.all_repertoire():
            if len(char.cp) == 1:
                cp = char.cp[0]
                if self.idn_table.unicode_database.is_digit(cp):
                    nbr_digits += 1
                    self.has_digits = True
                if self.idn_table.unicode_database.is_combining_mark(cp):
                    self.combining_mark = True
                if not self.language_tags and self.idn_table.unicode_database.is_rtl(cp):
                    # we don't have any language tag, check rtl with code points
                    self.is_rtl = True
            if char.when:
                self.idn_table_context_rules.setdefault(char.when, set()).add(char.cp)
            elif char.not_when:
                self.idn_table_context_rules.setdefault(char.not_when, set()).add(char.cp)
            elif self.reference_lgr and char not in self.reference_lgr.repertoire:
                self.idn_table_char_without_rule.add(char)

        # we consider that there is more than one digit set if we have more than 9 digits
        self.has_multiple_digits_sets = nbr_digits > 10

        if self.reference_lgr:
            for char in self.reference_lgr.repertoire:
                if char.when:
                    self.reference_lgr_context_rules.setdefault(char.when, set()).add(char.cp)
                if char.not_when:
                    self.reference_lgr_context_rules.setdefault(char.not_when, set()).add(char.cp)

    def get_labels(self, collection):
        labels = []
        for ls in self.language_tags:
            ls = SAME_SCRIPTS.get(ls, ls)
            l = collection.get(ls)
            if l:
                labels.extend(l)
        return labels

    def make_report(self, condition, collection):
        result = None
        if condition:
            for label in self.get_labels(collection):
                if not self.check_label_cp_in_repertoire(label):
                    result = None
                    break
                result = not self.test_label(label)
                if not result:
                    # label is eligible, rule does not exist, stop here
                    break

        return {
            'applicable': condition,
            'exists': result,
        }

    def check_label_cp_in_repertoire(self, label):
        i = 0
        result = False
        cp = label[i]

        try:
            char_list = self.idn_table.repertoire.get_chars_from_prefix(cp)
        except NotInLGR:
            return False

        for char in char_list:
            if isinstance(char, CharSequence):
                if not char.is_prefix_of(label[i:]):
                    continue
                else:
                    result |= self.check_label_cp_in_repertoire(label[i + len(char):])
            elif len(label) > 1:
                result |= self.check_label_cp_in_repertoire(label[i + 1:])
            else:
                return True

        return result

    def combining_mark_report(self) -> Dict:
        return self.make_report(self.combining_mark, COMBINING_MARK_LABELS)

    def consecutive_hyphens_report(self) -> Dict:
        return self.make_report(self.has_hyphen, CONSECUTIVE_HYPHEN_LABELS)

    def rtl_report(self) -> Dict:
        return self.make_report(self.is_rtl and self.has_digits, BEGIN_DIGIT_LABELS)

    def digits_set_report(self) -> Dict:
        return self.make_report(self.has_multiple_digits_sets, MULTIPLE_DIGIT_SETS_LABELS)

    def japanese_contextj_report(self) -> Dict:
        contains_katakana_middle_dot = 0x30FB in self.idn_table.repertoire
        return self.make_report(contains_katakana_middle_dot, JAPANESE_CONTEXTJ_LABELS)

    def arabic_no_extended_report(self):
        is_arabic = self.check_language('Arab')
        return self.make_report(is_arabic, ARABIC_NO_EXTENDED_END_LABELS)

    def check_language(self, language_code):
        is_language = False
        for ls in self.language_tags:
            if SAME_SCRIPTS.get(ls, ls) == language_code:
                is_language = True
        return is_language

    def test_label(self, label):
        result, a, b, c, d, e = self.idn_table.test_label_eligible(label)
        return result

    def additional_cp_report(self) -> List[Dict]:
        unidb = self.idn_table.unicode_database
        return cp_report(unidb, sorted(self.idn_table_char_without_rule, key=lambda x: x.cp))


def generate_additional_general_rules(check):
    return {
        'additional_general_rules': {
            'combining_mark': check.combining_mark_report(),
            'consecutive_hyphens': check.consecutive_hyphens_report(),
            'rtl': check.rtl_report(),
            'digits_set': check.digits_set_report(),
            'japanese_contextj': check.japanese_contextj_report(),
            # 'arabic_no_extended_end': check.arabic_no_extended_report(),  # TODO disabled for now
        }
    }


def generate_whole_label_evaluation_rules_report(idn_table: LGR, reference_lgr: LGR) -> Dict:
    check = WholeLabelEvaluationRulesCheck(idn_table, reference_lgr)
    reports = []
    for rule_name in sorted(idn_table.rules_lookup.keys() | reference_lgr.rules_lookup.keys()):
        report = WholeLabelEvaluationRuleReport(idn_table, idn_table.rules_lookup.get(rule_name),
                                                reference_lgr.rules_lookup.get(rule_name),
                                                check.idn_table_context_rules.get(rule_name, set()),
                                                check.reference_lgr_context_rules.get(rule_name, set()))
        reports.append(report.to_dict())

    result = {
        'comparison': reports,
        'additional_cp': check.additional_cp_report(),
    }
    result.update(generate_additional_general_rules(check))
    return result


def generate_whole_label_evaluation_rules_core_report(idn_table: LGR) -> Dict:
    return generate_additional_general_rules(WholeLabelEvaluationRulesCheck(idn_table, None))
