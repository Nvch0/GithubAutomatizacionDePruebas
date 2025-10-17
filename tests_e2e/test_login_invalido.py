# tests_e2e/test_login_invalido.py
import os, time, unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def _norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

def test_login_invalido(driver, open_page):
    # Abre login con bypass ngrok
    wait = open_page("/accounts/login/")

    # Campos
    user = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    pwd  = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    btn  = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

    # Credenciales inválidas
    user.clear(); user.send_keys("automatizacion")
    pwd.clear();  pwd.send_keys("Incorrecta123")
    btn.click()

    # Sigue en /accounts/login/
    WebDriverWait(driver, 10).until(EC.url_contains("/accounts/login"))
    assert "/accounts/login" in driver.current_url.lower()

    # Banner de error
    alert = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.alert.alert-danger, .alert-danger"))
    )
    esperado = _norm("Por favor introduzca nombre de usuario y contraseña correctos")
    assert _norm(alert.text).startswith(esperado[:25]), f"Mensaje inesperado: {alert.text!r}"

    # Sin sesión (no aparece logout ni badge)
    no_session = not driver.find_elements(By.CSS_SELECTOR, "a[href*='logout'], .logout, [data-test='user-badge']")
    assert no_session, "Se detectó sesión activa con credenciales inválidas."

    # Evidencia
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/login_invalido_{time.strftime('%Y%m%d-%H%M%S')}.png")
