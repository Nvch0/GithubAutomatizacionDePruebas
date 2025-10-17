# tests_e2e/test_categorias.py
import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


def _ss(driver, name):
    ts = time.strftime("%Y%m%d-%H%M%S")
    driver.save_screenshot(f"screenshots/{name}_{ts}.png")


def _bypass_ngrok_if_needed(driver):
    """
    Si aparece el interstitial de ngrok, hace clic en 'Visit Site' de forma robusta.
    Seguro de llamar en cualquier navegación.
    """
    try:
        # ¿Estamos en el interstitial? señales del DOM y/o título
        body = driver.find_element(By.TAG_NAME, "body")
        is_ngrok = ("ngrok" in (driver.title or "").lower()) or \
                   ("ngrok" in (body.get_attribute("id") or "").lower()) or \
                   ("ngrok" in (body.get_attribute("class") or "").lower()) or \
                   ("ngrok" in (driver.current_url or "").lower())

        if not is_ngrok:
            return

        wait = WebDriverWait(driver, 8)

        # 1) varios intentos con XPaths “por texto”
        candidates = [
            "//a[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='visit site']",
            "//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='visit site']",
            "//a[contains(@class,'btn') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'visit')]",
            "//button[contains(@class,'btn') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'visit')]",
        ]

        clicked = False
        for xp in candidates:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click()
                clicked = True
                break
            except Exception:
                pass

        # 2) si no funcionó, usa JS: busca el botón por texto y haz click
        if not clicked:
            driver.execute_script("""
                const btn = Array.from(document.querySelectorAll('a,button'))
                  .find(e => (e.textContent||'').trim().toLowerCase() === 'visit site');
                if (btn) btn.click();
            """)

        # 3) esperar a que deje de ser la página de ngrok
        WebDriverWait(driver, 10).until(lambda d: d.current_url.lower().startswith(BASE_URL.lower()))
    except Exception:
        # si algo falla, no interrumpimos; el siguiente paso de la prueba fallará con contexto útil
        pass



def _open(driver, path="/"):
    url = path if path.startswith("http") else f"{BASE_URL}{path}"
    driver.get(url)
    _bypass_ngrok_if_needed(driver)
    return WebDriverWait(driver, 12)


@pytest.fixture
def driver():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()


def test_menu_categorias_y_abrir_construccion(driver):
    """
    Flujo:
      - Abrir Home (saltando ngrok si aparece)
      - Abrir menú 'Categorias'
      - Seleccionar 'Construccion'
      - Validar que se muestra la página y hay productos
      - Mensaje final de éxito
    """
    wait = _open(driver, "/")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    _ss(driver, "cat_home")

    # 1) abrir menú Categorías
    menu = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Categorias")))
    menu.click()

    # 2) esperar offcanvas/título de Categorías
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(@class,'offcanvas') and .//*[contains(.,'Categor')]]")
        )
    )
    _ss(driver, "cat_offcanvas")

    # 3) elegir "Construccion"
    opcion = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Construccion']"))
    )
    opcion.click()

    # 4) validar que cargó la categoría y hay productos
    titulo = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h1[contains(.,'Categoria') or contains(.,'Categoría')]")
        )
    )
    assert "construccion" in titulo.text.lower()
    _ss(driver, "cat_construccion_titulo")

    # Presencia de tarjetas/productos (nombre/precio o botón añadir)
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'card') or .//button[contains(.,'Añadir al carro')]]")
            )
        )
    except Exception:
        _ss(driver, "cat_construccion_sin_productos")
        raise AssertionError("No se encontraron productos en la categoría 'Construccion'.")

    _ss(driver, "cat_construccion_ok")

    # 5) mensaje final de éxito para la consola
    print("✅ Prueba Categorías: se abrió 'Construccion' y se listaron productos correctamente.")
