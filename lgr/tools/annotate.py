# -*- coding: utf-8 -*-
"""
annotate.py - Annotate a list of labels with their disposition.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.utils import read_labels
from lgr.tools.diff_collisions import get_collisions

logger = logging.getLogger(__name__)


def annotate(lgr, labels_input):
    """
    Annotate a list of labels with their disposition.

    :param lgr: The LGR info object.
    :param labels_input: The file containing the labels
    """
    for label in read_labels(labels_input, lgr.unicode_database):
        label_cp = tuple([ord(c) for c in label])
        disp = lgr.test_label_eligible(label_cp, collect_log=False)[3]
        yield "%s: %s\n" % (label, disp)


def lgr_set_annotate(lgr, script_lgr, set_labels, labels_input):
    """
    Annotate a list of labels with their disposition.

    :param lgr: The LGR set object.
    :param script_lgr: The LGR object for the script used to check label validity.
    :param set_labels: The labels in the lgr set
    :param labels_input: The file containing the labels
    """
    for label in read_labels(labels_input, script_lgr.unicode_database):
        label_cp = tuple([ord(c) for c in label])
        (eligible, _, _, disp, _, _) = script_lgr.test_label_eligible(label_cp, collect_log=False)
        collision = ''
        if eligible:
            if label in set_labels:
                collision = 'Label is in the LGR set labels'
            # check for collisions
            indexes = get_collisions(lgr, set_labels + [label], quiet=False)
            if len(indexes) > 0:
                collision = 'Label collides with the LGR set labels'

        out = disp
        if collision:
            # TODO do we need to change disp to invalid???
            out = '{} - {}'.format(disp, collision)

        yield "%s: %s\n" % (label, out)

