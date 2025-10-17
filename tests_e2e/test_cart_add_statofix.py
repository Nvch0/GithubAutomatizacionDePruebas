# tests_e2e/test_cart_add_statofix.py
import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROD_ID = "133"                  # /carro/agregar/133
PROD_NAME = "STATOFIX 100G"

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    p = f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(p)
    print(f"[📸] {p}")

def _bypass_ngrok(driver):
    """Hace clic en 'Visit Site' si aparece el interstitial de ngrok."""
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'ngrok') and contains(.,'Visit Site')]"))
        )
        btn = driver.find_element(By.XPATH, "//a[normalize-space()='Visit Site']")
        driver.execute_script("arguments[0].click();", btn)
        print("[INFO] Intersticial de ngrok aceptado.")
    except Exception:
        pass

def _login(driver, wait, base="/"):
    """Login con TEST03 / Nacho2002. (o variables de entorno)"""
    user = os.getenv("TEST_USER", "TEST03")
    pwd  = os.getenv("TEST_PASS", "Nacho2002.")

    # Ir al login
    driver.get(f"{base}accounts/login/")
    _bypass_ngrok(driver)
    _ss(driver, "login_pantalla")

    # Completar y enviar
    username = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    password = wait.until(EC.presence_of_element_located((By.ID, "id_password")))
    username.clear(); username.send_keys(user)
    password.clear(); password.send_keys(pwd)

    # Botón submit
    btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@type='submit' or contains(@class,'btn-success')]")
    ))
    btn.click()

    # Confirmar login: aparece el nombre de usuario o se redirige al home
    WebDriverWait(driver, 10).until(
        EC.any_of(
            EC.url_contains("/"),
            EC.presence_of_element_located((By.XPATH, f"//*[contains(.,'{user}')]")),
        )
    )
    _ss(driver, "login_ok")
    print(f"[OK] Sesión iniciada como {user}.")

def _wait_cart_loaded(driver):
    return WebDriverWait(driver, 10).until(
        EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Carrito de Compras')]")),
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Resumen de compra')]")),
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Total:')]")),
        )
    )

def _product_present_in_cart(driver) -> bool:
    checks = [
        (By.XPATH, f"//*[contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{PROD_NAME}')]"),
        (By.XPATH, f"//*[contains(.,'Cód. Producto') and contains(.,'{PROD_ID}')]"),
        (By.XPATH, f"//*[contains(@class,'resumen') or contains(.,'Resumen')][contains(.,'{PROD_ID}') or contains(translate(.,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{PROD_NAME}')]"),
    ]
    for loc in checks:
        els = driver.find_elements(*loc)
        if any(e.is_displayed() for e in els):
            return True
    return False

def test_agregar_statofix_con_login(driver, open_page):
    # 1) Home
    wait = open_page("/")
    _bypass_ngrok(driver)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    _ss(driver, "home_cargado")

    # 2) Login (siempre, para asegurar autorización)
    _login(driver, wait, base=os.getenv("BASE_URL", "/"))

    # 3) Volver al home
    driver.get(os.getenv("BASE_URL", "/"))
    _bypass_ngrok(driver)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    _ss(driver, "home_post_login")

    # 4) Click al “Añadir al carro” del producto 133 (sin buscar)
    add_selector = (By.CSS_SELECTOR, "a[href*='/carro/agregar/133']")
    add_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(add_selector)
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_link)
    _ss(driver, "add_visible")

    href = add_link.get_attribute("href")
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(add_selector)).click()
    except Exception:
        assert href, "No se obtuvo href de 'Añadir al carro'."
        driver.get(href)

    # 5) Ir/esperar carrito
    try:
        WebDriverWait(driver, 6).until(lambda d: "/carro" in d.current_url.lower())
    except Exception:
        driver.get(os.getenv("BASE_URL", "/") + "carro/")

    _wait_cart_loaded(driver)
    _ss(driver, "carro_cargado")

    # 6) Validación
    assert _product_present_in_cart(driver), (
        f"No se encontró el producto en el carrito (nombre '{PROD_NAME}' o código {PROD_ID})."
    )
    print("[✅] Producto agregado y visible en el carrito.")
