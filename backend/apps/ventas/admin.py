"""
Administración de Ventas en Django Admin
"""
from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    """Inline para DetalleVenta en Venta"""
    model = DetalleVenta
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['numero_venta', 'cliente', 'fecha_venta', 'estado', 'total', 'metodo_pago']
    list_filter = ['estado', 'metodo_pago', 'fecha_venta']
    search_fields = ['numero_venta', 'cliente__nombre', 'cliente__apellido', 'cliente__ci']
    readonly_fields = ['numero_venta', 'subtotal', 'total', 'fecha_venta', 'created_at', 'updated_at']
    ordering = ['-fecha_venta', '-created_at']
    inlines = [DetalleVentaInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('numero_venta', 'cliente', 'fecha_venta', 'estado', 'vendedor')
        }),
        ('Pago', {
            'fields': ('metodo_pago', 'subtotal', 'descuento', 'total')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha_venta']
    search_fields = ['venta__numero_venta', 'producto__nombre']
    readonly_fields = ['subtotal', 'created_at', 'updated_at']

