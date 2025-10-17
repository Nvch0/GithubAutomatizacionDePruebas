import os
import time
import pathlib
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
SS_DIR = pathlib.Path("screenshots")
SS_DIR.mkdir(exist_ok=True)

@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,900")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    yield drv
    drv.quit()

def _ngrok_visit_if_present(drv):
    try:
        btn = WebDriverWait(drv, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Visit Site'] | //button[normalize-space()='Visit Site']"))
        )
        btn.click()
        print("[INFO] Splash ngrok detectado -> click en 'Visit Site'")
    except Exception:
        pass

def _open_home(drv):
    drv.get(BASE_URL + "/")
    _ngrok_visit_if_present(drv)
    WebDriverWait(drv, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

def _go_to_category(drv, visible_text):
    WebDriverWait(drv, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Categor')]"))).click()
    WebDriverWait(drv, 10).until(EC.element_to_be_clickable((By.XPATH, f"//a[normalize-space()='{visible_text}']"))).click()

def test_categoria_fijaciones_adhesivos(driver):
    _open_home(driver)
    _go_to_category(driver, "Fijaciones y Adhesivos")

    h1 = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[contains(normalize-space(),'Categoria: Fijaciones y Adhesivos')]"))
    )

    driver.save_screenshot(str(SS_DIR / "cat_fijaciones_adhesivos.png"))
    assert "Fijaciones y Adhesivos" in h1.text
    print("✅ Prueba correcta: Fijaciones y Adhesivos")
