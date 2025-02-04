#!/bin/sh

# Small helper to execute all tests.

echo Running tests and coverage report
python3 -m pip install -r tests/requirements.txt
pytest --cov-branch --cov-report=html --cov=lgr --doctest-modules
echo Report is in htmlcov/index.html
