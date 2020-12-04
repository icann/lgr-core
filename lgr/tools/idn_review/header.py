#! /bin/env python
# -*- coding: utf-8 -*-
# Author: Viagénie
"""
header - 
"""
import logging
from datetime import date

from lgr.core import LGR

logger = logging.getLogger('header')


def generate_header(idn_table: LGR, reference_lgr: LGR) -> dict:
    return {
        'date': date.today(),
        'disclaimer': 'TODO',
        'idn_table': {
            'filename': idn_table.name,
            'version': idn_table.metadata.version.value
        },
        'reference_lgr': {
            'name': reference_lgr.name,
            'version': reference_lgr.metadata.version.value
        }
    }
