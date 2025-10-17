# tests_e2e/test_cart_empty.py
import os, time, re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = os.getenv("BASE_URL", "/").rstrip("/") + "/"
USER = os.getenv("TEST_USER", "TEST03")
PWD  = os.getenv("TEST_PASS", "Nacho2002.")
PROD_ID   = "133"              # /carro/agregar/133
PROD_NAME = "STATOFIX 100G"    # texto visible del producto
EMPTY_MSG = "su carro de compras esta vacio"  # tal como aparece en pantalla

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    p = f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(p)
    print(f"[📸] {p}")

def _bypass_ngrok(driver):
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//*[self::a or self::button][contains(.,'Visit Site')]"))
        )
        btn.click()
        print("[INFO] Intersticial de ngrok aceptado.")
    except Exception:
        pass

def _login(driver, wait):
    driver.get(BASE + "accounts/login/")
    _bypass_ngrok(driver)
    _ss(driver, "empty_login_page")
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
    _ss(driver, "empty_logged_in")

def _ensure_item_in_cart(driver):
    driver.get(BASE)
    _bypass_ngrok(driver)
    add_sel = (By.CSS_SELECTOR, "a[href*='/carro/agregar/133']")
    link = WebDriverWait(driver, 10).until(EC.presence_of_element_located(add_sel))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(add_sel)).click()
    except Exception:
        href = link.get_attribute("href")
        driver.get(href)

    # Ir/esperar carrito
    try:
        WebDriverWait(driver, 6).until(lambda d: "/carro" in d.current_url.lower())
    except Exception:
        driver.get(BASE + "carro/")
    WebDriverWait(driver, 10).until(
        EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Carrito de Compras')]")),
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Resumen de compra')]")),
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Total:')]")),
        )
    )
    _ss(driver, "empty_cart_with_item")

def _product_present_in_cart(driver) -> bool:
    checks = [
        (By.XPATH, f"//*[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{PROD_NAME}')]"),
        (By.XPATH, f"//*[contains(.,'Cód. Producto') and contains(.,'{PROD_ID}')]"),
    ]
    for loc in checks:
        els = driver.find_elements(*loc)
        if any(e.is_displayed() for e in els):
            return True
    return False

def _click_vaciar_carro(driver):
    vaciar_sel = (By.CSS_SELECTOR, "a[href*='/carro/limpiar']")
    btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(vaciar_sel))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    _ss(driver, "empty_vaciar_visible")
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(vaciar_sel)).click()
    except Exception:
        href = btn.get_attribute("href")
        assert href, "No se pudo hacer clic ni obtener href del botón 'Vaciar carro'."
        driver.get(href)

def test_vaciar_carro_completamente(driver, open_page):
    # 1) Login
    wait = open_page("/")
    _login(driver, wait)

    # 2) Asegurar que haya un producto en el carrito
    _ensure_item_in_cart(driver)
    assert _product_present_in_cart(driver), "El producto no está en el carrito (precondición)."

    # 3) Vaciar carrito
    _click_vaciar_carro(driver)

    # 4) Volver/esperar carrito cargado después de limpiar
    try:
        WebDriverWait(driver, 6).until(lambda d: "/carro" in d.current_url.lower())
    except Exception:
        driver.get(BASE + "carro/")

    # ⬇⬇ NUEVO: esperar explícitamente el mensaje “Su carro de compras esta vacio”
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(translate(normalize-space(.),"
                       "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                       f"'{EMPTY_MSG}')]")
        )
    )
    _ss(driver, "empty_cart_after_clean")

    # 5) Validaciones finales
    assert not _product_present_in_cart(driver), "El producto aún aparece tras 'Vaciar carro'."
    assert EMPTY_MSG in driver.page_source.lower(), \
        f"No se encontró el mensaje esperado: '{EMPTY_MSG}'"

    print("[✅] Carro vaciado correctamente y mensaje de vacío mostrado.")
