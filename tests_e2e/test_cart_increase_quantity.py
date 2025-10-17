import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROD_ID = "133"
PROD_NAME = "STATOFIX 100G"

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    p = f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(p)
    print(f"[📸] {p}")

def _get_qty(driver):
    """Obtiene el valor actual del input de cantidad"""
    qty_input = driver.find_element(By.ID, f"cantidad-{PROD_ID}")
    return int(qty_input.get_attribute("value"))

def test_aumentar_cantidad_producto(driver, open_page, login_as_test_user):
    """
    Flujo:
      - Login con TEST03
      - Abrir /carro/
      - Aumentar cantidad del producto STATOFIX 100G (id 133)
      - Validar que la cantidad haya aumentado
    """
    # 1) Login
    assert login_as_test_user()

    # 2) Ir al carrito
    wait = open_page("/carro/")
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Carrito de Compras')]")))
    _ss(driver, "carrito_abierto")

    # 3) Obtener cantidad actual
    qty_before = _get_qty(driver)
    print(f"[INFO] Cantidad inicial: {qty_before}")

    # 4) Click en el botón "+"
    plus_btn = driver.find_element(By.CSS_SELECTOR, f"#producto-{PROD_ID} .btn_plus")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", plus_btn)
    time.sleep(0.5)
    plus_btn.click()
    _ss(driver, "click_plus")

    # 5) Esperar que el valor cambie
    WebDriverWait(driver, 10).until(
        lambda d: _get_qty(d) > qty_before
    )

    qty_after = _get_qty(driver)
    print(f"[INFO] Cantidad final: {qty_after}")
    _ss(driver, "cantidad_actualizada")

    assert qty_after == qty_before + 1, \
        f"La cantidad no aumentó correctamente: antes={qty_before}, después={qty_after}"

    print("[✅] Prueba exitosa: cantidad aumentada correctamente.")
