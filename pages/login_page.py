"""
File: login_page.py

Purpose:
Contains the LoginPage page object representing the Demo Web Shop Login page.
Exposes locators for the credentials fields, login execution action, and
validations for checking successful login or capturing error details.

Author: <Your Name>

Created: 2026-06-19
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage

# Logger configuration
logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    LoginPage Object containing locators, navigation mechanisms, actions,
    and visual validation elements.
    """

    # Locators
    EMAIL_INPUT_FIELD = (By.ID, "Email")
    PASSWORD_INPUT_FIELD = (By.ID, "Password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input.login-button")
    LOGOUT_LINK = (By.LINK_TEXT, "Log out")
    LOGIN_LINK = (By.LINK_TEXT, "Log in")

    # Error message containers
    VALIDATION_SUMMARY_ERROR = (By.CSS_SELECTOR, ".validation-summary-errors")
    FIELD_VALIDATION_ERROR = (By.CSS_SELECTOR, ".field-validation-error")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.login_url = f"{self.config.base_url}login"

    def navigate(self) -> None:
        """Navigates directly to the login page."""
        logger.info("Navigating to login page.")
        self.navigate_to(self.login_url)

    def login_with_credentials(self, email: str, password: str) -> None:
        """
        Inputs email and password, then submits the login form.
        Supports testing empty inputs by checking string lengths.
        """
        logger.info(f"Attempting login for email: '{email}'")

        # Enter email only if a string is provided
        if email:
            self.enter_text(self.EMAIL_INPUT_FIELD, email)
        else:
            # Explicitly clear field to simulate empty input
            self.find_visible_element(self.EMAIL_INPUT_FIELD).clear()

        # Enter password only if a string is provided
        if password:
            self.enter_text(self.PASSWORD_INPUT_FIELD, password)
        else:
            # Explicitly clear field to simulate empty input
            self.find_visible_element(self.PASSWORD_INPUT_FIELD).clear()

        # Execute login form submission
        self.click_element(self.LOGIN_BUTTON)

    def is_login_successful(self) -> bool:
        """
        Validates login success by checking if the 'Log out' link is displayed.
        """
        logger.info("Validating login success via presence of Logout link.")
        return self.is_element_displayed(self.LOGOUT_LINK)

    def get_validation_summary_error(self) -> str:
        """
        Retrieves the main block error message (e.g., incorrect credentials).
        """
        logger.info("Checking for validation summary error messages.")
        if self.is_element_displayed(self.VALIDATION_SUMMARY_ERROR):
            return self.get_element_text(self.VALIDATION_SUMMARY_ERROR)
        return ""

    def get_field_validation_error(self) -> str:
        """
        Retrieves specific field errors (e.g., 'Please enter a valid email address').
        """
        logger.info("Checking for field validation error messages.")
        if self.is_element_displayed(self.FIELD_VALIDATION_ERROR):
            return self.get_element_text(self.FIELD_VALIDATION_ERROR)
        return ""
