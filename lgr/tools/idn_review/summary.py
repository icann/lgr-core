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


def handle_report(reports, result_keys=None, remark_keys=None):
    result = IdnReviewResult.MATCH.name
    remarks = Counter()

    result_keys = result_keys or ['result']
    remark_keys = remark_keys or ['remark']
    for report in reports:
        for k in result_keys:
            result = report[k] if result and IdnReviewResult[report[k].replace(' ', '_')] > IdnReviewResult[
                result.replace(' ', '_')] else result
        for k in remark_keys:
            remarks.update((report[k],))

    return {
        'result': result,
        'remark': {k: v for k, v in remarks.items()} if remarks else {'-': '-'}
    }


def generate_summary(reports) -> Dict:
    return {'language_tag': handle_report(c for r in reports['language_tags'] for c in r['comparison']),
            'repertoire': handle_report(reports['repertoire']),
            'variant_sets': handle_report((c for r in reports['variant_sets']['reports'] for c in r['report']),
                                          result_keys=('result_fwd', 'result_rev'),
                                          remark_keys=('remark_fwd', 'remark_rev')),
            'classes': handle_report(reports['classes']),
            'wle': handle_report(reports['wle']['comparison']),
            'actions': handle_report(reports['actions']['comparison'])}
