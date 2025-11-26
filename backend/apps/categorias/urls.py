"""
URLs para Categorías de Productos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaProductoViewSet

router = DefaultRouter()
router.register(
    r'categorias-producto',
    CategoriaProductoViewSet,
    basename='categoria-producto'
)

urlpatterns = [
    path('', include(router.urls)),
]

