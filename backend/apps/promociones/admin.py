from django.contrib import admin
from apps.promociones.models import Promocion


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_descuento', 'valor_descuento', 'fecha_inicio', 'fecha_fin', 'activo', 'codigo']
    list_filter = ['activo', 'tipo_descuento', 'fecha_inicio', 'fecha_fin']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering = ['-created_at']
