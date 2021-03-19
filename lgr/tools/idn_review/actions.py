#! /bin/env python
# -*- coding: utf-8 -*-
"""
actions - 
"""
import logging
from collections import OrderedDict
from typing import List, Dict, Set

from lgr.action import Action
from lgr.core import LGR
from lgr.tools.idn_review.utils import IdnReviewResult

logger = logging.getLogger(__name__)


class ActionReport:

    def __init__(self, name: str, is_in_idn_table: bool, is_in_reference_lgr: bool, result: IdnReviewResult,
                 remark: str):
        self.name = name
        self.is_in_idn_table = is_in_idn_table
        self.is_in_reference_lgr = is_in_reference_lgr
        self.result = result
        self.remark = remark

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'idn_table': self.is_in_idn_table,
            'reference_lgr': self.is_in_reference_lgr,
            'result': self.result.name,
            'remark': self.remark
        }


def generate_actions_report(idn_table: LGR, reference_lgr: LGR) -> Dict:
    action_reports: List[ActionReport] = []
    idn_actions = OrderedDict()  # only necessary for Python < 3.7
    ref_actions = OrderedDict()
    idx = 0
    for a in idn_table.actions:
        idx += 1
        name = f' ({a.comment})' if a.comment else ''
        idn_actions[f'IDN Table-{idx}{name}'] = a
    idx = 0
    for a in reference_lgr.actions:
        idx += 1
        name = f' ({a.comment})' if a.comment else ''
        ref_actions[f'Ref. LGR-{idx}{name}'] = a

    matching_actions: Set[Action] = set(idn_actions.values()) & set(ref_actions.values())

    # check sequence of matching actions
    matching_idn_actions_ordered: List[Action] = []
    matching_ref_actions_ordered: List[Action] = []
    for action in idn_actions.values():
        if action in matching_actions:
            matching_idn_actions_ordered.append(action)
    for action in ref_actions.values():
        if action in matching_actions:
            matching_ref_actions_ordered.append(action)

    sequence_match: IdnReviewResult.name = IdnReviewResult.MANUAL_CHECK.name
    if matching_idn_actions_ordered == matching_ref_actions_ordered:
        sequence_match = IdnReviewResult.MATCH.name

    for name, action in idn_actions.items():
        if action in matching_idn_actions_ordered:
            action_reports.append(ActionReport(name, True, True, IdnReviewResult.MATCH,
                                               'Exact Match (action name and content are the same)'))
        else:
            action_reports.append(
                ActionReport(name, True, False, IdnReviewResult.MANUAL_CHECK, 'Mismatch (additional action)'))

    for name, action in ref_actions.items():
        if action in matching_ref_actions_ordered:
            continue
        action_reports.append(
            ActionReport(name, False, True, IdnReviewResult.MANUAL_CHECK, 'Mismatch (missing action)'))

    return {'comparison': [r.to_dict() for r in action_reports], 'sequence': sequence_match}
