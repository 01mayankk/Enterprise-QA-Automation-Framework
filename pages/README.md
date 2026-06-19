# Page Objects Layer

This directory contains the Page Object Model (POM) classes representing the target application's pages.

## Contents
* `base_page.py`: Wrapper for common Selenium WebDriver operations.
* `login_page.py`: Selectors and actions for the Login page.
* `registration_page.py`: Selectors and actions for the User Registration page.
* `search_page.py`: Selectors and actions for the Product Search page.

## Usage
Tests import these page objects to interact with the browser. No locators should be placed inside tests, and no assertions should live inside page objects.
