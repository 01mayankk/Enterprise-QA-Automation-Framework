# Execution Reporting & Email Guide

This document describes the structure of generated HTML reports, failure diagnostics metadata, and the SMTP email notification setup.

---

## 1. Pytest HTML Report (`reports/report.html`)

The test suite uses `pytest-html` to generate an interactive, self-contained HTML report. 

### 1.1 Custom HTML Design
- **Title and Meta Header**: Styled with custom headers (Target Environment, Base URL, Execution Timestamp, Author).
- **Execution Log Alignment**: The detailed traceback logs are embedded right beside the failed test row.

### 1.2 Failure Diagnostics Integration
On test failure, the framework captures the failure state immediately and inserts a formatted HTML block containing:
- **Timestamp**: Exact execution date and time.
- **Target URL**: Active browser page URL where the failure was caught.
- **Browser & Version**: Name and release version of the executing driver.
- **Resolution**: Window size of the browser window.
- **Exception Message**: The exception text thrown by Pytest.
- **Stack Trace**: Traceback steps in a collapsible, scrollable code container.

---

## 2. Screenshot Highlights & Embedding

Screenshots are embedded directly into the HTML report as Base64 strings. This ensures the report is a single, self-contained file that can be sent over email or viewed on another machine without missing images.

### 2.1 Visual Failure Indicator
- **Highlighting**: The framework executes JavaScript to style the target element with a red border:
  ```javascript
  arguments[0].style.border = '3px solid red';
  ```
- **Zoom Preview**: Hovering over the image in the HTML report applies a hover zoom effect. Clicking the screenshot opens the full-size image in a new tab.

---

## 3. Execution Summary Markdown (`reports/execution_summary.md`)

At the end of a test run, the `pytest_sessionfinish` hook in `conftest.py` parses the session results and writes a markdown summary file. This is a lightweight, easy-to-read summary of the run:

### Example Summary Markdown
```markdown
# Test Execution Summary

**Date:** 2026-06-19 18:30:45  
**Browser:** CHROME  
**Environment:** QA  
**Base URL:** https://demowebshop.tricentis.com/  

## Test Metrics
| Metric | Count |
| :--- | :--- |
| **Total Tests** | 10 |
| **Passed** | 8 |
| **Failed** | 2 |
| **Skipped** | 0 |
| **Duration** | 45.20 seconds |
```

---

## 4. Optional Email Distribution (`utils/email_sender.py`)

The framework includes an email distribution utility using Python's standard `smtplib` library.

### 4.1 Configuration Settings (`config/config.json`)
```json
"email_config": {
  "enabled": false,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "testautomation@example.com",
  "sender_password": "your_app_password",
  "receiver_email": "qa-team@example.com",
  "send_on_failure_only": true
}
```

### 4.2 How to trigger email distribution
1. Enable the email configuration in `config.json` by setting `"enabled": true`.
2. To trigger email delivery programmatically after a test run, execute:
   ```bash
   python utils/email_sender.py
   ```
   This script reads `reports/execution_summary.md` and sends the summary as the email body, with `reports/report.html` attached.
