# tests_e2e/test_cart_add_two.py
import os
import time
import pytest
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL   = os.getenv("BASE_URL", "").rstrip("/")
TEST_USER  = os.getenv("TEST_USER", "TEST03")
TEST_PASS  = os.getenv("TEST_PASS", "Nacho2002.")
HEADLESS   = os.getenv("HEADLESS", "false").lower() == "true"

# IDs de producto que vamos a usar
ID_STATOFIX = 133
ID_LONA     = 136

def _now():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def _ss(driver, name):
    driver.save_screenshot(f"screenshots/{name}_{_now()}.png")

@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()

def _click_ngrok_if_needed(driver):
    """Si aparece el splash de ngrok, pulsa 'Visit Site'."""
    try:
        if "ngrok" in driver.current_url or "Are you about to visit" in driver.page_source:
            btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='#'] , a, button"))
            )
            # Busca específicamente el botón con texto 'Visit Site'
            for el in driver.find_elements(By.CSS_SELECTOR, "a, button"):
                if el.text.strip().lower() == "visit site":
                    el.click()
                    WebDriverWait(driver, 10).until(lambda d: "ngrok" not in d.current_url.lower())
                    break
    except Exception:
        pass

def _open(driver, path):
    url = BASE_URL + path
    driver.get(url)
    _click_ngrok_if_needed(driver)
    return WebDriverWait(driver, 15)

def _texto_en_html(driver):
    """Siempre lee page_source (evita WebElements obsoletos)."""
    return driver.page_source.lower()

def _esta_logueado(driver) -> bool:
    txt = _texto_en_html(driver)
    # si ya muestra el usuario en el header
    return TEST_USER.lower() in txt or "/accounts/logout" in txt or "cerrar sesión" in txt

def _hacer_login(driver):
    """Realiza login en la página de /accounts/login/."""
    # Algunos templates usan name="username"/"password" (Django) — cubrimos ambos casos
    # Usuario
    try:
        user = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
    except Exception:
        user = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
    user.clear(); user.send_keys(TEST_USER)

    # Password
    try:
        pwd = driver.find_element(By.NAME, "password")
    except Exception:
        pwd = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    pwd.clear(); pwd.send_keys(TEST_PASS)

    # Botón Ingresar (por texto o por tipo submit)
    btn = None
    for el in driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']"):
        if el.get_attribute("type") == "submit" or "ingresar" in el.text.lower():
            btn = el
            break
    assert btn, "No se encontró botón para enviar el login."
    btn.click()

    # Espera a que pase el login
    WebDriverWait(driver, 15).until(lambda d: _esta_logueado(d))

def _login_si_hace_falta(driver):
    """Si no está logueado, entra a /accounts/login/ y se autentica."""
    if _esta_logueado(driver):
        return
    # Busca link/botón 'Iniciar sesión'
    # Si no existe, vamos directo a /accounts/login/
    try:
        for el in driver.find_elements(By.CSS_SELECTOR, "a, button"):
            if "iniciar sesión" in el.text.strip().lower() or "iniciar sesion" in el.text.strip().lower():
                el.click()
                break
        else:
            driver.get(BASE_URL + "/accounts/login/")
    except Exception:
        driver.get(BASE_URL + "/accounts/login/")

    WebDriverWait(driver, 10).until(lambda d: "/accounts/login" in d.current_url.lower())
    _ss(driver, "cart_two_login_form")
    _hacer_login(driver)

def _click_add_to_cart_por_href(driver, prod_id: int):
    """Intenta click en <a href="/carro/agregar/{id}">; si falla, navega directo."""
    selector = (By.CSS_SELECTOR, f"a[href*='/carro/agregar/{prod_id}']")
    try:
        el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(selector))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try:
            el.click()
        except Exception:
            # fallback: ir directo al href
            href = el.get_attribute("href")
            if href:
                driver.get(href)
    except Exception:
        driver.get(f"{BASE_URL}/carro/agregar/{prod_id}")

def _asegurar_producto_en_carro(driver, prod_id: int):
    """Si no aparece el producto en /carro/, vuelve a agregarlo."""
    driver.get(BASE_URL + "/carro/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    if str(prod_id) not in _texto_en_html(driver):
        # volver al home y agregar
        driver.get(BASE_URL + "/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        _click_add_to_cart_por_href(driver, prod_id)
        # regresar a carrito
        driver.get(BASE_URL + "/carro/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

def _assert_cart_contiene(driver, *texts):
    """Valida que todos los textos estén en el carrito."""
    driver.get(BASE_URL + "/carro/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    html = _texto_en_html(driver)
    for t in texts:
        assert t.lower() in html, f"No se encontró '{t}' en el carrito."

def test_agregar_dos_productos(driver):
    """
    Flujo:
      - Abrir Home y hacer login si hace falta
      - Agregar STATOFIX 100G (id=133)
      - Agregar LONA ANARANJADA 4X8M (id=136)
      - Abrir /carro/ y validar ambos ítems presentes
    """
    wait = _open(driver, "/")
    _login_si_hace_falta(driver)

    # Agregar STATOFIX 100G desde Home
    _open(driver, "/")
    _click_add_to_cart_por_href(driver, ID_STATOFIX)

    # Agregar LONA ANARANJADA 4X8M desde Home
    _open(driver, "/")
    _click_add_to_cart_por_href(driver, ID_LONA)

    # Asegurar que ambos estén en el carrito (si el click fue interceptado, se corrige aquí)
    _asegurar_producto_en_carro(driver, ID_STATOFIX)
    _asegurar_producto_en_carro(driver, ID_LONA)

    _ss(driver, "cart_two_carro_final")
    # Validaciones por nombre de producto
    _assert_cart_contiene(driver, "STATOFIX 100G", "LONA ANARANJADA 4X8M")
