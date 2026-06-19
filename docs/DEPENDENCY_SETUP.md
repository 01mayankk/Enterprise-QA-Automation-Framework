# Dependency & Environment Setup Guide

This guide details how to recreate the Python 3.10 virtual environment, install dependencies, and configure your IDE to resolve package imports.

---

## 1. Clean Environment Setup

Follow these steps to set up the workspace from scratch:

### Step 1: Create the Virtual Environment
Create a clean virtual environment using Python 3.10.

```bash
# In the project root directory
py -3.10 -m venv venv
```

### Step 2: Activate the Virtual Environment
Activate the environment to bind your shell to the local Python interpreter.

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat

# Linux / macOS Bash
source venv/bin/activate
```

### Step 3: Install Required Packages
Install dependencies from `requirements.txt`.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. IDE Integration (VS Code / Pyrefly / Pyright)

To fix import resolution errors, you must tell your IDE to use the virtual environment's interpreter.

1. **Workspace Settings**: Ensure the [.vscode/settings.json](file:///c:/Projects/QA-testing/.vscode/settings.json) exists and contains the correct Python interpreter path:
   ```json
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
     "python.analysis.extraPaths": [
       "${workspaceFolder}"
     ]
   }
   ```
2. **Select Interpreter**: In VS Code, open the Command Palette (`Ctrl+Shift+P`), type **Python: Select Interpreter**, and select the interpreter located at `.\venv\Scripts\python.exe`.

---

## 3. Verification Commands

Run these commands to verify that your environment is configured correctly:

### 3.1 Import & Dependency Verification
Run pytest to verify that all imports resolve successfully:
```bash
# Set PYTHONPATH and execute pytest
$env:PYTHONPATH="c:\Projects\QA-testing"; venv\Scripts\pytest --version
```

### 3.2 Linter and Quality Verification
Check code formatting and style guidelines:
```bash
# Check code style with flake8
venv\Scripts\flake8 pages/ tests/ utils/
```

### 3.3 Running Headless Regression Tests
Verify browser execution:
```bash
$env:PYTHONPATH="c:\Projects\QA-testing"; venv\Scripts\pytest -v --headless
```

---

## 4. Troubleshooting Guidelines

### 4.1 ChromeDriver Connection Timed Out
- **Issue**: Chrome or chromedriver hangs in the background.
- **Solution**: Terminate orphaned processes using:
  ```powershell
  taskkill /f /im chrome.exe
  taskkill /f /im chromedriver.exe
  ```

### 4.2 ModuleNotFoundError: No module named 'pages' or 'utils'
- **Issue**: Python cannot locate the root project folders.
- **Solution**: Set the `PYTHONPATH` environment variable to the absolute path of the project root:
  ```powershell
  $env:PYTHONPATH="c:\Projects\QA-testing"
  ```
