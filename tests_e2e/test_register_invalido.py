import os, time, unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

# Usa las fixtures `driver` y `open_page` que ya tienes en tests_e2e/conftest.py

def _uniq(prefix="badpwd"):
    return f"{prefix}_{int(time.time())}"

def _norm(s: str) -> str:
    # normaliza tildes y minúsculas
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()

def test_registro_contrasena_muy_corta(driver, open_page):
    """
    Registro inválido: contraseña '123' (muy corta).
    - Completa formulario con datos válidos salvo la contraseña
    - Click en 'Registrar' (con scroll + fallback JS)
    - Debe permanecer en /registro/ y mostrar mensajes de error
    """
    wait = open_page("/registro/")

    # Datos (username/email únicos) + pwd inválida
    username = _uniq("usuario")
    email    = f"{username}@example.test"
    pwd_bad  = "123"

    # Campos
    user = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    first = driver.find_element(By.ID, "id_first_name")
    last  = driver.find_element(By.ID, "id_last_name")
    mail  = driver.find_element(By.ID, "id_email")
    pwd1  = driver.find_element(By.ID, "id_password1")
    pwd2  = driver.find_element(By.ID, "id_password2")

    # Botón
    submit_locator = (By.CSS_SELECTOR, "button[type='submit'], .btn.btn-success[type='submit']")
    btn = wait.until(EC.element_to_be_clickable(submit_locator))

    # Completar
    user.clear(); user.send_keys(username)
    first.send_keys("Manuel")
    last.send_keys("Hidalgo")
    mail.send_keys(email)
    pwd1.send_keys(pwd_bad)
    pwd2.send_keys(pwd_bad)

    # Evidencia antes
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/registro_invalido_form_{int(time.time())}.png")

    # Click con scroll + fallback JS
    initial_url = driver.current_url
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(submit_locator))
    try:
        btn.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", btn)

    # Debe permanecer en /registro/
    try:
        WebDriverWait(driver, 5).until(EC.url_changes(initial_url))
        # Si cambió la URL, fallo: con pwd inválida NO debe redirigir
        assert False, f"Se redirigió a {driver.current_url} con contraseña inválida."
    except TimeoutException:
        pass  # correcto: no cambió

    assert "/registro" in driver.current_url.lower(), "No permaneció en /registro/ con contraseña inválida."

    # Mensajes de error visibles (como en tu captura)
    # Buscamos el bloque rojo y/o los item de validación de Django
    posibles_selectores = [
        (By.CSS_SELECTOR, ".errorlist, .invalid-feedback, .alert.alert-danger"),
        (By.XPATH, "//*[contains(.,'contraseña es muy corta') or contains(.,'8 caracteres')]"),
    ]
    hay_error = any(driver.find_elements(*loc) for loc in posibles_selectores)
    assert hay_error, "No se encontró mensaje de error para contraseña corta."

    # Validamos texto clave (tolerante a tildes)
    page_text = _norm(driver.page_source)
    assert "muy corta" in page_text and "8 caracteres" in page_text, \
        "El mensaje esperado de 'contraseña muy corta (8 caracteres)' no se encuentra."

    # Evidencia después
    driver.save_screenshot(f"screenshots/registro_invalido_err_{int(time.time())}.png")
