#!/bin/sh

# Small helper to execute all tests.

echo Running tests and coverage report
# --nologcapture: needed since some tests (validate) depends on the log output
# --with-doctest: enable doctests
nosetests --nologcapture --with-doctest --with-coverage --cover-branches --cover-html --cover-package=lgr
echo Report is in cover/index.html
