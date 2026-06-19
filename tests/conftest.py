"""
File: conftest.py

Purpose:
Serves as the Pytest bootstrapping file. Defines custom command line switches,
manages WebDriver lifecycle (supporting headed/headless Chrome and Firefox),
configures automatic test retries, captures comprehensive failure diagnostics
(URL, browser details, resolution, stack trace), and embeds failure screenshots
directly into pytest-html reports.

Author: <Your Name>

Created: 2026-06-19
"""

import base64
import logging
import os
from datetime import datetime

import pytest
from pytest_html import extras
from selenium import webdriver

from utils.config_loader import ConfigLoader
from utils.screenshot_manager import ScreenshotManager

# Initialize session-level logger
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """
    Registers custom command-line flags for Pytest execution.
    """
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Specify target browser (chrome or firefox)",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Specify headless execution",
    )
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Specify target test environment (development, qa, production)",
    )


def pytest_configure(config):
    """
    Performs early framework configurations before any test runs:
    1. Sets environment variable overrides from CLI flags.
    2. Bootstraps unified logging (File and Console handlers).
    3. Configures pytest-html reports meta-properties.
    4. Sets up automated retries based on config.json.
    """
    # 1. Resolve environment override from CLI flag
    env_opt = config.getoption("--env")
    if env_opt:
        os.environ["TEST_ENV"] = env_opt

    # Load configuration settings
    loader = ConfigLoader()

    # 2. Configure Logger
    log_file = loader.log_file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    logger.info("--------------------------------------------------")
    logger.info("Initializing Test Automation Execution...")
    logger.info(f"Target Environment: {loader.environment.upper()}")
    logger.info(f"Base Application URL: {loader.base_url}")
    logger.info("--------------------------------------------------")

    # 3. Configure Pytest HTML Report Meta-data
    if hasattr(config, "_metadata"):
        config._metadata["Project Name"] = "Demo Web Shop Automation Suite"
        config._metadata["Target Environment"] = loader.environment.upper()
        config._metadata["Base URL"] = loader.base_url
        config._metadata["Author"] = "QA Automation Architect Candidate"

        # Remove standard pytest metadata headers to clean up report
        config._metadata.pop("Packages", None)
        config._metadata.pop("Plugins", None)
        config._metadata.pop("Platform", None)

    # 4. Configure Test Retries Dynamically
    if hasattr(config.option, "reruns"):
        config.option.reruns = loader.retry_count
        logger.info(f"Pytest rerun failures configured to retry {loader.retry_count} time(s).")


