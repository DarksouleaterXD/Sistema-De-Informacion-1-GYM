"""
Administración de Compras en Django Admin
"""
from django.contrib import admin
from .models import OrdenCompra, ItemOrdenCompra


class ItemOrdenCompraInline(admin.TabularInline):
    """Inline para ItemOrdenCompra en OrdenCompra"""
    model = ItemOrdenCompra
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal']


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['numero_orden', 'proveedor', 'fecha_orden', 'estado', 'total']
    list_filter = ['estado', 'fecha_orden']
    search_fields = ['numero_orden', 'proveedor__razon_social', 'proveedor__nit']
    readonly_fields = ['numero_orden', 'subtotal', 'total', 'fecha_orden', 'created_at', 'updated_at']
    ordering = ['-fecha_orden', '-created_at']
    inlines = [ItemOrdenCompraInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('numero_orden', 'proveedor', 'fecha_orden', 'fecha_esperada', 'estado', 'creado_por')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento', 'total')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemOrdenCompra)
class ItemOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['orden', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['orden__fecha_orden']
    search_fields = ['orden__numero_orden', 'producto__nombre']
    readonly_fields = ['subtotal', 'created_at', 'updated_at']

