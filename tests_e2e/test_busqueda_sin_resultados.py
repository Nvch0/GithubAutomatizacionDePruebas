# tests_e2e/test_busqueda_sin_resultados.py
import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _ss(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(path)
    print(f"[📸] {path}")

def test_busqueda_sin_resultados(driver, open_page):
    """
    Caso: búsqueda sin resultados.
    - Abre el home
    - Busca 'martillo pesado'
    - Valida que no haya tarjetas de producto y/o se muestre mensaje de 'sin resultados'
    """
    QUERY = "martillo pesado"

    # 1) Home (bypass de ngrok incluido en open_page)
    wait = open_page("/")

    # 2) Input de búsqueda por name='buscar'
    inp = wait.until(EC.presence_of_element_located((By.NAME, "buscar")))
    inp.clear()
    inp.send_keys(QUERY)
    inp.send_keys(Keys.ENTER)
    _ss(driver, "busqueda_sin_resultados_enviada")

    # 3) Esperar cambio de URL o actualización
    current = driver.current_url
    try:
        WebDriverWait(driver, 10).until(EC.url_changes(current))
    except Exception:
        pass  # algunas apps actualizan por AJAX sin cambiar URL

    # 4) Revisar si aparecen tarjetas de producto (varios selectores por robustez)
    posibles_cards = [
        (By.CSS_SELECTOR, ".card.product, .product.card, .producto.card"),
        (By.CSS_SELECTOR, ".card"),  # fallback general
        (By.XPATH, "//*[contains(@class,'product') or contains(@class,'producto')]"),
    ]
    cards = []
    for loc in posibles_cards:
        elems = driver.find_elements(*loc)
        if elems:
            cards = [e for e in elems if e.is_displayed()]
            if cards:
                break

    # 5) Intentar detectar mensaje de 'sin resultados'
    posibles_msgs = [
        (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sin resultados')]"),
        (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no se encontraron')]"),
        (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no hay productos')]"),
        (By.CSS_SELECTOR, ".alert, .empty, .no-results, .not-found"),
    ]
    msg_visible = any(driver.find_elements(*loc) for loc in posibles_msgs)

    _ss(driver, "busqueda_sin_resultados_resultado")

    # 6) Validaciones
    # Aceptamos como OK:
    #   - No hay tarjetas visibles  (len==0)
    #   - O hay mensaje de 'sin resultados'
    assert (len(cards) == 0) or msg_visible, (
        f"Se encontraron tarjetas de producto ({len(cards)}) para una búsqueda sin resultados."
    )

    print("[✅] Búsqueda negativa OK: 'martillo pesado' no devuelve productos.")
