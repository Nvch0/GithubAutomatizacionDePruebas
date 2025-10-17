# tests_e2e/test_register.py
import os
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

# Usamos las fixtures `driver` y `open_page` desde tests_e2e/conftest.py

def _uniq(prefix="qauser"):
    return f"{prefix}_{int(time.time())}"

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png")

def test_registro_usuario(driver, open_page):
    """
    Registro exitoso:
    - Abre /registro/ (saltando 'Visit Site' de ngrok)
    - Completa el formulario con datos únicos
    - Hace click en 'Registrar' (con scroll + fallback JS si es necesario)
    - Verifica que NO permanezca en /registro/ y que no aparezcan errores
    """
    wait = open_page("/registro/")

    # Datos únicos
    username = _uniq()
    email    = f"{username}@example.test"
    password = "Prueba1234."

    # Localizadores del formulario
    user = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    first = driver.find_element(By.ID, "id_first_name")
    last  = driver.find_element(By.ID, "id_last_name")
    mail  = driver.find_element(By.ID, "id_email")
    pwd1  = driver.find_element(By.ID, "id_password1")
    pwd2  = driver.find_element(By.ID, "id_password2")

    # Botón Registrar (obtenemos el WebElement y también dejamos el locator para el re-wait)
    submit_locator = (By.CSS_SELECTOR, "button[type='submit'], .btn.btn-success[type='submit']")
    btn = wait.until(EC.element_to_be_clickable(submit_locator))

    # Completar
    user.clear();  user.send_keys(username)
    first.send_keys("QA")
    last.send_keys("Bot")
    mail.send_keys(email)
    pwd1.send_keys(password)
    pwd2.send_keys(password)

    _ss(driver, "registro_form_completo")

    # Guardamos la URL actual para detectar el cambio
    initial_url = driver.current_url

    # Asegurar visibilidad y clickabilidad; si lo interceptan, usamos JS
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", btn)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(submit_locator))
    try:
        btn.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", btn)

    # Esperar redirección (o al menos cambio de URL)
    try:
        WebDriverWait(driver, 12).until(EC.url_changes(initial_url))
    except TimeoutException:
        # Si no cambió la URL, revisamos si se muestran errores de validación
        errors = driver.find_elements(By.CSS_SELECTOR, ".errorlist, .alert.alert-danger, .invalid-feedback")
        _ss(driver, "registro_sin_redireccion")
        assert False, f"No hubo redirección tras registrar. Errores visibles: {bool(errors)}"

    final_url = driver.current_url
    _ss(driver, "registro_post_submit")

    # Validaciones de éxito
    # 1) No debe quedarse en /registro/
    assert "registro" not in final_url.lower(), f"Sigue en /registro/: {final_url}"

    # 2) No deben verse errores
    errors = driver.find_elements(By.CSS_SELECTOR, ".errorlist, .alert.alert-danger, .invalid-feedback")
    assert not errors, "Se muestran errores de validación tras el registro."

    print(f"[OK] Usuario registrado: {username} ({email}) → {final_url}")
