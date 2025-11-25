from django.contrib import admin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para Proveedores"""
    
    list_display = [
        'id',
        'razon_social',
        'nit',
        'telefono',
        'email',
        'estado',
        'created_at'
    ]
    
    list_filter = ['estado', 'created_at']
    
    search_fields = [
        'razon_social',
        'nit',
        'email',
        'telefono',
        'contacto_nombre'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('razon_social', 'nit', 'estado')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'contacto_nombre')
        }),
        ('Información Adicional', {
            'fields': ('notas',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
