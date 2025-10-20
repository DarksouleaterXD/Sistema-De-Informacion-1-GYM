from django.contrib import admin
from .models import Client, InscripcionMembresia, Membresia


class InscripcionMembresiaInline(admin.StackedInline):
    """
    Inline para ver inscripciones desde el cliente
    """
    model = InscripcionMembresia
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    can_delete = False


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Client
    """
    list_display = ('nombre', 'apellido', 'telefono', 'peso', 'altura', 'experiencia', 'created_at')
    list_filter = ('experiencia', 'created_at')
    search_fields = ('nombre', 'apellido', 'telefono')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InscripcionMembresiaInline]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'telefono')
        }),
        ('Información Física', {
            'fields': ('peso', 'altura', 'experiencia')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InscripcionMembresia)
class InscripcionMembresiaAdmin(admin.ModelAdmin):
    """
    Admin para el modelo InscripcionMembresia
    """
    list_display = ('cliente', 'monto', 'metodo_de_pago', 'created_at')
    list_filter = ('metodo_de_pago', 'created_at')
    search_fields = ('cliente__nombre', 'cliente__apellido')
    autocomplete_fields = ['cliente']
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Pago', {
            'fields': ('monto', 'metodo_de_pago')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Membresia
    """
    list_display = ('inscripcion', 'usuario_registro', 'estado', 'fecha_inicio', 'fecha_fin', 'dias_restantes')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('inscripcion__cliente__nombre', 'inscripcion__cliente__apellido', 'usuario_registro__email')
    autocomplete_fields = ['inscripcion', 'usuario_registro']
    readonly_fields = ('created_at', 'updated_at', 'dias_restantes')
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Inscripción', {
            'fields': ('inscripcion', 'usuario_registro')
        }),
        ('Estado y Vigencia', {
            'fields': ('estado', 'fecha_inicio', 'fecha_fin', 'dias_restantes')
        }),
        ('Fechas de Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def dias_restantes(self, obj):
        """Calcula los días restantes de la membresía"""
        from django.utils import timezone
        if obj.fecha_fin:
            dias = (obj.fecha_fin - timezone.now().date()).days
            if dias > 0:
                return f"{dias} días"
            elif dias == 0:
                return "Vence hoy"
            else:
                return f"Venció hace {abs(dias)} días"
        return "Sin fecha de fin"
    dias_restantes.short_description = 'Días Restantes'
