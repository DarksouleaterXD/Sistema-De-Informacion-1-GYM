from django.contrib import admin
from .models import HistorialActividad


@admin.register(HistorialActividad)
class HistorialActividadAdmin(admin.ModelAdmin):
    """
    Admin para el modelo HistorialActividad
    """
    list_display = ('usuario', 'accion', 'fecha', 'hora', 'ip')
    list_filter = ('accion', 'fecha', 'usuario')
    search_fields = ('usuario__email', 'usuario__username', 'accion', 'ip')
    readonly_fields = ('usuario', 'accion', 'fecha', 'hora', 'ip', 'created_at', 'updated_at')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', '-hora')
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros de auditoría"""
        return False
    
    fieldsets = (
        ('Información de la Actividad', {
            'fields': ('usuario', 'accion', 'fecha', 'hora', 'ip')
        }),
        ('Fechas de Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
