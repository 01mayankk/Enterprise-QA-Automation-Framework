# System Architecture Guide

This document describes the structural layout, layered design, and communication patterns of the QA Automation Framework.

---

## 1. System Components Overview

The framework is architected using a decoupled, multi-layered approach to ensure maximum maintainability, ease of understanding, and scalability. This design follows the classic **Page Object Model (POM)** pattern.

```mermaid
graph TD
    subgraph Vercel [Vercel Hosting Cloud]
        Dashboard["React Dashboard (SPA)"]
        Cache["LocalStorage Cache"]
        Dashboard <-->|Read/Write Cache| Cache
    end

    subgraph GitHub [GitHub Infrastructure]
        GHAPI["GitHub REST API"]
        GHActions["GitHub Actions Runner"]
        Artifacts["GitHub Run Artifacts (ZIP)"]
    end

    subgraph Runner [Runner Execution Sandbox]
        TestCases["Test Suites (pytest)"]
        POM["Page Objects (POM)"]
        Config["Config Layer (JSON)"]
        Selenium["Selenium WebDriver"]
        DemoShop["Demo Web Shop (AUT)"]
        
        TestCases --> POM
        POM --> Selenium
        TestCases --> Config
        Selenium -->|Interacts| DemoShop
    end

    %% Communication Flow
    Dashboard -->|1. Workflow Dispatch (Inputs)| GHAPI
    GHAPI -->|2. Triggers Execution| GHActions
    GHActions -->|3. Runs Python tests| Runner
    Runner -->|4. Generates & Uploads| Artifacts
    Dashboard -->|5. Fetches Run List & Status| GHAPI
    Dashboard -->|6. Downloads & Extracts <= 20MB| Artifacts
```

---

## 2. Layered Responsibilities

### 2.1 Core Configuration & Data Layer
- **`config/config.json`**: Holds environment mappings (development, qa, production), default browser selectors, waits, retry settings, and reports paths.
- **`utils/config_loader.py`**: A Singleton parser class that safely reads the configuration file, processes environment overrides, and yields Python-typed properties.
- **`data/login_test_data.csv`**: Holds externalized test input records to drive parametrized, multi-scenario tests.

### 2.2 Page Object Model (POM) Layer
- **`pages/base_page.py`**: Encapsulates raw Selenium operations (finding elements, executing clicks, inserting keys, checking displays) inside explicit wait wrappers. It logs all interactive events and handles standard browser exceptions.
- **Concrete Pages (`login_page.py`, `registration_page.py`, `search_page.py`)**: Subclasses of `BasePage` that store locators (and locators *only*) and page-specific user flows. They **never** contain test assertions.

### 2.3 Execution & Pytest Layer
- **`tests/conftest.py`**: Bootstraps the framework. Handles CLI args (`--browser`, `--headless`, `--env`), initializes local/containerized browser drivers, sets up standard test logging, manages retry options, and configures reporting hooks.
- **`tests/test_*.py`**: Houses individual tests. Imports page objects, sets up test actions, and carries out final test assertions. Locators are never defined in this layer.

### 2.4 Reporting, Logging & Diagnostic Layer
- **`utils/screenshot_manager.py`**: Handles screen capture on failure, highlights the error target elements on-screen, and saves timestamped screenshots.
- **`logs/automation.log`**: A unified file documenting framework setup, test steps, assertions, and stack traces.
- **`reports/report.html`**: An interactive, self-contained HTML report containing execution metrics, logs, and failure details.
- **`reports/execution_summary.md`**: Generated automatically at the end of each session, summarizing pass/fail outcomes.

---

## 3. Decoupling & Clean Architecture Principles

1. **Separation of Concerns**: Test scripts only deal with execution steps and assertions; Page Objects only deal with locator queries and page actions. If a UI element changes, only the corresponding Page Object class needs modification.
2. **Centralized Configurations**: Base URLs, wait times, and folders are never hardcoded. They are read dynamically.
3. **Robust Exception Safety**: WebDriver queries are wrapped inside explicit WebDriverWait constraints. This prevents test flakiness and logs exact element interaction states when elements fail to appear.
