"""
File: search_page.py

Purpose:
Contains the SearchPage page object representing product search functionality.
Defines locators for search input fields, submission buttons, product titles
in search results, and notifications when search returns no products.

Author: <Your Name>

Created: 2026-06-19
"""

import logging
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage

# Setup logger
logger = logging.getLogger(__name__)


class SearchPage(BasePage):
    """
    SearchPage Object containing locators, navigation mechanisms, actions,
    and validation methods for product searches.
    """

    # Locators
    SEARCH_INPUT_FIELD = (By.ID, "small-searchterms")
    SEARCH_SUBMIT_BUTTON = (By.CSS_SELECTOR, "input.search-box-button")
    PRODUCT_TITLES = (By.CSS_SELECTOR, ".product-item .product-title a")
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, ".search-results .result")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.home_url = self.config.base_url

    def navigate(self) -> None:
        """Navigates to the home page containing the search header."""
        logger.info("Navigating to home page for search operations.")
        self.navigate_to(self.home_url)

    def perform_search(self, search_query: str) -> None:
        """
        Enters a product query into the search field and submits.
        """
        logger.info(f"Performing search with query: '{search_query}'")
        self.enter_text(self.SEARCH_INPUT_FIELD, search_query)
        self.click_element(self.SEARCH_SUBMIT_BUTTON)

    def get_product_results_titles(self) -> List[str]:
        """
        Retrieves list of titles for all visible products matching search query.
        Handles StaleElementReferenceException automatically via a retry loop.
        """
        logger.info("Retrieving product search result titles.")
        import time

        from selenium.common.exceptions import StaleElementReferenceException

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                product_elements = self.find_elements(self.PRODUCT_TITLES)
                titles = [element.text.strip() for element in product_elements]
                logger.info(f"Found {len(titles)} search result item(s): {titles}")
                return titles
            except StaleElementReferenceException:
                logger.warning(
                    f"Stale element reference encountered on attempt {attempt + 1}. "
                    "Retrying retrieval..."
                )
                time.sleep(0.5)

        # Fallback final attempt if all retries are exhausted
        product_elements = self.find_elements(self.PRODUCT_TITLES)
        return [element.text.strip() for element in product_elements]

    def get_no_results_message(self) -> str:
        """
        Retrieves warning text if search query returned zero results.
        """
        logger.info("Checking for 'No products found' results notification.")
        if self.is_element_displayed(self.NO_RESULTS_MESSAGE):
            return self.get_element_text(self.NO_RESULTS_MESSAGE).strip()
        return ""
