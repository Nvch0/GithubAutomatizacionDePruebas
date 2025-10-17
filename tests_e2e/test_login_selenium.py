import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
TEST_USER = os.getenv("TEST_USER", "TEST03")
TEST_PASS = os.getenv("TEST_PASS", "Nacho2002.")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


@pytest.fixture
def driver():
    """Crea la instancia del navegador con WebDriver Manager."""
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    driver.quit()


def test_login_correcto(driver):
    """Verifica el login correcto, saltando la advertencia de Ngrok si aparece."""

    login_url = BASE_URL.rstrip("/") + "/accounts/login/"
    print(f"[INFO] Abriendo: {login_url}")
    driver.get(login_url)

    wait = WebDriverWait(driver, 15)

    # 🔹 Paso 1: Detectar y saltar pantalla de advertencia de Ngrok si aparece
    try:
        print("[INFO] Verificando si aparece advertencia de ngrok...")
        visit_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[self::a or self::button][contains(.,'Visit Site')]"))
        )
        print("[INFO] Advertencia detectada, haciendo clic en 'Visit Site'...")
        visit_btn.click()
    except TimeoutException:
        print("[INFO] No apareció advertencia de ngrok. Continuando...")

    # 🔹 Paso 2: Esperar formulario de login
    username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    boton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

    # 🔹 Paso 3: Completar y enviar formulario
    username.send_keys(TEST_USER)
    password.send_keys(TEST_PASS)
    boton.click()

    # 🔹 Paso 4: Verificar redirección
    wait.until(EC.url_changes(login_url))
    print(f"[INFO] URL después del login: {driver.current_url}")
    assert "login" not in driver.current_url, "No se logró iniciar sesión correctamente"

    print("[✅] Login exitoso y pantalla de ngrok manejada correctamente.")
