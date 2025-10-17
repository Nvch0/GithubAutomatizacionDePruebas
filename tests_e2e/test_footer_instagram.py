import os
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

SS_DIR = Path("screenshots")
SS_DIR.mkdir(exist_ok=True)


def _ss(driver, name: str):
    ts = time.strftime("%Y%m%d-%H%M%S")
    driver.save_screenshot(str(SS_DIR / f"{name}_{ts}.png"))


def _dismiss_ngrok_if_present(driver, timeout=6):
    """Si aparece la página intermedia de ngrok, hace click en 'Visit Site' y espera a que desaparezca."""
    end = time.time() + timeout
    while time.time() < end:
        try:
            btn = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//a[normalize-space()='Visit Site'] | //button[normalize-space()='Visit Site']"
                ))
            )
            driver.execute_script("arguments[0].click();", btn)
            WebDriverWait(driver, 5).until(
                lambda d: 'ngrok' not in (d.title or '').lower()
                and 'ngrok' not in d.find_element(By.TAG_NAME, "body").text.lower()
            )
            return
        except Exception:
            time.sleep(0.25)


@pytest.fixture
def driver():
    if not BASE_URL:
        raise RuntimeError("Falta BASE_URL en las variables de entorno")
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()


def test_footer_instagram(driver):
    """Verifica el enlace 'Instagram' en el footer y que abra Instagram en una pestaña nueva."""
    driver.get(BASE_URL + "/")
    _dismiss_ngrok_if_present(driver)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    _ss(driver, "ig_home")

    # Scroll al footer
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h5[normalize-space()='Social']"))
    )

    link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Instagram']"))
    )
    href = (link.get_attribute("href") or "").lower()
    assert "instagram.com" in href, f"href inesperado para Instagram: {href}"

    driver.execute_script("window.open(arguments[0].href, '_blank');", link)
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 15).until(lambda d: "instagram" in (d.current_url or "").lower())
    _ss(driver, "ig_nueva_pestana")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
