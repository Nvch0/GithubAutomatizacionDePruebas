# tests_e2e/test_busqueda_exitosa.py
import os
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _ss(driver, nombre):
    """Guarda capturas en la carpeta screenshots."""
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{nombre}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    driver.save_screenshot(path)
    print(f"[📸] Screenshot guardado: {path}")


def test_busqueda_exitosa_statofix(driver, open_page):
    """
    Caso de prueba: búsqueda exitosa en la barra de búsqueda
    Flujo:
      - Abre el home
      - Ingresa 'statofix 100g' en la barra de búsqueda
      - Presiona Enter o el botón de buscar
      - Valida que se muestre un producto con el texto 'STATOFIX 100G'
    """
    BUSQUEDA = "statofix 100g"

    # 1️⃣ Abrir página principal
    wait = open_page("/")

    # 2️⃣ Buscar campo de búsqueda por name='buscar'
    input_busqueda = wait.until(EC.presence_of_element_located((By.NAME, "buscar")))
    input_busqueda.clear()
    input_busqueda.send_keys(BUSQUEDA)

    # 3️⃣ Presionar Enter para realizar la búsqueda
    input_busqueda.send_keys(Keys.ENTER)
    print(f"[INFO] Se ingresó la búsqueda: {BUSQUEDA}")
    _ss(driver, "busqueda_enviada")

    # 4️⃣ Esperar a que aparezca algún producto en los resultados
    producto = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'statofix')]"))
    )
    _ss(driver, "busqueda_resultados")

    # 5️⃣ Validar que el producto contenga 'STATOFIX 100G'
    assert "statofix" in producto.text.lower(), "El resultado no contiene el texto esperado 'statofix'."

    print("[✅] Prueba exitosa: el producto 'STATOFIX 100G' fue encontrado correctamente.")
