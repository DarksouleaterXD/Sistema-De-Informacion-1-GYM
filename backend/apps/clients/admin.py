from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Client
    """
    list_display = ('nombre', 'apellido', 'ci', 'telefono', 'experiencia', 'fecha_registro')
    list_filter = ('experiencia', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'ci', 'telefono', 'email')
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'ci')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Información Física', {
            'fields': ('peso', 'altura', 'experiencia'),
            'description': 'Información sobre el estado físico y experiencia del cliente'
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
