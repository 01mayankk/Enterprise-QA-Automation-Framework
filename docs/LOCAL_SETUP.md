# Local Setup & Execution Guide

This guide provides step-by-step instructions to configure, run, and verify the QA Automation Framework on your local machine, within Docker containers, and using the React dashboard.

---

## 1. Prerequisites

Before starting, ensure you have the following installed:
- **Python**: v3.8 or higher.
- **Node.js & npm**: Node v18+ (required for the frontend dashboard).
- **Google Chrome** or **Mozilla Firefox**: Installed on the host.
- **Docker & Docker Compose**: (Optional) For running containerized tests.

---

## 2. Clone the Repository

Clone the project to your local workspace and navigate to the directory:

```bash
git clone https://github.com/01mayankk/Enterprise-QA-Automation-Framework.git
cd Enterprise-QA-Automation-Framework
```

---

## 3. Backend Python Setup

To configure the test runner, create and activate a Python virtual environment and install the required dependencies:

### 3.1 Environment Activation

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies

Install the core testing dependencies:
```bash
pip install -r requirements.txt
```

---

## 4. Test Execution

You can launch the automated regression test suite using either the Makefile helper commands or the pytest CLI.

### 4.1 CLI Execution Examples

Run the suite in default headless mode (using Chrome against the QA environment):
```bash
pytest
```

Run tests with the browser window visible:
```bash
pytest --headless false
```

Run tests on Firefox (requires Firefox browser installed):
```bash
pytest --browser firefox
```

Target a different environment config profile (e.g. `development` sandbox):
```bash
pytest --env development
```

### 4.2 Report Generation

To compile a self-contained, interactive HTML report summarizing metrics, logs, and base64-embedded failure screenshot grids, execute:
```bash
pytest --html=reports/report.html --self-contained-html
```

---

## 5. Dockerized Execution

Run the headless browser regression suite in isolated containers without installing Python or browsers on your host machine:

```bash
# Build the container image and execute the test suite
docker-compose up --build

# Tear down container boxes and release resources
docker-compose down
```

Test logs (`logs/`), reports (`reports/`), and screenshot captures (`screenshots/`) will automatically synchronize to your host system via mounted volume binds.

---

## 6. Frontend Dashboard Setup

Orchestrate, trigger, and view test suite runs from a modern, glassmorphic client-side React dashboard:

```bash
# Navigate to frontend folder
cd frontend

# Install packages
npm install

# Start Vite local development server
npm run dev
```

Open your browser and navigate to:
```text
http://localhost:5173
```

---

## 7. GitHub Actions Integration

The pipeline script is located in `.github/workflows/main.yml`.

### 7.1 Workflow Dispatch Triggers
The CI pipeline exposes manual triggering via **`workflow_dispatch`** inputs:
- **`environment`**: select deployment profiles (`qa`, `development`, `production`).
- **`browser`**: select automated browser runtimes (`chrome`, `firefox`).
- **`headless`**: select headless toggles (`true`, `false`).
- **`retry_count`**: configure pytest rerun retries (range `0` to `5`).

### 7.2 Run Artifacts & Outputs
Upon execution completion, GitHub Actions compiles and uploads the following:
- **`execution-report`**: A ZIP package containing `report.html` and the markdown execution summary.
- **`failure-screenshots`**: A ZIP package containing target-highlighted `.png` captures (uploaded only when assertions fail).
- **Execution Summary**: An in-line markdown summary visible directly on the GHA run page.
- **Dashboard Synchronization**: The React dashboard parses these artifacts using client-side `jszip` (supporting a 20MB limit) or prompts manual download options, rendering reports and galleries dynamically.
