from django.shortcuts import render
from .models import Categoria, Producto

# Create your views here.

def productos(request, id):

    categoria_id = id
    productos = Producto.objects.filter(categoria_id=categoria_id)

    categoria = Categoria.objects.filter(id = categoria_id)

    data = {
        'productos':productos,
        'categoria': categoria
    }

    return render(request,'categoria/producto.html', data)

def detalle_producto(request,id):

    producto_id = id
    producto = Producto.objects.filter(id=producto_id)
    categoria = Categoria.objects.all()

    data = {

        'producto':producto,
        'categoria':categoria
    }

    return render(request, 'unitario/detalle_producto.html', data)

