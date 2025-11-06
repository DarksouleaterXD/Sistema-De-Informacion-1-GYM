from django.contrib import admin
from .models import Disciplina


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'created_at', 'updated_at']
    list_filter = ['activa', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
