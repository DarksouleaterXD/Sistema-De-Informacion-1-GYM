"""
Administración de Categorías de Productos en Django Admin
"""
from django.contrib import admin
from .models import CategoriaProducto


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'descripcion', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering = ['nombre']
    readonly_fields = ['created_at', 'updated_at']

