# Test Data Directory

This directory stores externalized test data used for Data-Driven Testing (DDT).

## Contents
* `login_test_data.csv`: A CSV file containing test combinations (username, password, expected_result) for login testing.

## Usage
Pytest fixtures or helper methods parse files in this directory to run the same test scenario against multiple input datasets.
