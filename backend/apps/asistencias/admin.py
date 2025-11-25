from django.contrib import admin
from .models import AsistenciaClase


@admin.register(AsistenciaClase)
class AsistenciaClaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cliente', 'clase', 'estado', 'hora_llegada',
        'es_tardia', 'registrado_por', 'fecha_registro'
    ]
    list_filter = ['estado', 'fecha_registro', 'clase__fecha']
    search_fields = [
        'cliente__nombre', 'cliente__apellido', 'cliente__ci',
        'clase__disciplina__nombre', 'observaciones'
    ]
    readonly_fields = ['fecha_registro', 'created_at', 'updated_at', 'es_tardia', 'minutos_retraso']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('inscripcion', 'clase', 'cliente')
        }),
        ('Estado de Asistencia', {
            'fields': ('estado', 'hora_llegada', 'es_tardia', 'minutos_retraso')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Registro', {
            'fields': ('registrado_por', 'fecha_registro')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cliente', 'clase', 'clase__disciplina', 'inscripcion', 'registrado_por'
        )
