import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

def _click_ngrok_visit_if_present(driver):
    """Si aparece el splash de ngrok, hace click en 'Visit Site'."""
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        if "ngrok" in driver.page_source.lower() and "visit site" in driver.page_source.lower():
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Visit Site']|//button[normalize-space()='Visit Site']"))
            )
            btn.click()
            WebDriverWait(driver, 10).until(lambda d: BASE_URL in d.current_url or "/home" in d.current_url or "ngrok" not in d.page_source.lower())
    except Exception:
        pass

def _open_home(driver):
    driver.get(BASE_URL + "/")
    _click_ngrok_visit_if_present(driver)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "nav")))

@pytest.fixture
def driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    yield drv
    drv.quit()

def test_categoria_herramientas_manuales(driver):
    """
    Flujo:
      - Abrir home (superando splash de ngrok si aparece)
      - Abrir menú 'Categorias'
      - Clic en 'Herramientas Manuales'
      - Verificar que el h1 muestre 'Categoria: Herramientas Manuales'
      - Finalizar
    """
    _open_home(driver)

    # Abrir el offcanvas de Categorías
    categorias = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Categorias"))
    )
    categorias.click()

    # Esperar offcanvas visible y hacer click a la opción
    link_herr = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Herramientas Manuales']"))
    )
    link_herr.click()

    # Verificar el título de categoría
    h1 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[contains(.,'Categoria:') and contains(.,'Herramientas Manuales')]"))
    )

    # (opcional) captura para evidencia
    driver.save_screenshot("screenshots/categoria_herramientas_manuales.png")

    # Si llegó aquí, la prueba se considera correcta
    assert "Herramientas Manuales" in h1.text
