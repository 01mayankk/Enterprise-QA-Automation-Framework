"""
File: screenshot_manager.py

Purpose:
Provides automated screenshot capture capabilities. Generates standardized, timestamped
filenames containing test details, stores screenshots in the screenshots directory,
and implements visual element highlighting to assist in debugging test failures.

Author: <Your Name>

Created: 2026-06-19
"""

import logging
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from utils.config_loader import ConfigLoader

# Initialize logger
logger = logging.getLogger(__name__)


class ScreenshotManager:
    """
    Manages capturing, naming, storing, and embedding failure screenshots.
    """

    def __init__(self):
        self.config = ConfigLoader()
        self.screenshots_dir = self.config.screenshots_dir

    def highlight_element(self, driver: WebDriver, element: WebElement) -> None:
        """
        Applies a red border around the target WebElement using JavaScript execution.
        This provides a clear visual indicator of the failed element in screenshots.
        """
        try:
            driver.execute_script("arguments[0].style.border='3px solid red';", element)
            logger.info("Successfully highlighted target element with red border.")
        except Exception as error:
            logger.warning(f"Could not highlight element due to exception: {str(error)}")

    def capture_failure_screenshot(
        self,
        driver: WebDriver,
        test_name: str,
        failed_element: WebElement = None,
    ) -> str:
        """
        Captures a screenshot of the current browser state.
        Saves the screenshot in a structured filename format:
        screenshots/test_[test_name]_[browser]_[env]_[timestamp].png

        Args:
            driver: The Selenium WebDriver instance.
            test_name: Name of the executed test case.
            failed_element: Optional element to highlight before capturing.

        Returns:
            The absolute file path of the captured screenshot, or empty string on failure.
        """
        if not driver:
            logger.error("WebDriver instance is null; cannot capture screenshot.")
            return ""

        try:
            # Highlight target element if provided
            if failed_element:
                self.highlight_element(driver, failed_element)

            # Generate clean timestamp and filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            browser_name = self.config.browser
            environment_name = self.config.environment

            # Construct clean name: remove invalid characters if any
            clean_test_name = test_name.replace("[", "").replace("]", "")
            filename = f"{clean_test_name}_{browser_name}_{environment_name}_{timestamp}.png"
            file_path = self.screenshots_dir / filename

            # Capture screenshot via webdriver
            driver.save_screenshot(str(file_path))
            logger.info(f"Failure screenshot captured successfully: {file_path}")

            return str(file_path)

        except Exception as error:
            logger.error(f"Failed to capture failure screenshot for {test_name}: {str(error)}")
            return ""
