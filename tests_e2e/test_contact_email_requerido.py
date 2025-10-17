# tests_e2e/test_contact_email_requerido.py
import os, time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# =============================
# CONFIGURACIÓN GLOBAL
# =============================
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


# =============================
# FUNCIONES AUXILIARES
# =============================
def _ss(driver, name):
    """Guarda una captura con timestamp"""
    ts = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/{name}_{ts}.png")


# =============================
# FIXTURES
# =============================
@pytest.fixture
def driver():
    """Inicializa el navegador Chrome con opciones configurables"""
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")

    # ✅ Corrección: usar Service con webdriver-manager
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture
def open_page(driver):
    """Abre una página y maneja la advertencia de ngrok automáticamente"""
    def _open(path="/"):
        url = f"{BASE_URL}{path}"
        driver.get(url)

        # Verifica si aparece la advertencia de ngrok
        try:
            btn = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Visit Site')]"))
            )
            btn.click()
        except Exception:
            pass

        return WebDriverWait(driver, 10)
    return _open


# =============================
# TEST: Email requerido
# =============================
def test_contacto_email_requerido(driver, open_page):
    """
    Caso de Prueba: Enviar el formulario de contacto sin el campo 'Correo electrónico'.

    Dado que el usuario está en /contacto/
    Cuando completa los demás campos y deja vacío el correo
    Entonces el navegador muestra el mensaje nativo "Completa este campo".
    """
    wait = open_page("/contacto/")

    # Localizar campos
    name = wait.until(EC.presence_of_element_located((By.NAME, "name")))
    subj = driver.find_element(By.NAME, "subject")
    msg = driver.find_element(By.NAME, "message")
    submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    # Completar campos excepto el correo
    name.send_keys("Manuel Hidalgo")
    subj.send_keys("Consulta sobre productos")
    msg.send_keys("Quisiera saber si tienen stock de herramientas Makita.")
    _ss(driver, "contacto_sin_email_antes_enviar")

    # Intentar enviar formulario
    submit.click()

    # Leer mensaje nativo del navegador (validationMessage)
    email_input = driver.find_element(By.NAME, "email")
    validation_message = driver.execute_script("return arguments[0].validationMessage;", email_input)
    print("[DEBUG] validationMessage:", validation_message)

    # Validación (acepta variaciones en idioma)
    assert any(
        txt in validation_message.lower()
        for txt in ["completa este campo", "please fill out this field"]
    ), f"Mensaje esperado no encontrado. Recibido: {validation_message}"

    _ss(driver, "contacto_sin_email_mensaje")
    print("[✅] Validación de campo obligatorio 'Correo electrónico' verificada correctamente.")
