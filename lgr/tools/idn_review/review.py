#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
review - 
"""
import logging

from lgr.core import LGR
from lgr.tools.idn_review.actions import generate_actions_report
from lgr.tools.idn_review.classes import generate_classes_report
from lgr.tools.idn_review.header import generate_header
from lgr.tools.idn_review.language_tag import generate_language_tag_report
from lgr.tools.idn_review.repertoire import generate_repertoire_report
from lgr.tools.idn_review.summary import generate_summary
from lgr.tools.idn_review.variant_sets import generate_variant_sets_report
from lgr.tools.idn_review.whole_label_evaluation_rules import generate_whole_label_evaluation_rules_report

logger = logging.getLogger(__name__)


def review_lgr(idn_table: LGR, reference_lgr: LGR):
    report = {'header': generate_header(idn_table, reference_lgr),
              'language_tag': generate_language_tag_report(idn_table, reference_lgr),
              'repertoire': generate_repertoire_report(idn_table, reference_lgr),
              'variant_sets': generate_variant_sets_report(idn_table, reference_lgr),
              'classes': generate_classes_report(idn_table, reference_lgr),
              'wle': generate_whole_label_evaluation_rules_report(idn_table, reference_lgr),
              'actions': generate_actions_report(idn_table, reference_lgr)}
    report['summary'] = generate_summary(report)
    print(report)
