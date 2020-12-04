#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
actions - 
"""
import logging
from enum import auto
from typing import List, Dict, Set

from lgr.action import Action
from lgr.core import LGR
from lgr.tools.idn_review.utils import AutoName

logger = logging.getLogger(__name__)


class ActionResult(AutoName):
    MATCH = auto()
    MANUAL_CHECK = auto()


class ActionReport:

    def __init__(self, name: str, is_in_idn_table: bool, is_in_reference_lgr: bool, result: ActionResult, remark: str):
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
            'result': self.result.value,
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

    sequence_match: ActionResult.value = ActionResult.MANUAL_CHECK.value
    if matching_idn_actions_ordered == matching_ref_actions_ordered:
        sequence_match = ActionResult.MATCH.value

    for action in matching_idn_actions_ordered:
        action_reports.append(ActionReport(str(action), True, True, ActionResult.MATCH,
                                           'Exact Match (action name and content are the same)'))

    for action in idn_actions.keys() - ref_actions.keys():
        action_reports.append(
            ActionReport(str(action), True, False, ActionResult.MANUAL_CHECK,
                         'Mismatch (additional action)'))

    for action in ref_actions.keys() - idn_actions.keys():
        action_reports.append(
            ActionReport(str(action), False, True, ActionResult.MANUAL_CHECK,
                         'Mismatch (missing action)'))

    return {'comparison': [r.to_dict() for r in action_reports], 'sequence': sequence_match}
