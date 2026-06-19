"""
File: base_page.py

Purpose:
Acts as the parent Page Object. Encapsulates common Selenium WebDriver actions
(clicking, typing, waiting for visibility, checking page titles) with robust
error handling, explicit wait patterns, and structural step logging.

Author: <Your Name>

Created: 2026-06-19
"""

import logging
from typing import List

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config_loader import ConfigLoader

# Setup structured logger
logger = logging.getLogger(__name__)


class BasePage:
    """
    Base page model class encapsulating core Selenium operations.
    All Page Objects inherit from this class.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.config = ConfigLoader()
        self.wait = WebDriverWait(self.driver, self.config.explicit_wait)

    def navigate_to(self, url: str) -> None:
        """Navigates the browser to the specified URL."""
        try:
            logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)
        except WebDriverException as error:
            logger.error(f"Navigation failed to {url}: {str(error)}")
            raise

    def find_element(self, locator: tuple) -> WebElement:
        """
        Locates a single element matching the provided locator tuple (By.TYPE, 'selector').
        Applies explicit wait for presence before returning.
        """
        try:
            logger.debug(f"Locating element with locator: {locator}")
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException as error:
            logger.error(f"Timeout waiting for element presence with locator: {locator}")
            raise TimeoutException(
                f"Element matching {locator} was not found on the page within timeout."
            ) from error

    def find_visible_element(self, locator: tuple) -> WebElement:
        """
        Locates a single element and verifies it is visible on the DOM.
        """
        try:
            logger.debug(f"Waiting for visibility of element: {locator}")
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException as error:
            logger.error(f"Timeout waiting for element visibility with locator: {locator}")
            raise TimeoutException(
                f"Element matching {locator} was not visible on the page within timeout."
            ) from error

    def find_elements(self, locator: tuple) -> List[WebElement]:
        """
        Locates multiple elements matching the locator tuple.
        """
        try:
            logger.debug(f"Locating elements with locator: {locator}")
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            logger.warning(f"No elements found matching locator: {locator}")
            return []

    def click_element(self, locator: tuple) -> None:
        """
        Waits for an element to be clickable and performs a click operation.
        """
        try:
            logger.info(f"Clicking element: {locator}")
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except (TimeoutException, WebDriverException) as error:
            logger.error(f"Failed to click element: {locator}. Error: {str(error)}")
            raise

    def enter_text(self, locator: tuple, text: str, clear_first: bool = True) -> None:
        """
        Enters text into an input field after locating it.
        Optionally clears existing text beforehand.
        """
        try:
            logger.info(f"Entering text into field: {locator}")
            element = self.find_visible_element(locator)
            if clear_first:
                element.clear()
            element.send_keys(text)
        except (TimeoutException, WebDriverException) as error:
            logger.error(f"Failed to enter text into field: {locator}. Error: {str(error)}")
            raise

    def get_element_text(self, locator: tuple) -> str:
        """
        Retrieves text content of the visible element.
        """
        try:
            text = self.find_visible_element(locator).text
            logger.info(f"Retrieved text for {locator}: '{text}'")
            return text
        except (TimeoutException, NoSuchElementException) as error:
            logger.error(f"Failed to retrieve text from element: {locator}. Error: {str(error)}")
            raise

    def is_element_displayed(self, locator: tuple) -> bool:
        """
        Checks if an element is visible on the page. Does not throw an exception on failure,
        returns False instead.
        """
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element.is_displayed()
        except TimeoutException:
            logger.debug(f"Element {locator} was not visible within wait period; returning False.")
            return False

    def get_page_title(self) -> str:
        """Gets current page title."""
        title = self.driver.title
        logger.info(f"Retrieved page title: '{title}'")
        return title
