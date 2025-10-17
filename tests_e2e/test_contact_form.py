# tests_e2e/test_contact_form.py
import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = os.getenv("BASE_URL", "/").rstrip("/") + "/"
USER = os.getenv("TEST_USER", "TEST03")
PWD  = os.getenv("TEST_PASS", "Nacho2002.")

def _ss(driver, name):
    """Guarda capturas en carpeta screenshots/"""
    os.makedirs("screenshots", exist_ok=True)
    p = f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(p)
    print(f"[📸] {p}")

def _bypass_ngrok(driver):
    """Evita el banner de seguridad de ngrok si aparece."""
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//*[self::a or self::button][contains(.,'Visit Site')]"))
        )
        btn.click()
        print("[INFO] Intersticial ngrok aceptado.")
    except Exception:
        pass

def _login(driver, wait):
    """Inicia sesión con TEST03 si el sitio lo requiere."""
    driver.get(BASE + "accounts/login/")
    _bypass_ngrok(driver)
    _ss(driver, "contact_login_page")
    u = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    p = wait.until(EC.presence_of_element_located((By.ID, "id_password")))
    u.clear(); u.send_keys(USER)
    p.clear(); p.send_keys(PWD)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
    WebDriverWait(driver, 10).until(
        EC.any_of(
            EC.url_contains("/"),
            EC.presence_of_element_located((By.XPATH, f"//*[contains(.,'{USER}')]")),
        )
    )
    _ss(driver, "contact_logged_in")

def test_enviar_mensaje_contacto(driver, open_page):
    """
    Caso de Prueba 1:
    Enviar mensaje con todos los campos completos
    """
    wait = open_page("/")
    _login(driver, wait)

    # 1️⃣ Ir a la página de contacto
    driver.get(BASE + "contacto/")
    _bypass_ngrok(driver)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h2[contains(.,'Contáctate')]")))
    _ss(driver, "contact_page_loaded")

    # 2️⃣ Completar formulario
    nombre = wait.until(EC.presence_of_element_located((By.NAME, "name")))
    correo = driver.find_element(By.NAME, "email")
    asunto = driver.find_element(By.NAME, "subject")
    mensaje = driver.find_element(By.NAME, "message")

    nombre.clear();  nombre.send_keys("Manuel Hidalgo")
    correo.clear();  correo.send_keys("manuel.hidalgo@gmail.com")
    asunto.clear();  asunto.send_keys("Consulta sobre productos")
    mensaje.clear(); mensaje.send_keys("Me gustaría saber más sobre las herramientas Makita")
    _ss(driver, "contact_form_filled")

    # 3️⃣ Enviar el formulario
    btn_enviar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Enviar mensaje')]")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_enviar)
    time.sleep(0.5)
    btn_enviar.click()
    _ss(driver, "contact_sent_click")

    # 4️⃣ Validar resultado (mensaje de éxito)
    success_variants = [
        "se ha enviado el correo",          # mensaje real en tu app
        "mensaje enviado con éxito",        # texto alternativo
    ]

    ok = False
    page_lower = driver.page_source.lower()
    for msg in success_variants:
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    f"//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{msg}')]"
                ))
            )
            ok = True
            break
        except Exception:
            if msg in page_lower:
                ok = True
                break

    assert ok, f"No se encontró ninguno de los mensajes de éxito: {success_variants}"
    _ss(driver, "contact_success")
    print("[✅] El mensaje fue enviado correctamente y se muestra el texto de confirmación.")
