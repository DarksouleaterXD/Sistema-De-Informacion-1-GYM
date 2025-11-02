from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.roles.models import Role, Permiso, RolPermiso, UserRole

User = get_user_model()


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = "__all__"


class RolSerializer(serializers.ModelSerializer):
    permisos = serializers.SerializerMethodField()
    permisos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de permisos a asignar al rol"
    )
    usuarios_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "nombre",
            "descripcion",
            "created_at",
            "permisos",
            "permisos_ids",
            "usuarios_count",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_nombre(self, value):
        qs = Role.objects.all()
        instance = getattr(self, "instance", None)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.filter(nombre__iexact=value.strip()).exists():
            raise serializers.ValidationError("Ya existe un rol con ese nombre.")
        return value.strip()

    def get_permisos(self, obj):
        return PermisoSerializer(obj.permisos.all(), many=True).data

    def get_usuarios_count(self, obj):
        return UserRole.objects.filter(rol=obj).count()
    
    def create(self, validated_data):
        permisos_ids = validated_data.pop('permisos_ids', [])
        role = Role.objects.create(**validated_data)
        
        # Asignar permisos si se proporcionaron
        if permisos_ids:
            permisos = Permiso.objects.filter(id__in=permisos_ids)
            for permiso in permisos:
                RolPermiso.objects.create(rol=role, permiso=permiso)
        
        return role
    
    def update(self, instance, validated_data):
        permisos_ids = validated_data.pop('permisos_ids', None)
        
        # Actualizar campos básicos
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.save()
        
        # Actualizar permisos si se proporcionaron
        if permisos_ids is not None:
            # Eliminar permisos actuales
            RolPermiso.objects.filter(rol=instance).delete()
            # Asignar nuevos permisos
            permisos = Permiso.objects.filter(id__in=permisos_ids)
            for permiso in permisos:
                RolPermiso.objects.create(rol=instance, permiso=permiso)
        
        return instance

class RolPermisoSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.ReadOnlyField(source="rol.nombre")
    permiso_nombre = serializers.ReadOnlyField(source="permiso.nombre")

    class Meta:
        model = RolPermiso
        fields = ["id", "rol", "permiso", "rol_nombre", "permiso_nombre"]


class UsuarioRolSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.ReadOnlyField(source="usuario.username")
    rol_nombre = serializers.ReadOnlyField(source="rol.nombre")

    class Meta:
        model = UserRole
        fields = ["id", "usuario", "rol", "usuario_nombre", "rol_nombre"]


class RolePermissionSerializer(serializers.Serializer):
    permiso_id = serializers.IntegerField()


class RolePermissionSetSerializer(serializers.Serializer):
    permisos = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
