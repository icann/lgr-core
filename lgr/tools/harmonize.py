# -*- coding: utf-8 -*-
"""
harmonized.py - Perform LGR harmonization
"""
from __future__ import unicode_literals

import logging
from copy import deepcopy

from lgr.populate import populate_lgr

logger = logging.getLogger(__name__)


def harmonize(lgr_1, lgr_2, rz_lgr=None, script=None, _copy=True):
    """
    Harmonize 2 LGRs, using an optional related Rootzone LGR.

    This function will expand all ranges on the input LGRs `lgr_1` and `lgr_2`.

    :param lgr_1: First LGR. Will have its ranges expanded.
    :param lgr_2: Second LGR. Will have its ranges expanded.
    :param rz_lgr: Optional related Rootzone LGR.
    :param script: Optional script to consider in `rz_lgr`.
    :param _copy: If False, update the input `lgr_1`, `lgr_2` parameters instead of doing a copy.
    :return: (h_lgr_1, h_lgr_2, (lgr_1_cp_review, lgr_2_cp_review)), with:
             - h_lgr_1: Harmonized first LGR.
             - h_lgr_2: Harmonized second LGR.
             - lgr_1_cp_review: List of code points to be manually reviewed from `lgr_1`.
             - lgr_2_cp_review: List of code points to be manually reviewed from `lgr_2`.
    """

    h_lgr_1 = deepcopy(lgr_1) if _copy else lgr_1
    h_lgr_2 = deepcopy(lgr_2) if _copy else lgr_2

    h_lgr_1.expand_ranges()
    h_lgr_2.expand_ranges()

    for lgr in (h_lgr_1, h_lgr_2):
        if lgr.metadata.version is not None:
            lgr.metadata.version.comment = lgr.metadata.version.comment or '' + ' - Harmonized'

    # New variants from RZ-LGR - harmonize each of the LGR with the RZ-LGR for the given script
    if rz_lgr is not None:
        rz_lgr_script = deepcopy(rz_lgr)
        for char in rz_lgr.repertoire:
            if rz_lgr.unicode_database is not None and rz_lgr.unicode_database.get_script(char.cp[0]) != script:
                rz_lgr_script.del_cp(char.cp)
        harmonize(h_lgr_1, rz_lgr_script, _copy=False)
        harmonize(h_lgr_2, rz_lgr_script, _copy=False)

    # Perform harmonization between the 2 LGRs
    lgr_1_repertoire = {c.cp for c in h_lgr_1.repertoire}
    lgr_2_repertoire = {c.cp for c in h_lgr_2.repertoire}

    # Chars present in both LGRs
    for cp in lgr_2_repertoire & lgr_1_repertoire:
        char_lgr_1 = h_lgr_1.get_char(cp)
        char_lgr_2 = h_lgr_2.get_char(cp)

        lgr_1_variants = {v.cp for v in char_lgr_1.get_variants()}
        lgr_2_variants = {v.cp for v in char_lgr_2.get_variants()}

        # Find variants present in LGR 1 but not 2
        for variant_cp in lgr_1_variants - lgr_2_variants:
            if variant_cp not in lgr_2_repertoire:
                # Add variant to repertoire
                h_lgr_2.add_cp(variant_cp, comment='Out-of-repertoire')
            # Add variant to LGR 2
            h_lgr_2.add_variant(cp, variant_cp, variant_type='blocked')
        # Find variants present in LGR 2 but not 1
        for variant_cp in lgr_2_variants - lgr_1_variants:
            if variant_cp not in lgr_1_repertoire:
                # Add variant to repertoire
                h_lgr_1.add_cp(variant_cp, comment='Out-of-repertoire')
            # Add variant to LGR 1
            h_lgr_1.add_variant(cp, variant_cp, variant_type='blocked')

    # Ensure resulting LGRs are symmetric and transitive
    populate_lgr(h_lgr_1)
    populate_lgr(h_lgr_2)

    not_touched_cp = lgr_1_repertoire ^ lgr_2_repertoire

    return h_lgr_1, h_lgr_2, (lgr_1_repertoire & not_touched_cp, lgr_2_repertoire & not_touched_cp)
