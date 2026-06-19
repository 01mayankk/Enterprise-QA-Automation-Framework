# Screenshots Directory

This directory stores screenshots captured when tests fail.

## Contents
* PNG files named after the failed test, containing the test name, browser name, environment name, and an execution timestamp (e.g. `test_login_invalid_password_chrome_qa_2026-06-19_18-30-00.png`).

## Usage
Screenshots are taken automatically by `ScreenshotManager` when a test failure is caught by the test runner hooks in `tests/conftest.py`. They are also embedded in the HTML report.
