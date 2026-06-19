# Git Commit & Release Plan

This document details the recommended commit sequence for initializing and pushing the framework to the target remote repository:
`https://github.com/01mayankk/Enterprise-QA-Automation-Framework.git`

---

## 1. Commit Sequence Layout

We avoid squashing the entire codebase into a single initial commit. This shows a realistic development lifecycle for recruiters.

### Commit 1: Initial Project Structure
- **Commit Message**: `chore: initialize project structure and base dependencies`
- **Scope**:
  - Root directory READMEs
  - `requirements.txt`
  - `Makefile`
  - `config/config.json`
  - `utils/config_loader.py`
  - `.gitignore`

---

### Commit 2: Page Object Model Layer
- **Commit Message**: `feat: implement Page Object Model base and page classes`
- **Scope**:
  - `pages/base_page.py`
  - `pages/login_page.py`
  - `pages/registration_page.py`
  - `pages/search_page.py`

---

### Commit 3: Automation Test Suite & Data
- **Commit Message**: `feat: implement login, registration, and search test suites`
- **Scope**:
  - `data/login_test_data.csv`
  - `tests/test_login.py`
  - `tests/test_registration.py`
  - `tests/test_search.py`

---

### Commit 4: Reporting and Failure Diagnostics
- **Commit Message**: `feat: implement diagnostic reporting, screenshot manager, and session hooks`
- **Scope**:
  - `tests/conftest.py` (WebDriver fixtures and pytest HTML report hooks)
  - `utils/screenshot_manager.py` (highlight border element and PNG storage)
  - `pyproject.toml` & `.flake8` (linting standards configs)

---

### Commit 5: Containerization & CI/CD
- **Commit Message**: `ci: configure Docker execution and GitHub Actions pipelines`
- **Scope**:
  - `Dockerfile` & `docker-compose.yml`
  - `.dockerignore`
  - `.github/workflows/main.yml`

---

### Commit 6: Documentation Suite
- **Commit Message**: `docs: author architectural manuals, learning guides, and interview prep`
- **Scope**:
  - Main project `README.md`
  - All documents inside `docs/` (Architecture, ExecutionFlow, DeploymentGuide, LearningGuide, InterviewQuestions, ResumeContent, ADRs, SecurityConsiderations, FrontendGuide)

---

### Commit 7: Dashboard Integration (Release Candidate)
- **Commit Message**: `feat: implement React+Vite web dashboard for GitHub API execution tracking`
- **Scope**:
  - Dashboard frontend sources under `frontend/`
  - Dashboard configuration guides

---

## 2. Remote Repository Initialization Commands
Run these commands locally in sequence to initialize the repository:
```bash
# Initialize local repo
git init

# Set main branch
git branch -M main

# Add target remote
git remote add origin https://github.com/01mayankk/Enterprise-QA-Automation-Framework.git

# Execute Commits (Add and commit group-by-group as described in Section 1)
# Example for Commit 1:
# git add config/ utils/config_loader.py requirements.txt Makefile .gitignore
# git commit -m "chore: initialize project structure and base dependencies"

# Push to GitHub
git push -u origin main
```
