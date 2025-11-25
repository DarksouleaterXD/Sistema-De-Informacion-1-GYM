"""
URLs para Productos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaProductoViewSet, ProductoViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet, basename='categoria-producto')
router.register(r'productos', ProductoViewSet, basename='producto')

urlpatterns = [
    path('', include(router.urls)),
]
