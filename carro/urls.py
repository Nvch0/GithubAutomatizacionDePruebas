from django.urls import path
from . import views

app_name = "carro"

urlpatterns = [

    path('', views.vista_carro, name='carro'),
    path('agregar/<int:producto_id>',views.agregar_producto, name='agregar'),
    path('confirmar-direccion/', views.confirmar_direccion, name='confirmar_direccion'),
    path('cambiar_direccion/', views.cambiar_direccion, name='cambiar_direccion'),

    path('sumar_producto/<int:producto_id>/',views.sumar_producto, name='sumar_producto'),
    path('eliminar/<int:producto_id>/',views.eliminar_producto, name='eliminar'),
    path('restar/<int:producto_id>',views.restar_producto, name='restar'),
    path('limpiar/',views.limpiar_carro, name='limpiar'),
    path('mis_compras/', views.mis_compras, name='mis_compras'),



    path('retorno/', views.webpay_retorno, name='webpay_retorno'),
]