def pytest_html_report_title(report):
    """Sets the title of the HTML Report."""
    report.title = "QA Automation Execution Report - Demo Web Shop"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hooks into Pytest test execution phase. On failure:
    1. Gathers deep failure diagnostics (URL, Resolution, Exception, Stack Trace).
    2. Invokes ScreenshotManager to capture the failure state.
    3. Embeds the screenshot and diagnostics directly into the HTML report.
    """
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    # Capture failure diagnostics during test call execution phase
    if report.when == "call" and report.failed:
        # Retrieve the driver instance from the test session item
        driver = item.funcargs.get("driver") or getattr(item, "_driver", None)

        if driver:
            try:
                # 1. Gather browser details
                current_url = driver.current_url
                browser_name = driver.capabilities.get("browserName", "Unknown")
                browser_version = driver.capabilities.get("browserVersion", "Unknown")
                window_size = driver.get_window_size()
                resolution = f"{window_size.get('width', 0)}x{window_size.get('height', 0)}"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 2. Extract error message and traceback details
                exception_msg = (
                    str(call.excinfo.value) if call.excinfo else "No exception recorded."
                )
                stack_trace = (
                    str(call.excinfo.traceback) if call.excinfo else "No traceback available."
                )

                # 3. Capture failure screenshot
                screenshot_manager = ScreenshotManager()
                # Attempt to extract a target element from test failures to highlight
                # (For simplicity, we check if the test function stored an element)
                failed_element = getattr(item, "_failed_element", None)
                screenshot_path = screenshot_manager.capture_failure_screenshot(
                    driver=driver, test_name=item.name, failed_element=failed_element
                )

                # 4. Format screenshot into HTML report
                screenshot_html = ""
                if screenshot_path and os.path.exists(screenshot_path):
                    with open(screenshot_path, "rb") as image_file:
                        encoded_base64 = base64.b64encode(image_file.read()).decode("utf-8")
                    screenshot_html = (
                        '<div style="margin-top: 15px;">'
                        '  <strong style="color: #cc0000; display: block; '
                        'margin-bottom: 5px;">'
                        "Failure Screenshot Preview (Click to view "
                        "full-size):</strong>"
                        f'  <a href="data:image/png;base64,{encoded_base64}" '
                        'target="_blank">'
                        '    <img src="data:image/png;base64,'
                        f'{encoded_base64}" alt="Failure Screenshot" '
                        '         style="width: 500px; border: 2px solid '
                        "#cc0000; border-radius: 4px; box-shadow: 0 4px "
                        "6px rgba(0,0,0,0.1); cursor: zoom-in; transition: "
                        'transform 0.2s;" '
                        '         onmouseover="this.style.transform='
                        "'scale(1.02)'\" onmouseout=\"this.style.transform="
                        "'scale(1)'\"/>"
                        "  </a>"
                        "</div>"
                    )

                # 5. Format diagnostics HTML
                diagnostics_html = (
                    '<div class="failure-diagnostics" style="border: 1px '
                    "solid #cc0000; padding: 12px; margin-top: 15px; "
                    "background-color: #fff5f5; border-radius: 6px; "
                    'font-family: sans-serif;">'
                    '  <h4 style="margin: 0 0 10px 0; color: #cc0000; '
                    "border-bottom: 1px solid #cc0000; padding-bottom: 5px; "
                    'font-size: 14px;">Diagnostic Report</h4>'
                    '  <table style="width: 100%; border-collapse: collapse; '
                    "font-family: monospace; font-size: 12px; "
                    'line-height: 1.4;">'
                    '    <tr style="border-bottom: 1px solid #ffebeb;">'
                    '<td style="font-weight: bold; width: 150px; '
                    'padding: 4px 0;">Timestamp:</td>'
                    f'<td style="padding: 4px 0;">{timestamp}</td></tr>'
                    '    <tr style="border-bottom: 1px solid #ffebeb;">'
                    '<td style="font-weight: bold; padding: 4px 0;">'
                    "Target URL:</td>"
                    f'<td style="padding: 4px 0;"><a href="{current_url}" '
                    'target="_blank" style="color: #0066cc;">'
                    f"{current_url}</a></td></tr>"
                    '    <tr style="border-bottom: 1px solid #ffebeb;">'
                    '<td style="font-weight: bold; padding: 4px 0;">'
                    "Browser:</td>"
                    f'<td style="padding: 4px 0;">'
                    f"{browser_name.capitalize()} (v{browser_version})</td></tr>"
                    '    <tr style="border-bottom: 1px solid #ffebeb;">'
                    '<td style="font-weight: bold; padding: 4px 0;">'
                    f'Resolution:</td><td style="padding: 4px 0;">{resolution}</td></tr>'
                    '    <tr style="border-bottom: 1px solid #ffebeb;">'
                    '<td style="font-weight: bold; vertical-align: top; '
                    'padding: 4px 0;">Exception Message:</td>'
                    f'<td style="color: #b30000; font-weight: bold; '
                    f'padding: 4px 0; white-space: pre-wrap;">'
                    f"{exception_msg}</td></tr>"
                    '    <tr><td style="font-weight: bold; '
                    'vertical-align: top; padding: 4px 0;">Stack Trace:</td>'
                    f'<td style="padding: 4px 0;"><pre style="margin: 0; '
                    "white-space: pre-wrap; font-family: monospace; "
                    "font-size: 11px; background: #fafafa; padding: 8px; "
                    "border: 1px solid #eaeaea; border-radius: 4px; "
                    'max-height: 250px; overflow-y: auto;">'
                    f"{stack_trace}</pre></td></tr>"
                    "  </table>"
                    f"  {screenshot_html}"
                    "</div>"
                )

                # Append detailed diagnostics table to the test report
                extra.append(extras.html(diagnostics_html))

            except Exception as report_error:
                logger.error(
                    f"Failed to generate failure diagnostics for HTML report: {str(report_error)}"
                )

    report.extra = extra


# Track test session metrics and outcomes
_test_outcomes = {}
_session_start_time = 0.0


def pytest_sessionstart(session):
    """
    Called before session starts. Tracks start time.
    """
    global _session_start_time
    import time

    _session_start_time = time.time()


def pytest_sessionfinish(session, exitstatus):
    """
    Called after all tests complete.
    Generates reports/execution_summary.md containing test run statistics.
    """
    import time

    from utils.config_loader import ConfigLoader

    duration = time.time() - _session_start_time
    loader = ConfigLoader()

    passed = sum(1 for status in _test_outcomes.values() if status == "passed")
    failed = sum(1 for status in _test_outcomes.values() if status == "failed")
    skipped = sum(1 for status in _test_outcomes.values() if status == "skipped")
    total = len(_test_outcomes)

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format summary markdown text
    summary_markdown = (
        f"# Test Execution Summary\n\n"
        f"**Date:** {timestamp_str}  \n"
        f"**Browser:** {loader.browser.upper()}  \n"
        f"**Environment:** {loader.environment.upper()}  \n"
        f"**Base URL:** {loader.base_url}  \n\n"
        f"## Test Metrics\n"
        f"| Metric | Count |\n"
        f"| :--- | :--- |\n"
        f"| **Total Tests** | {total} |\n"
        f"| <span style='color:green;'>**Passed**</span> | {passed} |\n"
        f"| <span style='color:red;'>**Failed**</span> | {failed} |\n"
        f"| <span style='color:orange;'>**Skipped**</span> | {skipped} |\n"
        f"| **Duration** | {duration:.2f} seconds |\n"
    )

    # Write summary to target reports directory
    summary_path = loader.reports_dir / "execution_summary.md"
    try:
        with open(summary_path, "w", encoding="utf-8") as summary_file:
            summary_file.write(summary_markdown)
        logger.info(f"Execution summary markdown report written to: {summary_path}")
    except Exception as error:
        logger.error(f"Failed to generate execution summary markdown: {str(error)}")


def pytest_runtest_logreport(report):
    """
    Intercepts test reports to log rerun occurrences and record test outcomes.
    """
    if report.outcome == "rerun":
        logger.warning(
            f"Test execution '{report.nodeid}' FAILED. Initializing automatic test retry... "
            f"(Retry execution attempt {getattr(report, 'rerun', 0)})"
        )
        _test_outcomes[report.nodeid] = "rerun"
    elif (
        report.when == "call"
        or (report.when == "setup" and report.failed)
        or (report.when == "setup" and report.skipped)
    ):
        # We record the test outcome for the call phase or early setup errors
        _test_outcomes[report.nodeid] = report.outcome


@pytest.fixture(scope="function")
def driver(request):
    """
    Pytest fixture to initialize and quit the Selenium WebDriver.
    Checks command line options first, then falls back to central configurations.
    """
    loader = ConfigLoader()

    # 1. Resolve browser setting
    browser_cli = request.config.getoption("--browser")
    browser = browser_cli if browser_cli else loader.browser

    # 2. Resolve headless flag setting
    headless_cli = request.config.getoption("--headless")
    headless = headless_cli or loader.headless

    logger.info(f"Launching WebDriver session. Browser: {browser.upper()}, Headless: {headless}")

    driver_instance = None
    if browser.lower() == "chrome":
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=service, options=chrome_options)

    elif browser.lower() == "firefox":
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        from webdriver_manager.firefox import GeckoDriverManager

        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--window-size=1920,1080")

        service = Service(GeckoDriverManager().install())
        driver_instance = webdriver.Firefox(service=service, options=firefox_options)

    else:
        logger.critical(f"Requested browser type '{browser}' is unsupported.")
        raise ValueError(f"Browser '{browser}' is not supported by the framework.")

    # 3. Configure browser wait states
    driver_instance.implicitly_wait(loader.implicit_wait)
    driver_instance.maximize_window()

    # Attach driver reference to request node for hook retrieval
    request.node._driver = driver_instance

    yield driver_instance

    logger.info("Shutting down WebDriver session.")
    try:
        driver_instance.quit()
    except Exception as teardown_error:
        logger.error(f"Error encountered during browser close: {str(teardown_error)}")
