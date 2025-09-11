import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from producto.models import Producto, Categoria, Marca

# Fixture para crear un usuario
@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    return user

# Fixture para el cliente autenticado
@pytest.fixture
def client(user):
    client = Client()
    client.login(username='testuser', password='testpass')
    return client

# Fixture para crear una categoría
@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre='Herramientas')

# Fixture para crear una marca
@pytest.fixture
def marca(db):
    return Marca.objects.create(nombre='Herramientas')

# Fixture para crear un producto
@pytest.fixture
def producto(categoria, db, marca):
    return Producto.objects.create(
        nombre='Taladro',
        precio=100.00,
        descripcion='Un taladro potente',
        categoria=categoria,
        marca = marca,
        stock=10
    )

# Pruebas para productos
@pytest.mark.django_db
def test_get_productos_por_categoria(client, categoria, producto):
    response = client.get(reverse('producto:categoria', args=[categoria.id]))
    assert response.status_code == 200
    assert 'Taladro' in response.content.decode()

# Pruebas para detalle_producto
@pytest.mark.django_db
def test_get_detalle_producto(client, producto):
    response = client.get(reverse('producto:detalle_producto', args=[producto.id]))
    assert response.status_code == 200
    assert 'Taladro' in response.content.decode()
