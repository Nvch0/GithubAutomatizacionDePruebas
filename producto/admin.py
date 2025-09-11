from django.contrib import admin
from .models import Producto, Categoria, Marca ,Pedido

# Register your models here.

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Marca)
admin.site.register(Pedido)

