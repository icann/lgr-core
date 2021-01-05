# -*- coding: utf-8 -*-
"""
annotate.py - Annotate a list of labels with their disposition.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.utils import read_labels

logger = logging.getLogger(__name__)


def _out_valid_label(lgr, label, eligible, label_invalid_parts, disp, action_idx):
    yield "%s: %s\n" % (label, disp)
    if not eligible and action_idx > 0:
        yield " Rule %s: %s\n" % (action_idx, lgr.effective_actions[action_idx])
    for cp_not_in_lgr, rules in label_invalid_parts:
        yield " Code point {cp} {reason}\n".format(
            cp="U+{:04X}".format(cp_not_in_lgr),
            reason="not in repertoire" if rules is None else "does not comply with rules '{}'".format(','.join(rules))
        )


def annotate(lgr, labels_input):
    """
    Annotate a list of labels with their disposition.

    :param lgr: The LGR info object.
    :param labels_input: The file containing the labels
    """
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if valid:
            label_cp = tuple([ord(c) for c in label])
            (eligible, _, label_invalid_parts, disp, action_idx, _) = lgr.test_label_eligible(label_cp,
                                                                                              collect_log=False)
            for l in _out_valid_label(lgr, label, eligible, label_invalid_parts, disp, action_idx):
                yield l
        else:
            yield "%s: %s\n" % (label, error)


def lgr_set_annotate(lgr, script_lgr, set_labels_input, labels_input):
    """
    Annotate a list of labels with their disposition.

    :param lgr: The LGR set object.
    :param script_lgr: The LGR object for the script used to check label validity.
    :param set_labels_input: The labels in the lgr set.
    :param labels_input: The file containing the labels
    """
    from lgr.tools.diff_collisions import get_collisions

    # First, we need to filter-out out-of-LGR labels from the set_labels_input:
    yield "# The following labels from the set labels are invalid\n"
    filtered_set = []
    for label, valid, error in read_labels(set_labels_input, lgr.unicode_database):
        if not valid:
            yield "%s: %s\n" % (label, error)
        else:
            label_cp = tuple([ord(c) for c in label])
            if not lgr._test_preliminary_eligibility(label_cp)[0]:
                yield "%s: invalid\n" % label
            else:
                filtered_set.append(label)
    yield "# End of filtered set labels\n\n"

    for label, valid, error in read_labels(labels_input, script_lgr.unicode_database):
        if not valid:
            out = error
            yield "%s: %s\n" % (label, out)
        else:
            label_cp = tuple([ord(c) for c in label])
            # First, verify that a proposed label is valid by processing it with the Element LGR
            # corresponding to the script that was selected for the label in the application.
            (eligible, _, label_invalid_parts, disp, action_idx, _) = script_lgr.test_label_eligible(label_cp,
                                                                                                     collect_log=False)
            collision = ''
            if eligible:
                # Second, process the now validated label against the common LGR to verify it does not collide
                # with any existing delegated labels (and any of their variants, whether blocked or allocatable).
                if label in filtered_set:
                    collision = 'Label is in the LGR set labels'
                indexes = get_collisions(lgr, filtered_set + [label], quiet=False)
                if len(indexes) > 0:
                    collision = 'Label collides with the LGR set labels'

            out = disp
            if collision:
                # TODO do we need to change disp to invalid???
                out = '{} - {}'.format(disp, collision)

            for l in _out_valid_label(lgr, label, eligible, label_invalid_parts, out, action_idx):
                yield l
