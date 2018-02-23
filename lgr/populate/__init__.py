# -*- coding: utf-8 -*-
"""
__init__.py - Populate variants in an LGR
"""
from __future__ import unicode_literals

import logging

from lgr.exceptions import VariantAlreadyExists, NotInLGR
from lgr.validate.symmetry import check_symmetry
from lgr.validate.transitivity import check_transitivity
from lgr.utils import format_cp

logger = logging.getLogger(__name__)


def populate_lgr(lgr):
    """
    Populate an LGR with missing variants, and fix symmetry and transitivity

    :param lgr: The LGR to be populated.
    :return: Result of checks and summary as a string
    """
    return _populate_variants_1(lgr)


def _populate_variants_1(lgr):
    now_in_lgr = []
    # not in LGR variants
    for a in lgr.repertoire:
        for b in a.get_variants():
            try:
                lgr.get_variants(b.cp)
            except NotInLGR:
                if b.cp not in now_in_lgr:
                    logger.info("Add missing code point '{}' in LGR as it is a variant of '{}'".format(
                        format_cp(b.cp), format_cp(a.cp)))
                    lgr.add_cp(b.cp)
                    now_in_lgr.append(b.cp)
                # add current code point as variant for missing code point
                logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                         format_cp(b.cp)))
                lgr.add_variant(b.cp, a.cp)

    while not check_symmetry(lgr, None) or not check_transitivity(lgr, None):
        # symmetry
        for a in lgr.repertoire:
            for b in a.get_variants():
                # Variant is defined in repertoire
                # let's see if the original character is in its
                # variants
                if a.cp not in [var.cp for var in lgr.get_variants(b.cp)]:
                    logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                             format_cp(b.cp)))
                    lgr.add_variant(b.cp, a.cp)

        # transitivity
        for a in lgr.repertoire:
            for b in a.get_variants():
                for c in [var for var in lgr.get_variants(b.cp) if var.cp != a.cp]:
                    # Iterate through all second-level variants
                    # which are not the original code point
                    if c.cp not in [var.cp for var in a.get_variants()]:
                        logger.info("Add code point '{}' as variant of '{}' for transitivity with '{}'".format(
                            format_cp(c.cp), format_cp(a.cp), format_cp(b.cp)))
                        lgr.add_variant(a.cp, c.cp)


def _populate_variants_2(lgr):
    now_in_lgr = []
    # not in LGR variants
    for a in lgr.repertoire:
        for b in a.get_variants():
            try:
                lgr.get_variants(b.cp)
            except NotInLGR:
                if b.cp not in now_in_lgr:
                    logger.info("Add missing code point '{}' in LGR as it is a variant of '{}'".format(
                        format_cp(b.cp), format_cp(a.cp)))
                    lgr.add_cp(b.cp)
                    now_in_lgr.append(b.cp)
                # add current code point as variant for missing code point
                logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                         format_cp(b.cp)))
                lgr.add_variant(b.cp, a.cp)

    variants_sets_mapping = {}
    for a in lgr.repertoire:
        current_set = variants_sets_mapping.get(a.cp, {a.cp})
        for b in a.get_variants():
            b_set = variants_sets_mapping.get(b.cp, {b.cp})
            current_set |= b_set
        variants_sets_mapping[a.cp] = current_set
        for c in current_set:
            c_set = variants_sets_mapping.get(c, {c})
            c_set |= current_set
            variants_sets_mapping[c] = c_set

    for codepoint, variants in variants_sets_mapping.items():
        cp = lgr.get_char(codepoint)
        cp_variants = [v.cp for v in cp.get_variants()]
        for v in variants:
            if v == codepoint:
                continue
            if v not in cp_variants:
                lgr.add_variant(cp.cp, v)
                logger.info("Add code point '{}' as variant of '{}'".format(format_cp(v), format_cp(cp.cp)))
            try:
                lgr.add_variant(v, cp.cp)
                logger.info("Add code point '{}' as variant of '{}'".format(format_cp(cp.cp), format_cp(v)))
            except VariantAlreadyExists:
                pass


def _populate_variants_3(lgr):
    """
    This one does not actually populate correctly the LGR but it uses an already existing function so this may be
    fixed to do the job
    """
    now_in_lgr = []
    # not in LGR variants
    for a in lgr.repertoire:
        for b in a.get_variants():
            try:
                lgr.get_variants(b.cp)
            except NotInLGR:
                if b.cp not in now_in_lgr:
                    logger.info("Add missing code point '{}' in LGR as it is a variant of '{}'".format(
                        format_cp(b.cp), format_cp(a.cp)))
                    lgr.add_cp(b.cp)
                    now_in_lgr.append(b.cp)
                # add current code point as variant for missing code point
                logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                         format_cp(b.cp)))
                lgr.add_variant(b.cp, a.cp)

    while not check_symmetry(lgr, None) or not check_transitivity(lgr, None):
        variants_sets = lgr.repertoire.get_variant_sets()
        for variant_set in variants_sets:
            for a in variant_set:
                cp = lgr.get_char(a)
                cp_variants = [v.cp for v in cp.get_variants()]
                for b in variant_set:
                    if a == b:
                        continue

                    if b not in cp_variants:
                        lgr.add_variant(cp.cp, b)
                        logger.info("Add code point '{}' as variant of '{}'".format(format_cp(b), format_cp(cp.cp)))
                    try:
                        lgr.add_variant(b, cp.cp)
                        logger.info("Add code point '{}' as variant of '{}'".format(format_cp(cp.cp), format_cp(b)))
                    except VariantAlreadyExists:
                        pass
