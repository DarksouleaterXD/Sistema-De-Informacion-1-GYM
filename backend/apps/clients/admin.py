from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Client
    """
    list_display = ('nombre', 'apellido', 'ci', 'telefono', 'email', 'fecha_registro')
    list_filter = ('fecha_registro',)
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
        ('Fechas', {
            'fields': ('fecha_registro', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
