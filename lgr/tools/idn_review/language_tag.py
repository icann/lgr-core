#! /bin/env python
# -*- coding: utf-8 -*-
"""
language_tag - 
"""
import logging
from typing import List, Tuple, Dict

from language_tags import tags

from lgr.core import LGR
from lgr.tools.idn_review.utils import IdnReviewResult
from lgr.utils import tag_to_language_script

logger = logging.getLogger(__name__)


class LanguageTagReport:

    def __init__(self, idn_table_tag: str, reference_lgr_languages: List[str]):
        self.idn_table_tag = idn_table_tag
        self.reference_lgr_languages = reference_lgr_languages

    def compare_with_tag(self, tag: str) -> Tuple[IdnReviewResult, str]:
        if self.idn_table_tag is None:
            return IdnReviewResult.MANUAL_CHECK, "Language tag may be included in the comment"

        idn_language, idn_script = tag_to_language_script(self.idn_table_tag)
        ref_language, ref_script = tag_to_language_script(tag)

        if idn_language == ref_language and idn_script == ref_script:
            return IdnReviewResult.MATCH, "Exact match"

        idn_tag = tags.tag(self.idn_table_tag)
        if idn_tag.ERR_UNKNOWN in [e.code for e in idn_tag.errors]:
            return IdnReviewResult.MANUAL_CHECK, "Language tag may be included in the comment"

        if idn_language and idn_language == ref_language:
            if idn_tag.ERR_SUPPRESS_SCRIPT in [e.code for e in idn_tag.errors]:
                return (IdnReviewResult.MATCH,
                        "Consider minimizing the tag as per the RFC5646 and IANA subtag registry")
            return IdnReviewResult.MATCH, "Language match"

        if (idn_tag.language and idn_tag.language.script and ref_script and
                idn_tag.language.script.format == ref_script):
            return IdnReviewResult.MATCH, "The language tag in IDN Table relevant to the script tag in Reference LGR"

        return IdnReviewResult.REVIEW, "The language tag in IDN Table and Reference LGR are mismatched"

    def to_dict(self):
        comparisons = []
        for tag in self.reference_lgr_languages:
            result, remark = self.compare_with_tag(tag)
            comparisons.append({
                'reference_lgr_language_tag': tag,
                'result': result.name,
                'remark': remark
            })
        return {
            'idn_table_language_tag': self.idn_table_tag or '-',
            'comparison': sorted(comparisons, key=lambda x: x['reference_lgr_language_tag'])
        }


def generate_language_tag_report(idn_table: LGR, reference_lgr: LGR) -> List[Dict]:
    reports: List[Dict] = []
    language_tags = sorted(idn_table.metadata.languages)
    for language_tag in language_tags:
        reports.append(LanguageTagReport(language_tag, reference_lgr.metadata.languages).to_dict())
    if not language_tags:
        reports.append(LanguageTagReport(None, reference_lgr.metadata.languages).to_dict())

    return reports
