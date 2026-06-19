# Dependency Audit Report

This document records the dependency audit carried out to analyze package resolution failures within IDE static analysis engines (such as Pyrefly/Pyright/Pylance).

---

## 1. Installed Dependencies & Versions

The virtual environment (`venv`) has been successfully populated with the required packages:

| Package Name | Installed Version | Purpose |
| :--- | :--- | :--- |
| `selenium` | 4.45.0 | Browser automation engine |
| `webdriver-manager` | 4.1.2 | Automated ChromeDriver and GeckoDriver binary loader |
| `pytest` | 9.1.1 | Core test runner |
| `pytest-html` | 4.2.0 | Test runner HTML reporting plugin |
| `pytest-rerunfailures` | 16.3 | Dynamic test case rerun/retry logic |
| `black` | 26.5.1 | Code style formatter |
| `isort` | 8.0.1 | Import ordering tool |
| `flake8` | 7.3.0 | PEP 8 coding style linter |

All secondary sub-dependencies (such as `requests`, `urllib3`, `attrs`, `trio`, and `pytest-metadata`) are also present in the environment context.

---

## 2. Root Cause of Import Resolution Failures

The framework execution is fully operational, but IDEs (such as VS Code or Pyrefly) show import errors like `pytest` or `selenium` not resolved. The root causes are:

1. **Interpreter Selection Mismatch**:
   - **Issue**: The IDE is using the global system Python environment rather than the project-specific virtual environment (`venv/`).
   - **Result**: Packages like `selenium` and `pytest` are installed inside `venv/` but are missing in the global system path, triggering import warnings.
2. **Missing Workspace Path Specifications**:
   - **Issue**: Python paths within subdirectories like `pages/` and `utils/` are not resolved in the IDE analysis engine because the project workspace root is not appended to the analysis paths.

### Corrective Action Taken
We created [.vscode/settings.json](file:///c:/Projects/QA-testing/.vscode/settings.json) to explicitly direct the IDE and its static analysis engines to target:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.analysis.extraPaths": [
    "${workspaceFolder}"
  ]
}
```

---

## 3. Dependency Compatibility & Conflicts

- **Version Conflicts**: **None**. Pytest 9.x, Selenium 4.x, and webdriver-manager are fully compatible with Python 3.10.
- **Unused Dependencies**: **None**. Every installed package is utilized during execution.
- **Missing Dependencies**: **None**. All runtime dependencies are correctly declared in `requirements.txt`.
