#!/bin/sh

# Small helper to execute all tests.

echo Running tests and coverage report
pytest --cov-branch --cov-report=html --cov=lgr --doctest-modules
echo Report is in htmlcov/index.html