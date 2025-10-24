from django.contrib import admin
from .models import InscripcionMembresia, Membresia, PlanMembresia, MembresiaPromocion


@admin.register(PlanMembresia)
class PlanMembresiaAdmin(admin.ModelAdmin):
    """
    Admin para el modelo PlanMembresia
    """
    list_display = ('nombre', 'duracion', 'precio_base', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información del Plan', {
            'fields': ('nombre', 'duracion', 'precio_base', 'descripcion')
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
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__ci')
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


class MembresiaPromocionInline(admin.TabularInline):
    """Inline para promociones aplicadas a la membresía"""
    model = MembresiaPromocion
    extra = 1
    verbose_name = "Promoción Aplicada"
    verbose_name_plural = "Promociones Aplicadas"


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Membresia
    """
    list_display = ('get_cliente', 'plan', 'usuario_registro', 'estado', 'fecha_inicio', 'fecha_fin', 'dias_restantes')
    list_filter = ('estado', 'plan', 'fecha_inicio', 'fecha_fin')
    search_fields = ('inscripcion__cliente__nombre', 'inscripcion__cliente__apellido', 'usuario_registro__email')
    readonly_fields = ('created_at', 'updated_at', 'dias_restantes')
    date_hierarchy = 'fecha_inicio'
    inlines = [MembresiaPromocionInline]
    
    fieldsets = (
        ('Inscripción y Plan', {
            'fields': ('inscripcion', 'plan', 'usuario_registro')
        }),
        ('Estado y Vigencia', {
            'fields': ('estado', 'fecha_inicio', 'fecha_fin', 'dias_restantes')
        }),
        ('Fechas de Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_cliente(self, obj):
        """Obtiene el nombre del cliente"""
        return obj.inscripcion.cliente
    get_cliente.short_description = 'Cliente'
    
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
