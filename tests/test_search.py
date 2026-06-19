"""
File: test_search.py

Purpose:
Contains Pytest test cases for search functionality on Demo Web Shop.
Validates search accuracy for existing catalog entries (computing books) and
verifies missing product notifications when querying non-existing elements.

Author: <Your Name>

Created: 2026-06-19
"""

import logging

from pages.search_page import SearchPage

# Initialize logger
logger = logging.getLogger(__name__)


def test_search_for_existing_product(driver):
    """
    Verifies that searching for a valid product term ('Computing')
    successfully returns relevant products in the catalog search grid.
    """
    logger.info("Starting test scenario: Search for Existing Product")

    search_page = SearchPage(driver)
    search_page.navigate()
    search_page.perform_search("Computing")

    # Retrieve and evaluate product titles
    product_titles = search_page.get_product_results_titles()
    assert (
        len(product_titles) > 0
    ), "No products were returned in search results, but results were expected."

    # Validate that at least one item title contains the query substring
    match_found = any("Computing" in title for title in product_titles)
    assert (
        match_found
    ), f"None of the product results matched the search term 'Computing'. Found: {product_titles}"
    logger.info("Successfully validated search results for existing item.")


def test_search_for_non_existing_product(driver):
    """
    Verifies that searching for a non-existing product query ('non_existent_item_xyz')
    returns the appropriate catalog missing message.
    """
    logger.info("Starting test scenario: Search for Non-Existing Product")

    search_page = SearchPage(driver)
    search_page.navigate()
    search_page.perform_search("non_existent_item_xyz")

    # Validate catalog warnings
    warning_text = search_page.get_no_results_message()
    expected_warning = "No products were found that matched your criteria."
    assert (
        warning_text == expected_warning
    ), f"Expected missing products result notification, but retrieved: '{warning_text}'"
    logger.info("Successfully validated missing products warning for non-existent queries.")
