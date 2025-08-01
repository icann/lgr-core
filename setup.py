#!/bin/env python
# -*- coding: utf-8 -*-
from io import open
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# From https://docs.pytest.org/en/latest/goodpractices.html#manual-integration
# See if we could instead use pytest-runner
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(
    name="lgr-core",
    version='6.1.3',
    author='Cofomo, Viagénie and Wil Tan',
    author_email='int-eng@cofomo.com',
    description="API for manipulating Label Generation Rules",
    long_description=open('README.md', encoding='utf-8').read(),
    license="BSD",
    install_requires=['lxml', 'language-tags', 'pycountry', 'munidata', 'picu'],
    packages=find_packages(),
    scripts=[
        'tools/lgr_cli.py',
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
        'tools/lgr_harmonize',
        'tools/lgr_populate_variants.py',
        'tools/rfc7940_validate.py',
        'tools/lgr_idn_table_review.py'
    ],
    tests_require=['idna', 'pytest', 'pytest-cov'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries'
    ]
)
