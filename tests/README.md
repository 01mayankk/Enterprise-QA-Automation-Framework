# Tests Layer

This directory contains Pytest test files and configuration fixtures.

## Contents
* `conftest.py`: Bootstraps WebDriver, initializes logging, runs reports setup/teardown, and captures failure screenshots.
* `test_login.py`: Test scenarios for Login forms.
* `test_registration.py`: Test scenarios for User Registration.
* `test_search.py`: Test scenarios for Product Search.

## Usage
Run these tests using pytest command-line commands or makefile commands (e.g. `make test` or `make test-headless`).
