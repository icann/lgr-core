#!/bin/env python2
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="lgr-core",
    version='1.9',
    author='Viagénie and Wil Tan',
    author_email='support@viagenie.ca',
    description="API for manipulating Label Generation Rules",
    long_description=open('README.md').read(),
    license="TBD",
    install_requires=['lxml', 'language-tags', 'munidata', 'picu'],
    packages=find_packages(),
    scripts=['tools/lgr_cli.py',
             'tools/lgr_validate.py',
             'tools/rfc4290_dump.py',
             'tools/one_per_line_dump.py',
             'tools/rfc3743_dump.py',
             'tools/xml_dump.py',
             'tools/make_idna_repertoire.py',
             'tools/lgr_annotate.py',
             'tools/lgr_collision.py',
             'tools/lgr_compare.py',
             'tools/lgr_diff_collisions.py',
             'tools/lgr_merge_set.py',
             'tools/lgr_cross_script_variants.py',
             'tools/lgr_check_harmonized.py'
             ],
    tests_require=['nose', 'coverage'],
    test_suite='tests.unit',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ]
)
