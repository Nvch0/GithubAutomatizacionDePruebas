# 🛒 Proyecto Django - Sistema de Carrito de Compras con API y WebPay (Transbank)

Este es un sistema completo de comercio electrónico desarrollado en **Django**, que permite a los usuarios explorar productos, añadirlos a un carrito, procesar pedidos y realizar pagos en línea mediante **WebPay (Transbank)**. Además, expone una API RESTful para facilitar la integración con otros sistemas o frontends modernos.

---

## 🚀 Funcionalidades Clave

### 🧾 Gestión de Productos y Pedidos
- CRUD de productos desde el panel administrativo o mediante la API.
- Sistema de pedidos con control de estado.

### 🛍️ Carrito de Compras Dinámico
- Añadir, eliminar o modificar productos.
- Actualización automática de totales y cantidades.

### 💳 Integración con WebPay (Transbank)
- Proceso de pago seguro con **WebPay Plus**.
- Generación de transacciones desde el backend.
- Confirmación y validación de pagos en tiempo real.
- Pruebas disponibles con tarjetas en modo sandbox.

### 🔐 Sistema de Autenticación
- Registro y login de usuarios.
- Protección de vistas para usuarios autenticados.

### 🌐 API RESTful
- Endpoints para productos, pedidos y usuarios.
- Serializadores y vistas compatibles con aplicaciones frontend (ej. React, Vue).

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4+, Django REST Framework
- **Base de Datos**: SQLite3 (puede escalarse a PostgreSQL)
- **Pagos**: WebPay Plus (Transbank)
- **Frontend**: HTML + CSS + JS
- **Entorno**: Python 3.x, dotenv, pytest

---

## 📂 Estructura del Proyecto

```
proyecto/
│
├── API/                   # Lógica de API REST
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── carro/                 # Módulo del carrito de compras
│   ├── carro.py           # Lógica de carrito en sesión
│   ├── models.py          # Modelos de productos/pedidos
│   ├── forms.py           # Formularios para checkout
│   ├── urls.py
│   └── tarjeta_pruebas.txt # Tarjetas WebPay de prueba
│
├── templates/             # Vistas HTML (si existen)
│
├── .env                   # Variables de entorno sensibles
├── requirements.txt       # Paquetes necesarios
├── pytest.ini             # Configuración de pruebas
├── db.sqlite3             # Base de datos local
├── manage.py              # Comando principal
└── README.md
```

---

## ⚙️ Instalación del Proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/Nvch0/IntegracionNuevoWebpay
cd proyecto-carro
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables en `.env`
Incluye tu configuración de Transbank:
```
TRANSBANK_COMMERCE_CODE=597030000000
TRANSBANK_API_KEY=...
TRANSBANK_ENVIRONMENT=TEST
```

### 4. Ejecutar migraciones y servidor
```bash
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Tarjetas de Prueba WebPay

Puedes usar las tarjetas de prueba que se encuentran en `carro/tarjeta_pruebas.txt` para realizar pruebas en entorno de desarrollo:

- Número: 4051885600446623
- Vencimiento: 12/29
- CVV: 123
- Rut: 11.111.111-1
- Clave: 123

---

## ✅ Ejecutar Pruebas

Este proyecto incluye pruebas automatizadas con `pytest`.

```bash
pytest
```

---

## 📦 API REST

Algunos endpoints disponibles:

| Método | Endpoint             | Descripción                      |
|--------|----------------------|----------------------------------|
| GET    | /api/productos/      | Listado de productos             |
| GET    | /api/pedidos/        | Pedidos realizados               |
| POST   | /api/pedidos/crear/  | Crear nuevo pedido               |

---

## 📬 Contacto

Para soporte o colaboración:
- 📧 Email: contacto@tusitio.cl
- 🌐 Sitio Web: [www.tusitio.cl](https://www.tusitio.cl)

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Puedes utilizarlo libremente para fines educativos o comerciales con la debida atribución.

---

**Desarrollado con ❤️ en Django + Transbank**
