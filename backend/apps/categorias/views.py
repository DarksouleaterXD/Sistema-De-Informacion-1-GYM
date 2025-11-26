"""
Views para Categorías de Productos
CRUD completo con filtros, búsqueda y paginación
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import CategoriaProducto
from .serializers import CategoriaProductoSerializer
from apps.audit.helpers import (
    registrar_creacion,
    registrar_actualizacion,
    registrar_eliminacion,
)


class CategoriaProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Categorías de Productos
    
    list: Listar todas las categorías
    create: Crear nueva categoría
    retrieve: Ver detalle de categoría
    update: Actualizar categoría completa
    partial_update: Actualizar campos específicos
    destroy: Eliminar categoría
    """
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'codigo', 'created_at']
    ordering = ['nombre']
    
    def perform_create(self, serializer):
        categoria = serializer.save()
        registrar_creacion(self.request, categoria, modulo="Categorías de Productos")
    
    def perform_update(self, serializer):
        categoria = serializer.save()
        registrar_actualizacion(self.request, categoria, modulo="Categorías de Productos")
    
    def perform_destroy(self, instance):
        registrar_eliminacion(self.request, instance, modulo="Categorías de Productos")
        instance.delete()

