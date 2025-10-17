import os
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
HEADLESS  = os.getenv("HEADLESS", "false").lower() == "true"
TEST_USER = os.getenv("TEST_USER", "TEST03")
TEST_PASS = os.getenv("TEST_PASS", "Nacho2002.")

# ------------ utilidades ------------
def _ts(): return datetime.now().strftime("%Y%m%d-%H%M%S")
def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{name}_{_ts()}.png"
    driver.save_screenshot(path)
    print(f"[📸] {path}")

def _click_if(driver, xp, timeout=2):
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
        return True
    except Exception:
        return False

def _open(driver, path="/"):
    url = f"{BASE_URL}{path}"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Saltar pantalla de ngrok si aparece
    if _click_if(driver, "//button[contains(.,'Visit Site')]", 2) or \
       _click_if(driver, "//a[contains(.,'Visit Site')]", 2):
        print("[INFO] ngrok banner → Visitar sitio")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return wait

def _login_if_needed(driver, wait):
    # Si ya aparece el menú de usuario, estamos logueados
    if TEST_USER.lower() in driver.page_source.lower():
        return

    _open(driver, "/accounts/login/")
    user = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    pwd  = driver.find_element(By.ID, "id_password")
    btn  = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    user.clear(); user.send_keys(TEST_USER)
    pwd.clear();  pwd.send_keys(TEST_PASS)
    _ss(driver, "detalle_login_completado")
    btn.click()

    # Confirmar login
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), TEST_USER)
    )
    print("[OK] Sesión iniciada")

# ------------ webdriver ------------
@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()

# ------------ test ------------
def test_agregar_desde_detalle(driver):
    """
    Flujo:
      - Iniciar sesión si hace falta
      - Abrir detalle del producto 133 (STATOFIX 100G)
      - Clic en 'Agregar'
      - Validar /carro/ con el producto presente
    """
    wait = _open(driver, "/")
    _login_if_needed(driver, wait)

    # Ir al detalle del producto STATOFIX 100G
    wait = _open(driver, "/producto/detalle_producto/133")
    _ss(driver, "detalle_abierto")

    # Botón 'Agregar'
    add_sel = (By.CSS_SELECTOR, "a[href*='/carro/agregar/133']")
    add = wait.until(EC.element_to_be_clickable(add_sel))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add)
    _ss(driver, "detalle_boton_agregar_visible")

    # Click robusto (si es interceptado, ir por href)
    href = add.get_attribute("href")
    try:
        add.click()
    except Exception:
        print("[WARN] Click interceptado → navegación directa al href")
        driver.get(href)

    # Esperar carrito y validar producto
    try:
        WebDriverWait(driver, 8).until(lambda d: "/carro" in d.current_url.lower())
    except Exception:
        driver.get(f"{BASE_URL}/carro/")

    _ss(driver, "carro_abierto")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'STATOFIX 100G')]"))
    )
    print("✅ Producto 'STATOFIX 100G' aparece en el carrito. Prueba OK.")
