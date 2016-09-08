# -*- coding: utf-8 -*-
"""
annotate.py - Annotate a list of labels with their disposition.
"""
from __future__ import unicode_literals

import logging

from lgr.tools.utils import read_labels

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
