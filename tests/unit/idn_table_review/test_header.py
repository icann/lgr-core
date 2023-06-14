#! /bin/env python
# -*- coding: utf-8 -*-
"""
test_header - 
"""
import logging
from datetime import date
from unittest import TestCase

from lgr.tools.idn_review.header import generate_header
from tests.unit.utils import load_lgr

logger = logging.getLogger('test_header')


class Test(TestCase):

    def test_generage_header(self):
        ref = load_lgr('idn_table_review', 'reference_lgr.xml')
        idn = load_lgr('idn_table_review/header', 'header.xml')

        self.assertDictEqual(generate_header(idn, ref),
                             {
                                 'date': date.today(),
                                 'disclaimer': 'Please refer to the LGR (IDN Table) Review Tool disclaimer on this '
                                               '<a href="https://www.icann.org/resources/pages/lgr-toolset-2015-06-21-en" '
                                               'target="_blank" rel="noopener noreferrer">page</a>',
                                 'idn_table': {
                                     'filename': 'header.xml',
                                     'version': '2'
                                 },
                                 'reference_lgr': {
                                     'name': 'reference_lgr.xml',
                                     'version': '1'
                                 }
                             })


    def test_generage_header_core_requirements(self):
        idn = load_lgr('idn_table_review/header', 'header.xml')

        self.assertDictEqual(generate_header(idn),
                             {
                                 'date': date.today(),
                                 'disclaimer': 'Please refer to the LGR (IDN Table) Review Tool disclaimer on this '
                                               '<a href="https://www.icann.org/resources/pages/lgr-toolset-2015-06-21-en" '
                                               'target="_blank" rel="noopener noreferrer">page</a>',
                                 'idn_table': {
                                     'filename': 'header.xml',
                                     'version': '2'
                                 }
                             })
