import pytest
from django.http import HttpRequest
from django.contrib.sessions.middleware import SessionMiddleware
from producto.models import Producto, Categoria, Marca
from carro.carro import Carro

@pytest.fixture
def http_request():
    request = HttpRequest()
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request

@pytest.fixture
def categoria():
    return Categoria.objects.create(nombre='Herramientas')

@pytest.fixture
def marca():
    return Marca.objects.create(nombre='Generica')

@pytest.fixture
def producto(categoria, marca):
    return Producto.objects.create(
        id = 1,
        nombre='Taladro',
        precio=100.00,
        descripcion='Un taladro potente',
        marca = marca,
        categoria=categoria,
        stock=10
    )

@pytest.fixture
def carro(http_request):
    return Carro(http_request)

@pytest.mark.django_db
def test_agregar_producto(carro, producto):
    carro.agregar(producto)
    assert producto.id in carro.carro
    assert carro.carro[producto.id]['cantidad'] == 1 ##OK

@pytest.mark.django_db
def test_agregar_mismo_producto(carro, producto):  #NOK
    carro.agregar(producto)
    carro.agregar(producto)
    assert producto.id in carro.carro
    assert carro.carro[producto.id]['cantidad'] == 1

@pytest.mark.django_db
def test_restar_producto(carro, producto):
    carro.agregar(producto)
    carro.agregar(producto)
    carro.restar_producto(producto)
    assert producto.id in carro.carro
    assert carro.carro[producto.id]['cantidad'] == 1

@pytest.mark.django_db
def test_restar_producto_hasta_eliminar(carro, producto): #OKNOTDATA
    carro.agregar(producto)
    carro.restar_producto(producto)
    carro.restar_producto(producto)
    assert str(producto.id) not in carro.carro

@pytest.mark.django_db
def test_eliminar_producto(carro, producto):
    carro.agregar(producto)
    carro.eliminar(producto)
    assert str(producto.id) not in carro.carro

# @pytest.mark.django_db
# def test_limpiar_carro(carro, producto):
#     carro.agregar(producto)
#     carro.limpiar_carro()
#     assert carro.carro == {}