# Architecture Decision Records (ADR)

This document outlines the architectural decisions made when designing this testing framework, along with the alternatives considered and rejected.

---

## ADR 1: Choose Selenium WebDriver as the Browser Automation Engine

### Context & Requirements
The framework needs to automate web browsers across different operating systems. It must also run headlessly in Docker containers and CI/CD environments.

### Decision
Use **Selenium WebDriver** (via `selenium` Python library).

### Alternatives Considered & Rejected
- **Playwright**: Playwright is a modern automation tool with fast execution speeds and auto-waiting features. However, Selenium is still the industry standard with a larger job market. Using Selenium allows students to demonstrate understanding of core automation challenges (like sync waits, webdriver drivers, and browser capabilities) which are common interview topics.
- **Cypress**: Cypress is limited to JavaScript/TypeScript, whereas this framework requires Python to align with Computer Science student profiles.

---

## ADR 2: Choose Pytest as the Test Runner

### Context & Requirements
We need a test runner that supports test execution, fixtures, test parametrization for data-driven testing, and HTML report plugins.

### Decision
Use **Pytest**.

### Alternatives Considered & Rejected
- **unittest (Python Standard Library)**: Unittest is the built-in unit testing framework. However, it requires writing boilerplate class structures for every test file. Pytest supports clean, function-based tests and features a powerful fixture model (`yield` setups/teardowns) that is cleaner than unittest's `setUp` and `tearDown` methods.

---

## ADR 3: Choose CSV for Data-Driven Testing

### Context & Requirements
We need to run the same login test case with multiple sets of credentials (valid, invalid, format errors, blank fields).

### Decision
Use standard **CSV files** (via Python's built-in `csv` library).

### Alternatives Considered & Rejected
- **Excel (OpenPyXL/Pandas)**: Excel files require installing large third-party libraries (`openpyxl` or `pandas`). Reading CSV files is faster, does not require third-party dependencies, and can be easily tracked inside Git diffs.
- **Database (SQLite/MySQL)**: Database integrations increase complexity by requiring database servers or local file management. This is unnecessary for basic test suite configurations.

---

## ADR 4: Choose Docker & Docker Compose for Containerization

### Context & Requirements
We want to package the test suite so it runs consistently across different machines without needing local setups.

### Decision
Use **Docker and Docker Compose**.

### Alternatives Considered & Rejected
- **Local Virtual Environments only (`venv`)**: Virtual environments isolate Python packages, but they do not manage system-level dependencies like Google Chrome and ChromeDriver. Docker packages everything, including the browser itself, to ensure the framework runs consistently in any environment.

---

## ADR 5: Choose Demo Web Shop as target website

### Context & Requirements
We need a free, public, stable website designed for web automation practice.

### Decision
Use **Tricentis Demo Web Shop** (https://demowebshop.tricentis.com/).

### Alternatives Considered & Rejected
- **SauceLabs SauceDemo**: SauceDemo is a great, simple site, but it is limited to a single page login and a basic cart workflow. It does not have user registration forms, search bars, or field-level validation errors.
- **E-commerce sites (Amazon, eBay)**: Automating real production websites is discouraged due to dynamic content changes, CAPTCHA blockages, and terms of service restrictions.
