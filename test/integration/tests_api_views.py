import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from producto.models import Producto, Categoria, Marca

# Fixture para crear un usuario
@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    return user

# Fixture para el cliente autenticado
@pytest.fixture
def auth_client(user):
    client = APIClient()
    response = client.post('/api/token/', {'username': 'testuser', 'password': 'testpass'})
    access_token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    return client

# Fixture para crear una categoría
@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre='Herramientas')

# Fixture para crear una categoría
@pytest.fixture
def marca(db):
    return Marca.objects.create(nombre='Generica')

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

# Pruebas para ProductoViewset
@pytest.mark.django_db
def test_get_lista_productos(auth_client, producto):
    response = auth_client.get('/api/producto/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['nombre'] == 'Taladro'

@pytest.mark.django_db
def test_get_detalle_producto(auth_client, producto):
    response = auth_client.get(f'/api/producto/{producto.id}/')
    assert response.status_code == 200
    assert response.data['nombre'] == 'Taladro'

@pytest.mark.django_db
def test_post_crear_producto(auth_client, categoria, marca):
    data = {
        'nombre': 'Martillo',
        'precio': 50.00,
        'descripcion': 'Un martillo resistente',
        'categoria': categoria.id,
        'marca':marca.id,
        'stock': 15
    }
    response = auth_client.post('/api/producto/', data)
    assert response.status_code == 201
    assert response.data['nombre'] == 'Martillo'

@pytest.mark.django_db
def test_put_actualizar_producto(auth_client, producto):
    data = {
        'nombre': 'Taladro Inalámbrico',
        'precio': 150.00,
        'descripcion': 'Un taladro potente y sin cables',
        'categoria': producto.categoria.id,
        'marca': producto.marca.id,
        'stock': 5
    }
    response = auth_client.put(f'/api/producto/{producto.id}/', data)
    assert response.status_code == 200
    assert response.data['nombre'] == 'Taladro Inalámbrico'

@pytest.mark.django_db
def test_delete_eliminar_producto(auth_client, producto):
    response = auth_client.delete(f'/api/producto/{producto.id}/')
    assert response.status_code == 204
    assert Producto.objects.count() == 0

# Pruebas para CategoriaViewset
@pytest.mark.django_db
def test_get_lista_categorias(auth_client, categoria):
    response = auth_client.get('/api/categoria/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['nombre'] == 'Herramientas'

@pytest.mark.django_db
def test_get_detalle_categoria(auth_client, categoria):
    response = auth_client.get(f'/api/categoria/{categoria.id}/')
    assert response.status_code == 200
    assert response.data['nombre'] == 'Herramientas'

@pytest.mark.django_db
def test_post_crear_categoria(auth_client):
    data = {'nombre': 'Electrodomésticos'}
    response = auth_client.post('/api/categoria/', data)
    assert response.status_code == 201
    assert response.data['nombre'] == 'Electrodomésticos'

@pytest.mark.django_db
def test_put_actualizar_categoria(auth_client, categoria):
    data = {'nombre': 'Herramientas de Jardín'}
    response = auth_client.put(f'/api/categoria/{categoria.id}/', data)
    assert response.status_code == 200
    assert response.data['nombre'] == 'Herramientas de Jardín'

@pytest.mark.django_db
def test_delete_eliminar_categoria(auth_client, categoria):
    response = auth_client.delete(f'/api/categoria/{categoria.id}/')
    assert response.status_code == 204
    assert Categoria.objects.count() == 0

# Pruebas para MarcaViewset
@pytest.mark.django_db
def test_get_lista_marca(auth_client, marca):
    response = auth_client.get('/api/marca/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['nombre'] == 'Generica'

@pytest.mark.django_db
def test_get_detalle_marca(auth_client, marca):
    response = auth_client.get(f'/api/marca/{marca.id}/')
    assert response.status_code == 200
    assert response.data['nombre'] == 'Generica'

@pytest.mark.django_db
def test_post_crear_marca(auth_client):
    data = {'nombre': 'Bush'}
    response = auth_client.post('/api/marca/', data)
    assert response.status_code == 201
    assert response.data['nombre'] == 'Bush'

@pytest.mark.django_db
def test_put_actualizar_marca(auth_client, marca):
    data = {'nombre': 'Bush'}
    response = auth_client.put(f'/api/marca/{marca.id}/', data)
    assert response.status_code == 200
    assert response.data['nombre'] == 'Bush'

@pytest.mark.django_db
def test_delete_eliminar_marca(auth_client, marca):
    response = auth_client.delete(f'/api/marca/{marca.id}/')
    assert response.status_code == 204
    assert Marca.objects.count() == 0
