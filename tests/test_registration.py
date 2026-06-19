"""
File: test_registration.py

Purpose:
Contains Pytest test cases for registration workflows on Demo Web Shop.
Validates successful registration with unique generated credentials,
duplicate registration prevention, and field-level validation errors.

Author: <Your Name>

Created: 2026-06-19
"""

import logging
from datetime import datetime

from pages.registration_page import RegistrationPage

# Initialize logger
logger = logging.getLogger(__name__)


def test_registration_successful(driver):
    """
    Verifies that a user can register successfully with unique credentials.
    Generates a timestamped email address to guarantee fresh test run state.
    """
    logger.info("Starting test scenario: Successful Registration")

    # Generate unique timestamp email to prevent existing user errors
    unique_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_email = f"pytest_user_{unique_timestamp}@test.com"

    register_page = RegistrationPage(driver)
    register_page.navigate()
    register_page.register_user(
        gender="Female",
        first_name="Jane",
        last_name="Doe",
        email=unique_email,
        password="Pass123!",
        confirm_password="Pass123!",
    )

    # Validate that registration succeeded
    success_text = register_page.get_success_message()
    assert (
        "Your registration completed" in success_text
    ), f"Expected registration confirmation message, but found: '{success_text}'"
    logger.info(f"Successfully verified registration for email: '{unique_email}'")


def test_registration_existing_user(driver):
    """
    Verifies that registration fails when using an email that is already registered.
    Uses the static test account email.
    """
    logger.info("Starting test scenario: Registration with Existing User Email")

    existing_email = "tester_antigravity@test.com"

    # We navigate to register page and submit the duplicate details
    register_page = RegistrationPage(driver)
    register_page.navigate()
    register_page.register_user(
        gender="Male",
        first_name="Automation",
        last_name="Tester",
        email=existing_email,
        password="Pass123!",
        confirm_password="Pass123!",
    )

    # Validate duplicate warning error
    summary_error = register_page.get_validation_summary_error()
    assert (
        "The specified email already exists" in summary_error
    ), f"Expected duplicate email warning, but found: '{summary_error}'"
    logger.info("Successfully validated that duplicate user registration is prevented.")


def test_registration_invalid_email(driver):
    """
    Verifies that registering with an invalid email format triggers field validation.
    """
    logger.info("Starting test scenario: Registration with Invalid Email Format")

    invalid_email = "invalid_user_format"

    register_page = RegistrationPage(driver)
    register_page.navigate()
    register_page.register_user(
        gender="Male",
        first_name="Invalid",
        last_name="User",
        email=invalid_email,
        password="Pass123!",
        confirm_password="Pass123!",
    )

    # Validate field format error
    field_error = register_page.get_field_validation_error()
    assert (
        "Wrong email" in field_error or "Please enter a valid email address" in field_error
    ), f"Expected email format validation error, but found: '{field_error}'"
    logger.info("Successfully validated email format validation during registration.")
