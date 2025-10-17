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
    """Click automático en 'Visit Site' si aparece el splash de ngrok."""
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


def test_carousel_next(driver):
    """Verifica que el botón 'Next' del carrusel principal funciona."""
    driver.get(BASE_URL + "/")
    _dismiss_ngrok_if_present(driver)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    _ss(driver, "carousel_home_inicial")

    # Esperar carrusel visible
    carousel = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "carouselExampleInterval"))
    )

    # Obtener la primera imagen visible (o slide activo)
    first_slide = driver.execute_script("""
        return Array.from(document.querySelectorAll('#carouselExampleInterval .carousel-item'))
            .findIndex(e => e.classList.contains('active'));
    """)
    print(f"Índice inicial del slide activo: {first_slide}")

    # Click en el botón "Next"
    next_button = driver.find_element(By.CSS_SELECTOR, ".carousel-control-next")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_button)
    next_button.click()
    time.sleep(2)  # Dar tiempo a la animación

    _ss(driver, "carousel_despues_click")

    # Verificar que cambió el slide activo
    new_slide = driver.execute_script("""
        return Array.from(document.querySelectorAll('#carouselExampleInterval .carousel-item'))
            .findIndex(e => e.classList.contains('active'));
    """)
    print(f"Índice después del click: {new_slide}")

    assert new_slide != first_slide, "El carrusel no cambió de slide tras hacer clic en 'Next'"
