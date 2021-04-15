#! /bin/env python
# -*- coding: utf-8 -*-
"""
summary - 
"""
import logging
from collections import Counter
from typing import Dict

from lgr.tools.idn_review.utils import IdnReviewResult

logger = logging.getLogger(__name__)


def handle_report(reports, keys=None):
    result = IdnReviewResult.MANUAL_CHECK.name
    remarks = Counter()
    result_remarks = {}

    keys = keys or (('result', 'remark'),)
    for report in reports:
        for res_k, rem_k in keys:
            result = report[res_k] if result and IdnReviewResult[report[res_k].replace(' ', '_')] > IdnReviewResult[
                result.replace(' ', '_')] else result
            result_remarks[report[rem_k]] = report[res_k]
            remarks.update((report[rem_k],))

    return {
        'overall': result,
        'results': [{
            'result': result_remarks[k],
            'remark': k,
            'count': v
        } for k, v in remarks.items()]
    }


def generate_summary(reports) -> Dict:
    return {'language_tag': handle_report(c for r in reports['language_tags'] for c in r['comparison']),
            'repertoire': handle_report(reports['repertoire']['reports']),
            'variant_sets': handle_report((c for r in reports['variant_sets']['reports'] for c in r['report']),
                                          keys=(('result_fwd', 'remark_fwd'), ('result_rev', 'remark_rev'))),
            'classes': handle_report(reports['classes']),
            'wle': handle_report(reports['wle']['comparison']),
            'actions': handle_report(reports['actions']['comparison'])}
