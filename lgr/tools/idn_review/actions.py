#! /bin/env python
# -*- coding: utf-8 -*-
"""
actions - 
"""
import logging
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
    idn_actions = {a: None for a in idn_table.actions}
    ref_actions = {a: None for a in reference_lgr.actions}

    matching_actions: Set[str] = idn_actions.keys() & ref_actions.keys()

    # check sequence of matching actions
    matching_idn_actions_ordered: List[Action] = []
    matching_ref_actions_ordered: List[Action] = []
    for action in idn_actions:
        if action in matching_actions:
            matching_idn_actions_ordered.append(action)
    for action in ref_actions:
        if action in matching_actions:
            matching_ref_actions_ordered.append(action)

    sequence_match: IdnReviewResult.name = IdnReviewResult.MANUAL_CHECK.name
    if matching_idn_actions_ordered == matching_ref_actions_ordered:
        sequence_match = IdnReviewResult.MATCH.name

    for action in matching_idn_actions_ordered:
        action_reports.append(ActionReport(str(action), True, True, IdnReviewResult.MATCH,
                                           'Exact Match (action name and content are the same)'))

    for action in idn_actions.keys() - ref_actions.keys():
        action_reports.append(
            ActionReport(str(action), True, False, IdnReviewResult.MANUAL_CHECK,
                         'Mismatch (additional action)'))

    for action in ref_actions.keys() - idn_actions.keys():
        action_reports.append(
            ActionReport(str(action), False, True, IdnReviewResult.MANUAL_CHECK,
                         'Mismatch (missing action)'))

    return {'comparison': [r.to_dict() for r in action_reports], 'sequence': sequence_match}
