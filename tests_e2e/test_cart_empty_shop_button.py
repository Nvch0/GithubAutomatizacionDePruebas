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


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
TEST_USER = os.getenv("TEST_USER", "TEST03")
TEST_PASS = os.getenv("TEST_PASS", "Nacho2002.")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"


def _open(driver, path="/"):
    """Abre la ruta indicada y maneja la pantalla de ngrok 'Visit Site'."""
    driver.get(BASE_URL + path)
    wait = WebDriverWait(driver, 12)
    try:
        visit_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Visit Site')]"))
        )
        visit_btn.click()
    except Exception:
        pass
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return wait


def _login_if_needed(driver, wait):
    """Inicia sesión con TEST_USER y TEST_PASS si no está logueado."""
    if TEST_USER.lower() in driver.page_source.lower():
        return
    _open(driver, "/accounts/login/")
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(TEST_USER)
    driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
    driver.find_element(By.XPATH, "//button[contains(.,'Ingresar')]").click()
    WebDriverWait(driver, 15).until(lambda d: TEST_USER.lower() in d.page_source.lower())


def _vaciar_carro_si_hay(driver, wait):
    """Si el carro tiene productos, hace click en 'Vaciar carro'."""
    try:
        vaciar = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Vaciar carro')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", vaciar)
        time.sleep(0.2)
        vaciar.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(.,'Su carro de compras esta vacio')]")
            )
        )
    except Exception:
        pass


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
    try:
        drv.quit()
    except Exception:
        pass


def test_boton_comprar_en_ferremas_con_login(driver):
    """
    Dado que el usuario está logueado y su carro está vacío,
    cuando hace clic en 'Comprar en ferremas.cl',
    entonces debe ser redirigido correctamente al Home (/).
    """
    wait = _open(driver, "/")
    _login_if_needed(driver, wait)

    # Ir al carro
    _open(driver, "/carro/")

    # Vaciar carro si tiene productos
    _vaciar_carro_si_hay(driver, wait)

    # Verificar mensaje y el botón
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(.,'Su carro de compras esta vacio')]")
        )
    )

    boton = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'btn-outline-secondary') and contains(.,'Comprar en ferremas.cl')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
    time.sleep(0.3)
    boton.click()

    # Esperar redirección al Home
    WebDriverWait(driver, 12).until(lambda d: d.current_url.rstrip("/").lower() == BASE_URL.lower())

    print("✅ Test correcto: el botón 'Comprar en ferremas.cl' redirige al Home estando logueado.")
