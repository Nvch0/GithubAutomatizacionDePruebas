# tests_e2e/test_logout.py
import os
import time
import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
HEADLESS = os.environ.get("HEADLESS", "true").lower() in ("1", "true", "yes")
TEST_USER = os.environ.get("TEST_USER", "TEST03")
TEST_PASS = os.environ.get("TEST_PASS", "Nacho2002.")
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")


@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


def _ensure_screenshots_dir():
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def _ss(driver, name):
    _ensure_screenshots_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fname = f"{name}_{ts}.png"
    path = os.path.join(SCREENSHOTS_DIR, fname)
    driver.save_screenshot(path)
    print(f"[📸] Screenshot guardado: {path}")
    return path


def _bypass_ngrok_if_needed(driver):
    try:
        # heurística para detectar interstitial ngrok
        is_ngrok = (
            "ngrok" in (driver.title or "").lower()
            or "You are about to visit" in (driver.page_source or "")[:1000]
            or "You are about to visit" in (driver.title or "")
        )
        if not is_ngrok:
            return
        print("[INFO] Interstitial de ngrok detectado. Intentando pulsar 'Visit Site'...")
        wait = WebDriverWait(driver, 6)
        xpaths = [
            "//a[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='visit site']",
            "//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='visit site']",
            "//a[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'visit site')]",
        ]
        clicked = False
        for xp in xpaths:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click()
                clicked = True
                break
            except Exception:
                pass
        if not clicked:
            driver.execute_script("""
                const btn = Array.from(document.querySelectorAll('a,button'))
                  .find(e => (e.textContent||'').trim().toLowerCase() === 'visit site');
                if (btn) btn.click();
            """)
        # esperar que la URL deje de ser la interstitial (o que el body se cargue)
        WebDriverWait(driver, 10).until(lambda d: d.current_url and "ngrok" not in d.current_url.lower())
    except Exception as e:
        print("[WARN] No se pudo completar bypass de ngrok:", e)


def open_page(driver, path="/"):
    url = BASE_URL.rstrip("/") + "/" + path.lstrip("/")
    driver.get(url)
    time.sleep(0.3)
    _bypass_ngrok_if_needed(driver)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return WebDriverWait(driver, 10)


def _login_if_needed(driver, wait):
    """
    Asegura estar autenticado con TEST_USER/TEST_PASS.
    Si ya está logueado (nombre de usuario en la cabecera), no re-login.
    """
    # si aparece el nombre del usuario en un botón/elemento del header, asumimos que ya está logueado
    try:
        if TEST_USER:
            # buscar botón que contenga el nombre de usuario
            elems = driver.find_elements(By.XPATH, f"//*[contains(normalize-space(.), '{TEST_USER}')]")
            for e in elems:
                # heurística: si está dentro del nav o header, consideramos que ya hay sesión
                ancestor = driver.execute_script("return arguments[0].closest('nav') || arguments[0].closest('header')", e)
                if ancestor:
                    print("[INFO] Ya hay sesión iniciada (usuario detectado en header).")
                    return
    except Exception:
        pass

    # no está autenticado -> ir a /accounts/login/ y loguear
    driver.get(BASE_URL.rstrip("/") + "/accounts/login/")
    _bypass_ngrok_if_needed(driver)
    wait = WebDriverWait(driver, 10)
    # localizar campos por id conocidos
    try:
        username = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        password = driver.find_element(By.ID, "id_password")
    except Exception:
        # intentos alternativos por name
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = driver.find_element(By.NAME, "password")

    username.clear()
    username.send_keys(TEST_USER)
    password.clear()
    password.send_keys(TEST_PASS)

    # buscar botón "Ingresar" o tipo submit
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
    except Exception:
        driver.find_element(By.CSS_SELECTOR, "form").submit()

    # esperar a que el header muestre el usuario o que no estemos en la página /accounts/login/
    WebDriverWait(driver, 10).until(lambda d: TEST_USER.lower() in d.page_source.lower() or "/accounts/login" not in d.current_url)


def test_logout_flow(driver):
    """
    - Asegura login con TEST_USER / TEST_PASS
    - Abre menú de usuario y pulsa 'Cerrar sesión'
    - Verifica que aparece 'Iniciar sesión' o que el nombre del usuario desaparece
    - Guarda screenshots
    """
    wait = open_page(driver, "/")
    _login_if_needed(driver, wait)

    # volver al home y capturar estado con sesión
    driver.get(BASE_URL.rstrip("/") + "/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    _ss(driver, "logout_before_click")

    # localizar el botón/dropdown del usuario y el link 'Cerrar sesión'
    logout_link = None

    # intentar localizar directamente el enlace de cerrar sesión si está visible
    try:
        logout_link = driver.find_element(By.CSS_SELECTOR, "a[href*='/salir/'], a[href*='/logout/'], a[href*='/accounts/logout/']")
    except Exception:
        logout_link = None

    # si no está visible, abrir el dropdown del usuario (botón que contiene el nombre de usuario o con clase dropdown-toggle)
    if not logout_link:
        try:
            # botón con el texto del usuario
            toggle = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(.,'{TEST_USER}')]"))
            )
            toggle.click()
        except Exception:
            try:
                toggle = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.dropdown button, button.dropdown-toggle"))
                )
                toggle.click()
            except Exception:
                print("[WARN] No se pudo abrir dropdown de usuario; intentaremos abrir por JS.")
                driver.execute_script("""
                    const b = Array.from(document.querySelectorAll('button, a'))
                      .find(e => (e.textContent||'').trim().toLowerCase().includes(arguments[0]));
                    if (b) { b.click(); }
                """, TEST_USER.lower())

        # esperar el enlace dentro del menú y localizarlo
        try:
            logout_link = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Cerrar sesión' or contains(normalize-space(.),'Cerrar sesión') or contains(.,'Cerrar sesión')]"))
            )
        except Exception:
            # alternativas por href
            try:
                logout_link = driver.find_element(By.CSS_SELECTOR, "a[href*='/salir/'], a[href*='/logout/'], a[href*='/cerrar/']")
            except Exception:
                logout_link = None

    assert logout_link is not None, "No se encontró el enlace 'Cerrar sesión' en el header."

    # click en cerrar sesión
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", logout_link)
        logout_link.click()
    except Exception:
        href = logout_link.get_attribute("href")
        assert href, "El enlace de cerrar sesión no tiene href y no fue clickeable."
        driver.get(href)

    # esperar que desaparezca el nombre del usuario o que aparezca 'Iniciar sesión'
    try:
        WebDriverWait(driver, 10).until(lambda d: TEST_USER.lower() not in d.page_source.lower() or "iniciar sesión" in d.page_source.lower())
    except Exception:
        pass

    _ss(driver, "logout_after_click")

    # validación final: que ya no aparezca el nombre del usuario en el header
    assert TEST_USER.lower() not in driver.page_source.lower(), "El usuario sigue presente en la página tras cerrar sesión."
    print("[✅] Logout ejecutado correctamente.")
