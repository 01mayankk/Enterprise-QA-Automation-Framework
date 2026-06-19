# Automated Testing Strategy

This document outlines the testing scope, test data setup, validation assertions, and strategy used for our test regression suite.

---

## 1. Scope of Automation

We target the public **Demo Web Shop** (https://demowebshop.tricentis.com/) e-commerce web application. The suite covers three core operational areas:
- **Authentication**: Login forms validation (positive and negative cases).
- **Identity Management**: User account registration validation.
- **Product Discovery**: Catalog search functions.

---

## 2. Test Case Specifications

### 2.1 Login Scenarios (`tests/test_login.py`)
Driven by Data-Driven Testing (DDT) using records from `data/login_test_data.csv`.

| Scenario ID | Test Input (Username, Password) | Expected Outcome | Assertions & Validations |
| :--- | :--- | :--- | :--- |
| **Valid Login** | `tester_antigravity@test.com`, `Pass123!` | Success | Logout link is displayed on the page header. Log out immediately to restore state. |
| **Invalid Password** | `tester_antigravity@test.com`, `WrongPass!` | Failure | Login fails; validation summary element contains correct warning texts. |
| **Invalid Email Format** | `invalid_user_format`, `Pass123!` | Failure | Login fails; field validation error returns "Please enter a valid email address" or "Wrong email". |
| **Empty Username** | `[BLANK]`, `Pass123!` | Failure | Login fails; validation displays field error: "Please enter your email". |
| **Empty Password** | `tester_antigravity@test.com`, `[BLANK]` | Failure | Login fails; validation summary displays error. |

---

### 2.2 Registration Scenarios (`tests/test_registration.py`)
Validates user onboarding requirements.

1. **Successful Onboarding (Positive Path)**:
   - **Strategy**: To prevent test failure caused by existing records, the script generates a unique email on every run (e.g. `pytest_user_YYYYMMDDHHMMSS@test.com`).
   - **Validation**: Verifies that the success result text contains "Your registration completed".
2. **Duplicate Registration Prevention (Negative Path)**:
   - **Strategy**: Re-attempts to register with the static credentials of our pre-registered test user (`tester_antigravity@test.com`).
   - **Validation**: Asserts that registration fails and returns the summary error: "The specified email already exists".
3. **Email Formatting Rules (Negative Path)**:
   - **Strategy**: Attempts registration using an invalid formatting term (`invalid_user_format`).
   - **Validation**: Asserts that registration fails and displays field validation error: "Wrong email".

---

### 2.3 Catalog Search Scenarios (`tests/test_search.py`)
Validates product indexing correctness.

1. **Product Search (Positive Path)**:
   - **Strategy**: Search for a valid product search term (`Computing`).
   - **Validation**: Verifies that search results are displayed and that the returned products include "Computing" inside their titles.
2. **Missing Product Search (Negative Path)**:
   - **Strategy**: Search for a term that does not exist in the store catalog (`non_existent_item_xyz`).
   - **Validation**: Verifies that no products are returned and the empty search result displays: "No products were found that match your criteria."

---

## 3. Test Design Principles

- **Test Independence**: Every test case runs in its own browser session. No test depends on the state or execution output of another.
- **Self-Healing Test Data**: Rather than relying on database backups to manage test data state, the suite registers the required test account dynamically if it is missing at startup. It also creates unique generated profiles to guarantee fresh runs.
- **Assertion Messages**: Every `assert` command contains a descriptive custom failure message to provide readable stack traces without needing to trace the source code line.
