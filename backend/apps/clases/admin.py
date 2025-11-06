from django.contrib import admin
from .models import Salon, Clase, InscripcionClase


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad', 'activo', 'created_at']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']


@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ['disciplina', 'instructor', 'salon', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'cupos_disponibles']
    list_filter = ['estado', 'fecha', 'disciplina']
    search_fields = ['disciplina__nombre', 'instructor__first_name', 'instructor__last_name']
    date_hierarchy = 'fecha'


@admin.register(InscripcionClase)
class InscripcionClaseAdmin(admin.ModelAdmin):
    list_display = ['clase', 'cliente', 'estado', 'fecha_inscripcion']
    list_filter = ['estado', 'fecha_inscripcion']
    search_fields = ['cliente__nombre', 'cliente__apellido', 'clase__disciplina__nombre']
