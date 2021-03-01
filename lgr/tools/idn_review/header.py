#! /bin/env python
# -*- coding: utf-8 -*-
"""
header - 
"""
import logging
from datetime import date

from lgr.core import LGR

logger = logging.getLogger('header')


def generate_header(idn_table: LGR, reference_lgr: LGR) -> dict:
    try:
        idn_table_version = idn_table.metadata.version.value
    except BaseException:
        idn_table_version = None
    try:
        ref_lgr_version = reference_lgr.metadata.version.value
    except BaseException:
        ref_lgr_version = None

    return {
        'date': date.today(),
        'disclaimer': 'Waiting for ICANN disclaimer',
        'idn_table': {
            'filename': idn_table.name,
            'version': idn_table_version
        },
        'reference_lgr': {
            'name': reference_lgr.name,
            'version': ref_lgr_version
        }
    }
