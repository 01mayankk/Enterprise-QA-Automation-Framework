# Student Learning & Mentorship Guide

This guide is designed for Computer Science students and junior engineers. It explains how the framework works under the hood so you can discuss it confidently during technical interviews.

---

## 1. Project Execution Flow

### 1.1 Where does execution start?
When you run `pytest` (or `make test`), Pytest scans your project directory for test configuration files and test scripts.
1. It locates `tests/conftest.py` to load fixtures, command-line arguments, and reporting hooks.
2. It looks for files prefixed with `test_` (e.g. `test_login.py`).
3. Inside those files, it runs functions prefixed with `test_` (e.g. `test_login_scenarios`).

### 1.2 How Pytest fixtures work (`conftest.py`)
In Pytest, a **fixture** is a function that runs before (setup) and after (teardown) your tests.
- **The `driver` fixture**:
  - **Setup**: Pytest calls `driver()` before a test starts. It reads your browser configuration, launches the browser (Chrome or Firefox), and opens a new session.
  - **Teardown**: The fixture uses Python's `yield` statement. Once the test completes, execution resumes *after* the `yield` statement, calling `driver.quit()` to close the browser.

---

## 2. Reporting & Screenshot Generation

### 2.1 How screenshots are captured on failure
1. Pytest has a hook called `pytest_runtest_makereport`. This function runs after every step of a test (setup, execution call, teardown).
2. If a test fails during the execution call phase (`report.failed` is `True`), the hook retrieves the browser instance.
3. The hook calls `ScreenshotManager.capture_failure_screenshot()`, which:
   - Locates the element that caused the failure.
   - Outlines it with a red border using JavaScript.
   - Captures the screen to a `.png` file.
4. The hook reads the `.png` file, converts it to a Base64 string, and embeds it directly into the HTML report alongside details like the URL, resolution, and stack trace.

---

## 3. Data-Driven Testing (DDT) Explained

### 3.1 What is DDT?
Data-Driven Testing is a design pattern where test inputs are separated from test scripts. This allows you to run the same test scenario multiple times with different inputs (e.g. testing login with valid, invalid, and blank inputs).

### 3.2 How it is implemented here
1. Test data is stored in `data/login_test_data.csv`.
2. `test_login.py` defines a helper function `load_login_test_data()` that parses this CSV file into a list of tuples.
3. We use Pytest's `@pytest.mark.parametrize` decorator to map these tuples to our test parameters:
   ```python
   @pytest.mark.parametrize("username,password,expected_result", load_login_test_data())
   def test_login_scenarios(driver, username, password, expected_result):
       ...
   ```
4. Pytest runs the `test_login_scenarios` function 5 times, once for each row in the CSV file, displaying them as separate test runs in the final report.

---

## 4. Containerization with Docker

### 4.1 What does Docker do?
Docker packages your application and its dependencies (Python, Selenium, Google Chrome, Chromedriver) into a single container. This ensures the tests run exactly the same way on any machine (Windows, macOS, Linux, or CI/CD servers) without needing to install these tools locally.

### 4.2 How Docker Compose manages reports
Inside [docker-compose.yml](file:///c:/Projects/QA-testing/docker-compose.yml), we define **volumes**:
```yaml
volumes:
  - ./reports:/usr/src/app/reports
  - ./screenshots:/usr/src/app/screenshots
  - ./logs:/usr/src/app/logs
```
This mounts folders on your host machine to folders inside the Docker container. When the container writes logs, screenshots, or HTML reports, they are saved directly to your local computer, making them easy to access and view.
