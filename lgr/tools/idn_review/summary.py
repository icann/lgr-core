#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
summary - 
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def handle_report(reports, result_keys=None, remark_keys=None):
    result = 'MATCH'
    remarks = set()

    result_keys = result_keys or ['result']
    remark_keys = remark_keys or ['remark']
    for report in reports:
        for k in result_keys:
            result = report[k]
        for k in remark_keys:
            remarks.update(report[k].split('\n'))

    return {
        'result': result,
        'remark': '\n'.join(remarks)
    }


def generate_summary(reports) -> Dict:
    return {'language_tag': handle_report(c for r in reports['language_tags'] for c in r['comparison']),
            'repertoire': handle_report(reports['repertoire']),
            'variant_sets': handle_report((c for r in reports['variant_sets'] for c in r['report']),
                                          result_keys=('result_fwd', 'result_rev'),
                                          remark_keys=('remark_fwd', 'remark_rev')),
            'classes': handle_report(reports['classes']),
            'wle': handle_report(reports['wle']['comparison']),
            'actions': handle_report(reports['actions']['comparison'])}
