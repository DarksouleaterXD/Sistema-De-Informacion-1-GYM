"""
Serializers para el módulo de Instructores
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Instructor
from apps.users.serializers import UserSerializer

User = get_user_model()


class InstructorListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar instructores"""
    nombre_completo = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    usuario_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = [
            'id', 'usuario', 'usuario_info', 'nombre_completo', 'email',
            'especialidades', 'experiencia_anos', 'telefono', 
            'activo', 'fecha_ingreso', 'created_at', 'updated_at'
        ]
    
    def get_usuario_info(self, obj):
        """Información básica del usuario"""
        return {
            'id': obj.usuario.id,
            'username': obj.usuario.username,
            'email': obj.usuario.email,
            'first_name': obj.usuario.first_name,
            'last_name': obj.usuario.last_name,
            'is_active': obj.usuario.is_active,
        }


class InstructorDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para ver un instructor"""
    nombre_completo = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    usuario_info = UserSerializer(source='usuario', read_only=True)
    clases_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = [
            'id', 'usuario', 'usuario_info', 'nombre_completo', 'email',
            'especialidades', 'certificaciones', 'experiencia_anos',
            'telefono', 'telefono_emergencia', 'biografia', 'foto_url',
            'activo', 'fecha_ingreso', 'clases_count',
            'created_at', 'updated_at'
        ]
    
    def get_clases_count(self, obj):
        """Cuenta las clases asignadas al instructor"""
        return obj.usuario.clases_instructor.count()


class InstructorCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un instructor"""
    usuario_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Instructor
        fields = [
            'usuario_id', 'especialidades', 'certificaciones', 
            'experiencia_anos', 'telefono', 'telefono_emergencia',
            'biografia', 'foto_url', 'activo', 'fecha_ingreso'
        ]
    
    def validate_usuario_id(self, value):
        """Validar que el usuario existe y no tiene perfil de instructor"""
        try:
            usuario = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("El usuario no existe.")
        
        # Verificar que no tenga ya un perfil de instructor
        if hasattr(usuario, 'instructor_profile'):
            raise serializers.ValidationError(
                "Este usuario ya tiene un perfil de instructor."
            )
        
        # Verificar que el usuario tenga el rol de Instructor
        from apps.roles.models import UserRole, Role
        try:
            rol_instructor = Role.objects.get(nombre='Instructor')
            if not UserRole.objects.filter(usuario=usuario, rol=rol_instructor).exists():
                raise serializers.ValidationError(
                    "El usuario debe tener el rol de Instructor."
                )
        except Role.DoesNotExist:
            pass  # Si no existe el rol, permitir la creación
        
        return value
    
    def create(self, validated_data):
        """Crear el perfil de instructor"""
        usuario_id = validated_data.pop('usuario_id')
        usuario = User.objects.get(id=usuario_id)
        instructor = Instructor.objects.create(usuario=usuario, **validated_data)
        return instructor


class InstructorUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar un instructor"""
    
    class Meta:
        model = Instructor
        fields = [
            'especialidades', 'certificaciones', 'experiencia_anos',
            'telefono', 'telefono_emergencia', 'biografia', 'foto_url',
            'activo', 'fecha_ingreso'
        ]
    
    def validate_especialidades(self, value):
        """Validar que las especialidades no estén vacías"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Las especialidades no pueden estar vacías."
            )
        return value
