# tests_e2e/test_click_logo_home.py
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
    """Guarda screenshot con timestamp y devuelve la ruta."""
    _ensure_screenshots_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fname = f"{name}_{ts}.png"
    path = os.path.join(SCREENSHOTS_DIR, fname)
    driver.save_screenshot(path)
    print(f"[📸] Screenshot guardado: {path}")
    return path


def _bypass_ngrok_if_needed(driver):
    """
    Si aparece el interstitial de ngrok, intenta pulsar 'Visit Site'.
    No lanza excepción en caso de fallo (se registrará y el test fallará luego si es necesario).
    """
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        # heurística simple para detectar interstitial ngrok
        is_ngrok = (
            "ngrok" in (driver.title or "").lower()
            or "ngrok" in (driver.current_url or "").lower()
            or "You are about to visit" in driver.page_source[:500]
        )
        if not is_ngrok:
            return

        print("[INFO] Interstitial de ngrok detectado; intentando pulsar 'Visit Site'…")
        wait = WebDriverWait(driver, 6)

        # probar varios selectores/xpaths posibles
        xpaths = [
            "//a[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='visit site']",
            "//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='visit site']",
            "//a[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'visit site')]",
            "//a[contains(@href,'ngrok') and contains(.,'Visit Site')]",
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
            # intento por JS buscando texto exactamente 'Visit Site'
            driver.execute_script("""
                const btn = Array.from(document.querySelectorAll('a,button'))
                  .find(e => (e.textContent||'').trim().toLowerCase() === 'visit site');
                if (btn) btn.click();
            """)
        # dar tiempo y comprobar que estamos en la URL real del site
        WebDriverWait(driver, 10).until(lambda d: d.current_url and not d.current_url.lower().startswith("https://ngrok.com"))
    except Exception as e:
        print("[WARN] No se pudo completar bypass de ngrok:", e)


def open_page(driver, path="/"):
    """Abre BASE_URL + path y aplica bypass si aparece ngrok, devuelve WebDriverWait."""
    url = BASE_URL.rstrip("/") + "/" + path.lstrip("/")
    driver.get(url)
    time.sleep(0.4)
    _bypass_ngrok_if_needed(driver)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return WebDriverWait(driver, 10)


def test_click_logo_vuelve_home(driver):
    """
    - Abre /contacto/
    - Saca screenshot de la pagina antes del click
    - Hace click en el logo (a.navbar-brand o img dentro)
    - Espera la navegación al home y saca screenshot final
    """
    wait = open_page(driver, "/contacto/")
    _ss(driver, "before_click_contacto")

    # buscar el logo anchor (<a class="navbar-brand" href="/">)
    logo = None
    try:
        # primero intentar anchor clickable
        logo = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.navbar-brand")))
    except Exception:
        # intentar la imagen dentro del anchor
        try:
            logo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.navbar-brand img")))
        except Exception:
            # fallback: buscar por href='/'
            logo = driver.find_element(By.CSS_SELECTOR, "a[href='/']")

    # Si el elemento es imagen, hacer click en su anchor padre
    tag = logo.tag_name.lower()
    if tag == "img":
        parent = driver.execute_script("return arguments[0].closest('a')", logo)
        if parent:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", parent)
            parent.click()
        else:
            logo.click()
    else:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", logo)
        logo.click()

    # esperar navegación al home
    WebDriverWait(driver, 12).until(lambda d: d.current_url.rstrip("/").lower() == BASE_URL.rstrip("/").lower())
    _ss(driver, "after_click_home")

    assert driver.current_url.rstrip("/").lower() == BASE_URL.rstrip("/").lower(), "No se redirigió al home al hacer click en el logo."
    print("[✅] Click en logo navegó al home correctamente.")
