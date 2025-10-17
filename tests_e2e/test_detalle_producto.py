import os
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

def _now():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    fn = f"screenshots/{name}_{_now()}.png"
    driver.save_screenshot(fn)
    print(f"[📸] {fn}")

def _click_if(driver, xpath, timeout=2):
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        return True
    except Exception:
        return False

def _open(driver, path="/"):
    url = BASE_URL + path
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Saltar pantalla de NGROK si aparece
    try:
        if _click_if(driver, "//button[contains(.,'Visit Site')]", 2) or _click_if(driver, "//a[contains(.,'Visit Site')]", 2):
            print("[INFO] Banner ngrok detectado → 'Visit Site' presionado.")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        pass

    return wait

@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()

def test_detalle_producto_finaliza_en_descripcion(driver):
    """
    Caso: Ver la descripción del producto STATOFIX 100G y finalizar al verla.
    """
    wait = _open(driver, "/")
    _ss(driver, "detalle_home")

    # Hacer clic en la tarjeta STATOFIX 100G
    producto = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/producto/detalle_producto/133']")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", producto)
    producto.click()
    print("[INFO] Se hizo clic en STATOFIX 100G")

    # ✅ Detectar la descripción del producto y finalizar
    descripcion = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//p[@class='h5' and contains(.,'Descripcion del producto')]"))
    )
    _ss(driver, "detalle_producto_detectado")
    print("✅ 'Descripción del producto' detectada. Fin de la prueba.")
    return  # <--- Termina inmediatamente
