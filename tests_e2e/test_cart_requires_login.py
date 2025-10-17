import os
import time
import pathlib
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

SS_DIR = pathlib.Path("screenshots")
SS_DIR.mkdir(exist_ok=True)

def _ss(driver, name):
    p = SS_DIR / f"{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(str(p))
    print(f"[📸] {p}")

def _open(driver, path="/"):
    driver.get(BASE_URL + path)
    wait = WebDriverWait(driver, 10)
    # Bypass splash de ngrok si aparece
    try:
        visit = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[@id='root']//a[normalize-space()='Visit Site' or normalize-space()='Visit site' or normalize-space()='Visit'] | //button[normalize-space()='Visit Site' or normalize-space()='Visit site' or normalize-space()='Visit']")
            )
        )
        visit.click()
        print("[INFO] Splash ngrok detectado -> click en 'Visit Site'")
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.XPATH, "//*[@id='root']"))
        )
    except Exception:
        pass
    return wait

@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--allow-insecure-localhost")
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()

def _esperar_pagina_login(driver, timeout=10):
    """Devuelve True si vemos login por URL, título h2 o campo usuario."""
    w = WebDriverWait(driver, timeout)
    try:
        w.until(
            lambda d: (
                "/accounts/login" in d.current_url.lower()
                or d.find_elements(By.ID, "id_username")
                or d.find_elements(By.XPATH, "//h2[normalize-space()='Ingresa tus credenciales.']")
            )
        )
        return True
    except TimeoutException:
        return False

def test_cart_requires_login_redirects_to_login(driver):
    """
    Usuario NO logueado:
    - Click (o navegación directa) a 'Añadir al carro' de STATOFIX 100G
    - Debe verse la pantalla de login (URL, h2 o campo usuario)
    """
    wait = _open(driver, "/")
    _ss(driver, "cart_req_login_home")

    add_sel = (By.CSS_SELECTOR, "a[href*='/carro/agregar/133']")
    add_link = wait.until(EC.presence_of_element_located(add_sel))

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_link)
    _ss(driver, "cart_req_login_statofix_visible")

    href = add_link.get_attribute("href")

    try:
        # Intento de click “normal”
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(add_sel)).click()
    except (ElementClickInterceptedException, TimeoutException) as e:
        # Si está interceptado, navego directo al href
        print(f"[INFO] Click interceptado ({type(e).__name__}) -> voy a {href}")
        driver.get(href)

    # Confirmamos que llegó a la pantalla de login
    ok = _esperar_pagina_login(driver, timeout=10)
    _ss(driver, "cart_req_login_login_page")

    assert ok, "No se detectó la pantalla de inicio de sesión."
    print("✅ Prueba exitosa: al intentar añadir sin login, se mostró la página de inicio de sesión.")
