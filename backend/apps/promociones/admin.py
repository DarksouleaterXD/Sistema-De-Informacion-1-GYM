from django.contrib import admin
from apps.promociones.models import Promocion


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Promocion según PUML
    """
    list_display = ['nombre', 'meses', 'descuento', 'fecha_inicio', 'fecha_fin', 'estado', 'esta_vigente']
    list_filter = ['estado', 'fecha_inicio', 'fecha_fin']
    search_fields = ['nombre']
    ordering = ['-fecha_inicio']
    readonly_fields = ['esta_vigente', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información de la Promoción', {
            'fields': ('nombre', 'meses', 'descuento')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'estado', 'esta_vigente')
        }),
        ('Fechas del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
