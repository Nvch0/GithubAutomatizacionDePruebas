import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = os.getenv("BASE_URL", "/").rstrip("/") + "/"
USER = os.getenv("TEST_USER", "TEST03")
PWD  = os.getenv("TEST_PASS", "Nacho2002.")

PROD_ID   = "133"              # STATOFIX 100G
PROD_NAME = "STATOFIX 100G"

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
        print("[INFO] Intersticial ngrok omitido.")
    except Exception:
        pass

def _login(driver, wait):
    driver.get(BASE + "accounts/login/")
    _bypass_ngrok(driver)
    _ss(driver, "qty_login_page")
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
    _ss(driver, "qty_logged_in")

def _ensure_item_in_cart(driver):
    """Si no está el producto, lo agrega desde el home usando /carro/agregar/133."""
    driver.get(BASE)
    _bypass_ngrok(driver)

    # link "Añadir al carro" por href
    add_sel = (By.CSS_SELECTOR, "a[href*='/carro/agregar/133']")
    link = WebDriverWait(driver, 10).until(EC.presence_of_element_located(add_sel))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(add_sel)).click()
    except Exception:
        href = link.get_attribute("href")
        driver.get(href)

    # ir/esperar carrito
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
    _ss(driver, "qty_cart_with_item")

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

def _go_cart(driver):
    if "/carro" not in driver.current_url.lower():
        driver.get(BASE + "carro/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Carrito de Compras')]"))
    )

def _qty_input(driver):
    # input con id='cantidad-133'
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cantidad-133, input[id*='cantidad-133']"))
    )

def _btn_plus(driver):
    # botón + (hay dos maneras de enganchar)
    sel = (By.CSS_SELECTOR, "span.input-group-btn.btn_plus > button, button[onclick*='sumarProducto'][onclick*='133']")
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located(sel))

def _btn_minus(driver):
    sel = (By.CSS_SELECTOR, "span.input-group-btn.btn_minus > button, button[onclick*='restarProducto'][onclick*='133']")
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located(sel))

def _set_qty_by_clicks(driver, target):
    inp = _qty_input(driver)
    # Llevar la vista hacia el control de cantidad
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", inp)
    time.sleep(0.3)

    def current():
        try:
            return int(_qty_input(driver).get_attribute("value"))
        except Exception:
            return None

    # subir o bajar hasta target
    tries = 0
    while current() != target and tries < 20:
        tries += 1
        val = current()
        if val is None:
            time.sleep(0.2); continue
        if val < target:
            _btn_plus(driver).click()
        elif val > target:
            _btn_minus(driver).click()
        time.sleep(0.3)

    final = current()
    assert final == target, f"No se pudo ajustar la cantidad a {target}. Quedó en {final}."
    _ss(driver, f"qty_set_{target}")

def test_aumentar_y_restar_statofix(driver, open_page):
    """Agrega STATOFIX 100G, sube a 3 unidades, resta 2 y valida que quede en 1."""
    wait = open_page("/")
    _login(driver, wait)

    # Asegurar producto en el carrito
    _ensure_item_in_cart(driver)
    assert _product_present_in_cart(driver), "El producto STATOFIX 100G no está en el carrito."

    # Ir/asegurar página carrito
    _go_cart(driver)

    # 1) Subir cantidad hasta 3
    _set_qty_by_clicks(driver, 3)

    # 2) Restar dos (quedar en 1)
    _set_qty_by_clicks(driver, 1)

    # Validación final extra: que el texto “STATOFIX 100G x 1” (si existe) coincida
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'statofix 100g x 1')]")
            )
        )
    except Exception:
        # Si tu template no muestra “x 1”, basta con validar el input en 1
        pass

    # Evidencia final
    _ss(driver, "qty_final_ok")
    print("[✅] Ajuste de cantidad OK: 3 unidades, luego resta 2 => queda 1.")
