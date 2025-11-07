from django.contrib import admin
from .models import Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'nombre_completo', 'email', 'especialidades', 
        'experiencia_anos', 'activo', 'created_at'
    ]
    list_filter = ['activo', 'experiencia_anos', 'created_at']
    search_fields = [
        'usuario__first_name', 'usuario__last_name', 
        'usuario__email', 'especialidades'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario',)
        }),
        ('Información Profesional', {
            'fields': (
                'especialidades', 'certificaciones', 
                'experiencia_anos', 'biografia'
            )
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'telefono_emergencia')
        }),
        ('Otros', {
            'fields': ('foto_url', 'activo', 'fecha_ingreso')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
