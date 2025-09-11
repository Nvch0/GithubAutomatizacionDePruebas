from django.urls import path, include
from .views import ProductoViewset, CategoriaViewset, MarcaViewset
from rest_framework import routers

router = routers.DefaultRouter()

router.register('producto',ProductoViewset)
router.register('categoria',CategoriaViewset)
router.register('marca',MarcaViewset)

#Urls de la API
urlpatterns = [
    path('', include(router.urls)),
]