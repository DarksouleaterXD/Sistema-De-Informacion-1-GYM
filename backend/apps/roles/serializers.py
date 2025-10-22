# apps/roles/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.roles.models import Role , Permiso, RolPermiso, UserRole

User = get_user_model()


class PermisoSerializer(serializers.ModelSerializer):
    """Serializer básico de permisos."""
    class Meta:
        model = Permiso
        fields = "__all__"


class RolSerializer(serializers.ModelSerializer):
    """
    Serializer de Rol con:
      - permisos: lista de permisos (derivada de la tabla puente RolPermiso)
      - usuarios_count: cantidad de usuarios asignados a este rol
    """
    permisos = serializers.SerializerMethodField()
    usuarios_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activo",
            "fecha_creacion",
            "permisos",
            "usuarios_count",
        ]
        read_only_fields = ["id", "fecha_creacion"]

    def validate_nombre(self, value):
        qs = Role.objects.all()
        # Si es update, excluir el propio id
        instance = getattr(self, "instance", None)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.filter(nombre__iexact=value.strip()).exists():
            raise serializers.ValidationError("Ya existe un rol con ese nombre.")
        return value.strip()

    def get_permisos(self, obj: Role):
        # Usa prefetch en la vista para mejor rendimiento:
        #   Rol.objects.prefetch_related("permisos__permiso")
        rol_permisos = obj.permisos.select_related("permiso").all()
        permisos = [rp.permiso for rp in rol_permisos]
        return PermisoSerializer(permisos, many=True).data

    def get_usuarios_count(self, obj: Role) -> int:
        return UserRole.objects.filter(rol=obj).count()


class RolPermisoSerializer(serializers.ModelSerializer):
    """Serializer de la relación Rol-Permiso (lectura/depuración)."""
    rol_nombre = serializers.ReadOnlyField(source="rol.nombre")
    permiso_nombre = serializers.ReadOnlyField(source="permiso.nombre")

    class Meta:
        model = RolPermiso
        fields = ["id", "rol", "permiso", "rol_nombre", "permiso_nombre"]


class UsuarioRolSerializer(serializers.ModelSerializer):
    """
    Serializer de la relación Usuario-Rol.
    Útil para listar las asignaciones actuales.
    """
    usuario_nombre = serializers.ReadOnlyField(source="usuario.username")
    rol_nombre = serializers.ReadOnlyField(source="rol.nombre")

    class Meta:
        model = UserRole
        fields = ["id", "usuario", "rol", "usuario_nombre", "rol_nombre"]
