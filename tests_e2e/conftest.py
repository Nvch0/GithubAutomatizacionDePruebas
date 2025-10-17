# tests_e2e/conftest.py
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")

def _build_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,800")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

@pytest.fixture
def driver():
    d = _build_driver()
    yield d
    d.quit()

@pytest.fixture
def open_page(driver):
    """Devuelve una función para abrir rutas y saltar el aviso de ngrok si aparece."""
    def _open(path, timeout=10):
        url = BASE_URL.rstrip("/") + path
        driver.get(url)
        wait = WebDriverWait(driver, timeout)
        # Bypass de la pantalla 'Visit Site' de ngrok si aparece
        try:
            visit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[self::a or self::button][contains(.,'Visit Site')]"))
            )
            visit_btn.click()
        except TimeoutException:
            pass
        return wait
    return _open
# --- Helper: login como usuario de pruebas ---
import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png")

@pytest.fixture
def login_as_test_user(driver, open_page):
    def _login():
        wait = open_page("/accounts/login/")
        user = os.getenv("TEST_USER", "TEST03")
        pwd  = os.getenv("TEST_PASS", "Nacho2002.")

        username = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        password = wait.until(EC.presence_of_element_located((By.ID, "id_password")))
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class,'btn-success')]")))

        username.clear(); username.send_keys(user)
        password.clear(); password.send_keys(pwd)
        _ss(driver, "login_before_submit")
        btn.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/"))
        _ss(driver, "login_ok")
        return True
    return _login
