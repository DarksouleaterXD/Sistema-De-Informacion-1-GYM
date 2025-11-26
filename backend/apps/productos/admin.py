"""
Administración de Productos en Django Admin
"""
from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'codigo', 
        'categoria', 
        'proveedor',
        'precio', 
        'stock', 
        'stock_minimo',
        'estado',
        'created_at'
    ]
    list_filter = ['estado', 'categoria', 'proveedor', 'created_at']
    search_fields = ['nombre', 'codigo', 'descripcion']
    autocomplete_fields = ['categoria', 'proveedor', 'promocion']
    readonly_fields = ['created_at', 'updated_at', 'creado_por', 'modificado_por']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'categoria', 'descripcion', 'imagen')
        }),
        ('Proveedor y Precio', {
            'fields': ('proveedor', 'precio', 'costo')
        }),
        ('Inventario', {
            'fields': ('stock', 'stock_minimo', 'unidad_medida')
        }),
        ('Promoción y Estado', {
            'fields': ('promocion', 'estado')
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'modificado_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        obj.modificado_por = request.user
        super().save_model(request, obj, form, change)
