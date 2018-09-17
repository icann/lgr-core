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
    version='2.0.0',
    author='Viagénie and Wil Tan',
    author_email='support@viagenie.ca',
    description="API for manipulating Label Generation Rules",
    long_description=open('README.md', encoding='utf-8').read(),
    license="TBD",
    install_requires=['lxml', 'language-tags', 'munidata', 'picu'],
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
        'tools/lgr_cross_script_variants.py',
        'tools/lgr_harmonize'
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
