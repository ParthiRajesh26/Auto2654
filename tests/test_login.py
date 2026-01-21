import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# Test Metadata & Constants
# =========================
JIRA_TICKET = {
    "key": "KAN-15",
    "summary": "Automate login functionality for OrangeHRM",
    "description": (
        "Application: OrangeHRM\n"
        "Feature: Login\n"
        "Scenario:\n"
        "Verify that a valid user can successfully log in to the application.\n"
        "Steps:\n"
        "1. Navigate to the login page\n"
        "2. Enter valid username\n"
        "3. Enter valid password\n"
        "4. Click on Login button\n"
        "Expected Result:\n"
        "User should be redirected to the dashboard page."
    ),
    "status": "To Do",
    "assignee": "",
    "due_date": ""
}

LOGIN_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
USERNAME = "Admin"
PASSWORD = "admin123"
USERNAME_XPATH = "//input[@name='username']"
PASSWORD_XPATH = "//input[@name='password']"
LOGIN_BTN_XPATH = "//button[@type='submit']"
DASHBOARD_URL_KEYWORD = "/dashboard"  # Validate redirection to dashboard

# =========================
# Utility Functions
# =========================
def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def validate_jira_ticket(ticket):
    required_fields = ['key', 'summary', 'description']
    for field in required_fields:
        if field not in ticket or not ticket[field]:
            raise ValueError(f"Jira ticket missing or malformed field: {field}")

def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except Exception as e:
        raise AssertionError(f"Element not found: {value}. Exception: {e}")

def wait_for_url_contains(driver, keyword, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: keyword in d.current_url
        )
        return True
    except Exception:
        return False

# =========================
# Test Implementation
# =========================
def test_orangehrm_login_valid_user():
    """
    Jira Ticket: KAN-15
    Summary: Automate login functionality for OrangeHRM
    Description: Verify that a valid user can successfully log in to the application.
    Steps:
        1. Navigate to the login page
        2. Enter valid username
        3. Enter valid password
        4. Click on Login button
    Expected Result:
        User should be redirected to the dashboard page.
    """
    # Input Validation
    try:
        validate_jira_ticket(JIRA_TICKET)
    except Exception as input_err:
        pytest.fail(f"Input validation failed: {input_err}")

    driver = None
    try:
        driver = get_chrome_driver()
        driver.get(LOGIN_URL)

        # Step 1: Wait for username field
        username_field = wait_for_element(driver, By.XPATH, USERNAME_XPATH)
        username_field.clear()
        username_field.send_keys(USERNAME)

        # Step 2: Wait for password field
        password_field = wait_for_element(driver, By.XPATH, PASSWORD_XPATH)
        password_field.clear()
        password_field.send_keys(PASSWORD)

        # Step 3: Click login button
        login_btn = wait_for_element(driver, By.XPATH, LOGIN_BTN_XPATH)
        login_btn.click()

        # Step 4: Wait for dashboard redirection (URL contains '/dashboard')
        redirected = wait_for_url_contains(driver, DASHBOARD_URL_KEYWORD, timeout=15)
        assert redirected, (
            f"Login failed: Did not redirect to dashboard. "
            f"Current URL: {driver.current_url}"
        )

        # Step 5: Additional validation - check dashboard element presence
        dashboard_header_xpath = "//h6[text()='Dashboard']"
        dashboard_header = wait_for_element(driver, By.XPATH, dashboard_header_xpath, timeout=10)
        assert dashboard_header.is_displayed(), "Dashboard header not visible after login."

    except AssertionError as ae:
        pytest.fail(f"Assertion failed: {ae}")
    except Exception as e:
        pytest.fail(f"Unexpected error during test execution: {e}")
    finally:
        if driver:
            driver.quit()
