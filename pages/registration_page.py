"""
File: registration_page.py

Purpose:
Contains the RegistrationPage page object representing the Demo Web Shop Registration page.
Defines locators for gender options, name inputs, credentials, registration submission,
and retrieval of success messages or error validation alerts.

Author: <Your Name>

Created: 2026-06-19
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage

# Setup logger
logger = logging.getLogger(__name__)


class RegistrationPage(BasePage):
    """
    RegistrationPage Object containing locators, navigation mechanisms, actions,
    and visual validation elements.
    """

    # Gender locators
    GENDER_MALE_RADIO = (By.ID, "gender-male")
    GENDER_FEMALE_RADIO = (By.ID, "gender-female")

    # Name input locators
    FIRST_NAME_INPUT = (By.ID, "FirstName")
    LAST_NAME_INPUT = (By.ID, "LastName")

    # Email and Password locators
    EMAIL_INPUT = (By.ID, "Email")
    PASSWORD_INPUT = (By.ID, "Password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "ConfirmPassword")

    # Submission locator
    REGISTER_BUTTON = (By.ID, "register-button")

    # Success and error message locators
    REGISTRATION_RESULT = (By.CLASS_NAME, "result")
    VALIDATION_SUMMARY_ERROR = (By.CSS_SELECTOR, ".validation-summary-errors")
    FIELD_VALIDATION_ERROR = (By.CSS_SELECTOR, ".field-validation-error")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.register_url = f"{self.config.base_url}register"

    def navigate(self) -> None:
        """Navigates directly to the registration page."""
        logger.info("Navigating to registration page.")
        self.navigate_to(self.register_url)

    def register_user(
        self,
        gender: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> None:
        """
        Fills out the registration form with credentials and clicks Register.
        """
        logger.info(f"Attempting registration for user email: '{email}'")

        # Select Gender radio button
        if gender.lower() == "male":
            self.click_element(self.GENDER_MALE_RADIO)
        elif gender.lower() == "female":
            self.click_element(self.GENDER_FEMALE_RADIO)

        # Enter Personal Details
        if first_name is not None:
            self.enter_text(self.FIRST_NAME_INPUT, first_name)
        if last_name is not None:
            self.enter_text(self.LAST_NAME_INPUT, last_name)

        # Enter Account Credentials
        if email is not None:
            self.enter_text(self.EMAIL_INPUT, email)
        if password is not None:
            self.enter_text(self.PASSWORD_INPUT, password)
        if confirm_password is not None:
            self.enter_text(self.CONFIRM_PASSWORD_INPUT, confirm_password)

        # Click registration submit button
        self.click_element(self.REGISTER_BUTTON)

    def get_success_message(self) -> str:
        """
        Retrieves the registration success message if registration completes.
        """
        logger.info("Checking for registration success message.")
        if self.is_element_displayed(self.REGISTRATION_RESULT):
            return self.get_element_text(self.REGISTRATION_RESULT)
        return ""

    def get_validation_summary_error(self) -> str:
        """
        Retrieves registration summary error message (e.g. 'The specified email already exists').
        """
        logger.info("Checking for registration validation summary errors.")
        if self.is_element_displayed(self.VALIDATION_SUMMARY_ERROR):
            return self.get_element_text(self.VALIDATION_SUMMARY_ERROR)
        return ""

    def get_field_validation_error(self) -> str:
        """
        Retrieves field validation error messages (e.g. 'Email is required.' or 'Wrong email').
        """
        logger.info("Checking for registration field-level errors.")
        if self.is_element_displayed(self.FIELD_VALIDATION_ERROR):
            return self.get_element_text(self.FIELD_VALIDATION_ERROR)
        return ""
