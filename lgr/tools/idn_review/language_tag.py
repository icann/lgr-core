#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
language_tag - 
"""
import logging
from enum import auto
from typing import List, Tuple, Dict

from language_tags import tags

from lgr.core import LGR
from lgr.tools.idn_review.utils import AutoName

logger = logging.getLogger(__name__)


class LanguageTagResult(AutoName):
    MATCH = auto()
    REVIEW = auto()
    MANUAL_CHECK = auto()


class LanguageTagReport:

    def __init__(self, idn_table_tag: str, reference_lgr_languages: List[str]):
        self.idn_table_tag = idn_table_tag
        self.reference_lgr_languages = reference_lgr_languages

    @staticmethod
    def compare_language(tag1, tag2):
        return tag1.language and tag2.language and tag1.language.format == tag2.language.format

    def compare_with_tag(self, tag: str) -> Tuple[LanguageTagResult, str]:
        if self.idn_table_tag == tag:
            return LanguageTagResult.MATCH, "Exact match"

        idn_tag = tags.tag(self.idn_table_tag)
        ref_tag = tags.tag(tag)
        if self.compare_language(idn_tag, ref_tag):
            if idn_tag.ERR_SUPPRESS_SCRIPT in [e.code for e in idn_tag.errors]:
                return (
                LanguageTagResult.MATCH, "Consider minimizing the tag as per the RFC5646 and IANA subtag registry")
            return LanguageTagResult.MATCH, "Language match"

        if (idn_tag.language and idn_tag.language.script and ref_tag.script and
                idn_tag.language.script.format == ref_tag.script.format):
            return LanguageTagResult.MATCH, "The language tag in IDN Table relevant to the script tag in Reference LGR"

        if idn_tag.ERR_UNKNOWN in [e.code for e in idn_tag.errors]:
            return LanguageTagResult.MANUAL_CHECK, "Language tag may have been included in the comment"

        return LanguageTagResult.REVIEW, "The language tag in IDN Table and Reference LGR are mismatched"

    def to_dict(self):
        comparisons = []
        for tag in self.reference_lgr_languages:
            result, remark = self.compare_with_tag(tag)
            comparisons.append({
                'reference_lgr_language_tag': tag,
                'result': result.value,
                'remark': remark
            })
        return {
            'idn_table_language_tag': self.idn_table_tag,
            'comparison': sorted(comparisons, key=lambda x: x['reference_lgr_language_tag'])
        }


def generate_language_tag_report(idn_table: LGR, reference_lgr: LGR) -> List[Dict]:
    reports: List[Dict] = []
    for language_tag in sorted(idn_table.metadata.languages):
        reports.append(LanguageTagReport(language_tag, reference_lgr.metadata.languages).to_dict())

    return reports