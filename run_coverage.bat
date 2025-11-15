@echo off
echo Running tests with coverage...
python -m pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=75 tests/
echo.
echo Coverage report generated in htmlcov/index.html
