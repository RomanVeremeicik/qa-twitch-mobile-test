import pytest
import requests

# --------------------------
#  API FIXTURE
# --------------------------
@pytest.fixture(scope="session")
def client():
    """Shared requests session for API tests."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "qa-automation-tests/1.0",
        "Accept": "application/json",
    })
    yield session
    session.close()


# --------------------------
#  SELENIUM FIXTURE
# --------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """Mobile Chrome (iPhone X) used for UI tests."""
    mobile_emulation = {"deviceName": "iPhone X"}

    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # uncomment to run headless:
    # chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.set_window_size(375, 812)
    driver.implicitly_wait(2)

    yield driver

    driver.quit()
