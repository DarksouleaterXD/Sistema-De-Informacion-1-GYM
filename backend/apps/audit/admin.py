from django.contrib import admin
from .models import HistorialActividad


@admin.register(HistorialActividad)
class HistorialActividadAdmin(admin.ModelAdmin):
    """
    Admin para el modelo HistorialActividad (Bitácora del Sistema)
    """
    list_display = (
        'usuario_display', 
        'tipo_accion_display', 
        'accion', 
        'nivel_badge', 
        'fecha_hora_display', 
        'ip_address'
    )
    list_filter = (
        'tipo_accion', 
        'nivel', 
        'fecha_hora',
        ('usuario', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'usuario__email', 
        'usuario__username', 
        'accion', 
        'descripcion',
        'ip_address'
    )
    readonly_fields = (
        'usuario', 
        'tipo_accion', 
        'accion', 
        'descripcion',
        'nivel',
        'ip_address', 
        'user_agent',
        'fecha_hora',
        'datos_adicionales',
        'created_at', 
        'updated_at'
    )
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
    
    # Configuración de visualización
    list_per_page = 50
    list_max_show_all = 200
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar registros de auditoría"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros de auditoría"""
        return request.user.is_superuser  # Solo superusuario puede eliminar
    
    # Métodos personalizados para list_display
    def usuario_display(self, obj):
        """Mostrar usuario o Sistema si es None"""
        if obj.usuario:
            return f"{obj.usuario.username} ({obj.usuario.email})"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def tipo_accion_display(self, obj):
        """Mostrar tipo de acción con etiqueta legible"""
        return dict(HistorialActividad.TIPO_ACCION_CHOICES).get(obj.tipo_accion, obj.tipo_accion)
    tipo_accion_display.short_description = "Tipo"
    
    def nivel_badge(self, obj):
        """Mostrar nivel con colores"""
        colores = {
            'info': '#007bff',      # Azul
            'warning': '#ffc107',   # Amarillo
            'error': '#dc3545',     # Rojo
            'critical': '#6f42c1',  # Púrpura
        }
        color = colores.get(obj.nivel, '#6c757d')
        return f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{obj.nivel.upper()}</span>'
    nivel_badge.short_description = "Nivel"
    nivel_badge.allow_tags = True
    
    def fecha_hora_display(self, obj):
        """Formato de fecha y hora más legible"""
        return obj.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')
    fecha_hora_display.short_description = "Fecha y Hora"
    fecha_hora_display.admin_order_field = 'fecha_hora'
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'ip_address', 'user_agent')
        }),
        ('Detalles de la Acción', {
            'fields': ('tipo_accion', 'accion', 'descripcion', 'nivel')
        }),
        ('Datos Adicionales', {
            'fields': ('datos_adicionales',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('fecha_hora', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
