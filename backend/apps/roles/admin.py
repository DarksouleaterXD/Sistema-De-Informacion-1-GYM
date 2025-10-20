from django.contrib import admin
from .models import Role, Permiso, UserRole, RolPermiso


class RolPermisoInline(admin.TabularInline):
    """
    Inline para gestionar permisos de un rol
    """
    model = RolPermiso
    extra = 1
    autocomplete_fields = ['permiso']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Role
    """
    list_display = ('nombre', 'descripcion', 'total_permisos', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RolPermisoInline]
    
    def total_permisos(self, obj):
        """Muestra el total de permisos asignados al rol"""
        return obj.permisos.count()
    total_permisos.short_description = 'Total Permisos'


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Permiso
    """
    list_display = ('nombre', 'descripcion', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin para la tabla intermedia UserRole
    """
    list_display = ('usuario', 'rol', 'created_at')
    list_filter = ('rol',)
    search_fields = ('usuario__email', 'usuario__username', 'rol__nombre')
    autocomplete_fields = ['usuario', 'rol']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    """
    Admin para la tabla intermedia RolPermiso
    """
    list_display = ('rol', 'permiso', 'created_at')
    list_filter = ('rol',)
    search_fields = ('rol__nombre', 'permiso__nombre')
    autocomplete_fields = ['rol', 'permiso']
    readonly_fields = ('created_at', 'updated_at')
