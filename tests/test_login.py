"""
File: test_login.py

Purpose:
Contains Pytest test cases for login workflows on Demo Web Shop.
Implements Data-Driven Testing (DDT) using a CSV data source to validate
valid login, invalid credentials, incorrect formats, and blank input fields.

Author: <Your Name>

Created: 2026-06-19
"""

import csv
import logging
from pathlib import Path

import pytest

from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage

# Initialize logger
logger = logging.getLogger(__name__)

# Flag to guarantee registration executes only once per test run session
_ddt_user_registered = False


def load_login_test_data():
    """
    Reads credentials and expected outcomes from the login CSV data file.
    """
    csv_path = Path(__file__).parent.parent / "data" / "login_test_data.csv"
    test_cases = []
    try:
        with open(csv_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                test_cases.append(
                    (
                        row["username"],
                        row["password"],
                        row["expected_result"],
                    )
                )
    except FileNotFoundError as error:
        logger.critical(f"DDT login test data file missing at: {csv_path}. Error: {str(error)}")
        raise
    return test_cases


@pytest.fixture(scope="function", autouse=True)
def ensure_ddt_user_is_registered(driver):
    """
    Ensures that the CSV-driven user is registered on the Demo Web Shop application.
    Runs once per module run by checking a execution status flag.
    """
    global _ddt_user_registered
    if not _ddt_user_registered:
        logger.info("DDT Setup: Ensuring test account 'tester_antigravity@test.com' exists.")
        registration = RegistrationPage(driver)
        registration.navigate()
        registration.register_user(
            gender="Male",
            first_name="Automation",
            last_name="Tester",
            email="tester_antigravity@test.com",
            password="Pass123!",
            confirm_password="Pass123!",
        )

        # Log completion; we do not assert success because if the user is already
        # registered, the web portal returns a duplicate email error which is safe to ignore.
        logger.info("DDT Setup: Pre-registration attempt completed successfully.")
        _ddt_user_registered = True


@pytest.mark.parametrize("username,password,expected_result", load_login_test_data())
def test_login_scenarios(driver, username, password, expected_result):
    """
    Executes multiple login validation paths driven by data-driven inputs.
    Verifies success routes and validates error messages for incorrect entries.
    """
    logger.info(
        f"Starting test scenario. User: '{username}', Expected Result Tag: '{expected_result}'"
    )

    login_page = LoginPage(driver)
    login_page.navigate()
    login_page.login_with_credentials(username, password)

    # 1. Assertions for Successful Login scenario
    if expected_result == "success":
        assert (
            login_page.is_login_successful()
        ), f"Login was expected to succeed for '{username}' but failed."
        logger.info(f"Verified successful login for: '{username}'")

        # Perform logout to restore browser state for subsequent tests
        login_page.click_element(LoginPage.LOGOUT_LINK)
        logger.info("Cleaned up session by logging out.")

    # 2. Assertions for Incorrect Password / Incorrect Username scenarios
    elif expected_result == "fail_credentials":
        assert (
            not login_page.is_login_successful()
        ), f"Login succeeded unexpectedly for credentials '{username}' / '{password}'."
        error_message = login_page.get_validation_summary_error()
        assert (
            "Login was unsuccessful" in error_message
            or "The credentials provided are incorrect" in error_message
        ), f"Incorrect credentials error was not displayed. Found instead: '{error_message}'"
        logger.info("Verified failure response for invalid credentials.")

    # 3. Assertions for Invalid Email Format scenarios
    elif expected_result == "fail_email":
        assert (
            not login_page.is_login_successful()
        ), f"Login succeeded unexpectedly for invalid email formatting: '{username}'."
        error_message = login_page.get_field_validation_error()
        assert (
            "Please enter a valid email address" in error_message or "Wrong email" in error_message
        ), f"Email format validation warning was missing. Found instead: '{error_message}'"
        logger.info("Verified failure response for invalid email structure.")

    # 4. Assertions for Empty Email Input scenarios
    elif expected_result == "fail_empty_username":
        assert (
            not login_page.is_login_successful()
        ), "Login succeeded unexpectedly with empty username."
        error_message = login_page.get_validation_summary_error()
        # Demo Web Shop processes empty username as invalid credentials lookup error
        assert (
            "No customer account found" in error_message
            or "Login was unsuccessful" in error_message
        ), (
            "Empty username warning was missing in validation summary. "
            f"Found instead: '{error_message}'"
        )
        logger.info("Verified failure response for blank username.")

    # 5. Assertions for Empty Password Input scenarios
    elif expected_result == "fail_empty_password":
        assert (
            not login_page.is_login_successful()
        ), "Login succeeded unexpectedly with empty password."
        # Demo Web Shop displays a validation summary error for empty passwords
        error_message = login_page.get_validation_summary_error()
        assert (
            "Login was unsuccessful" in error_message
            or "credentials provided are incorrect" in error_message
        ), f"Empty password warning was missing. Found instead: '{error_message}'"
        logger.info("Verified failure response for blank password.")

    else:
        logger.critical(
            f"Unknown expected result token encountered in DDT sheet: '{expected_result}'"
        )
        raise ValueError(f"Result token '{expected_result}' has no matching assertion logic.")
