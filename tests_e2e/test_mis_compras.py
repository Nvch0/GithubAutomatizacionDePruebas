# tests_e2e/test_mis_compras.py
import os, time
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TEST_USER = os.getenv("TEST_USER", "TEST03")
TEST_PASS = os.getenv("TEST_PASS", "Nacho2002.")

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
    wait = WebDriverWait(driver, 12)

    # Banner de ngrok (Visit Site)
    try:
        # Botón como <button>…
        if _click_if(driver, "//button[contains(.,'Visit Site')]", timeout=2):
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        else:
            # O como <a>…
            if _click_if(driver, "//a[contains(.,'Visit Site')]", timeout=2):
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        pass

    return WebDriverWait(driver, 15)

def _login_if_needed(driver, wait):
    # Si ya aparece el botón/dropdown con el usuario, no hace falta login
    try:
        wait.until(EC.presence_of_element_located((
            By.XPATH, "//*[@id='navbarSupportedContent']//*[contains(., '%s')]" % TEST_USER
        )))
        return
    except Exception:
        pass

    # Ir directo a la página de login
    driver.get(BASE_URL + "/accounts/login/")
    user = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    pwd  = wait.until(EC.presence_of_element_located((By.ID, "id_password")))
    user.clear(); user.send_keys(TEST_USER)
    pwd.clear();  pwd.send_keys(TEST_PASS)

    # Botón "Ingresar"
    _click_if(driver, "//button[@type='submit' or contains(.,'Ingresar')]", timeout=5)

    # Esperar que en el navbar aparezca el usuario
    WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((
            By.XPATH, "//*[@id='navbarSupportedContent']//*[contains(., '%s')]" % TEST_USER
        ))
    )

@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opts)  # usa el chromedriver de tu PATH
    yield drv
    drv.quit()

def test_ver_mis_compras_con_sesion(driver):
    """
    Finaliza inmediatamente al detectar el título 'Mis compras'.
    """
    wait = _open(driver, "/")
    _login_if_needed(driver, wait)

    # Abrir el dropdown del usuario y entrar a "Mis Compras"
    user_dropdown_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class,'dropdown')]/button[contains(@class,'dropdown-toggle')]"
        ))
    )
    user_dropdown_btn.click()

    mis_compras_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH, "//a[contains(@class,'dropdown-item') and (contains(.,'Mis Compras') or contains(.,'Mis compras'))]"
        ))
    )
    mis_compras_link.click()

    # ✅ Esperar el título y salir
    titulo = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h2[contains(normalize-space(),'Mis compras')]"))
    )
    _ss(driver, "miscompras_detectado")
    assert "mis compras" in titulo.text.lower()

    print("✅ Listo: se detectó 'Mis compras'. Fin del caso.")
    return  # <<--- FIN inmediato del test
