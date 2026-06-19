# Repository Release Audit

This document classifies framework files into Source, Generated, and Temporary categories. It ensures that only the required source assets are tracked in Git, keeping execution outputs isolated.

---

## 1. Classification Index

### 1.1 Source Files (MUST be committed)
These directories and files contain core configurations, test cases, and application code:
- **`config/`**: Target application settings (`config.json`).
- **`data/`**: Parameterized CSV files (`login_test_data.csv`).
- **`docs/`**: Framework documentation and tutorials.
- **`pages/`**: Page Object Model (POM) layer files.
- **`tests/`**: Pytest test scripts (`test_*.py`) and configs (`conftest.py`).
- **`utils/`**: Core utilities (ConfigLoader, ScreenshotManager, EmailSender).
- **`.github/workflows/`**: GitHub Actions runner workflows (`main.yml`).
- **Configuration Files**:
  - `requirements.txt` — PIP package manifest.
  - `Makefile` — Execution script shortcuts.
  - `pyproject.toml` — Black & Isort code formatting setup.
  - `.flake8` — Linting rules.
  - `project_status.md` — Append-only developmental journal.
  - `README.md` — Portfolio overview.
  - `Dockerfile` & `docker-compose.yml` — Container configurations.

---

### 1.2 Generated Files (MUST NOT be committed)
These are files synthesized locally or inside containers during test runs:
- **`reports/`**: Pytest HTML test reports and summary files.
- **`screenshots/`**: PNG captures of test failures.
- **`logs/`**: Detailed runtime browser logs (`automation.log`).
- **Python Cache Directories**:
  - `__pycache__/`
  - `.pytest_cache/`
- **Virtual Environments**:
  - `venv/`
  - `.venv/`

---

### 1.3 Temporary Files (MUST NOT be committed)
These are transient scratch files:
- `*.tmp` / `*.temp` — Temporary storage.
- `*.log` — Local logging outputs.
- `*.cache` — Cache blocks.
- `venv/` / `.venv/` — Python execution environments.

---

## 2. Directory Validation Status

To ensure compliance with the above classification:
- **`.gitignore`**: Maintained and updated to ignore all patterns listed in *Generated Files* and *Temporary Files*.
- **`.dockerignore`**: Configured to prevent generated logs or local virtual environments from copy-building into the runner image.
