
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
# --- CU1: Registrar Administrador -------------------------------------------
class AdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese username.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
# --- /CU1 -------------------------------------------------------------------
User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        # La vista llamará a authenticate(); aquí solo validamos presencia
        if not attrs.get("email") or not attrs.get("password"):
            raise serializers.ValidationError("Email y contraseña son obligatorios.")
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        # invalidar refresh (requiere app 'token_blacklist' habilitada)
        RefreshToken(self.token).blacklist()
# --- /CU2 --------------------------------------------------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=6, trim_whitespace=False)

    def validate_new_password(self, value):
        # Ajusta tus reglas (longitud, complejidad, etc.)
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value
# --- /Password Reset ---------------------------------------------------------

# Serializer para obtener datos del usuario actual
class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active", "roles"]
        read_only_fields = ["id", "username", "email"]
    
    def get_roles(self, obj):
        from apps.roles.models import UserRole
        user_roles = UserRole.objects.filter(usuario=obj).select_related('rol')
        return [ur.rol.nombre for ur in user_roles]


# --- CRUD Usuarios -----------------------------------------------------------
class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar usuarios"""
    roles = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name", 
                  "is_active", "is_staff", "is_superuser", "date_joined", "roles"]
    
    def get_roles(self, obj):
        from apps.roles.models import UserRole
        user_roles = UserRole.objects.filter(usuario=obj).select_related('rol')
        return [{"id": ur.rol.id, "nombre": ur.rol.nombre} for ur in user_roles]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios"""
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de roles a asignar"
    )
    
    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", 
                  "is_active", "is_staff", "is_superuser", "roles"]
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value.lower()
    
    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese username.")
        return value.lower()
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value
    
    def create(self, validated_data):
        roles_ids = validated_data.pop('roles', [])
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Asignar roles
        if roles_ids:
            from apps.roles.models import Role, UserRole
            for role_id in roles_ids:
                try:
                    role = Role.objects.get(id=role_id)
                    UserRole.objects.create(usuario=user, rol=role)
                except Role.DoesNotExist:
                    pass
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios"""
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de roles a asignar"
    )
    change_password = serializers.CharField(
        write_only=True, 
        required=False, 
        min_length=8,
        help_text="Nueva contraseña (opcional)"
    )
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "is_active", "is_staff", 
                  "is_superuser", "roles", "change_password"]
    
    def validate_change_password(self, value):
        if value and len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value
    
    def update(self, instance, validated_data):
        roles_ids = validated_data.pop('roles', None)
        new_password = validated_data.pop('change_password', None)
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Cambiar contraseña si se proporciona
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        
        # Actualizar roles
        if roles_ids is not None:
            from apps.roles.models import Role, UserRole
            # Eliminar roles actuales
            UserRole.objects.filter(usuario=instance).delete()
            # Asignar nuevos roles
            for role_id in roles_ids:
                try:
                    role = Role.objects.get(id=role_id)
                    UserRole.objects.create(usuario=instance, rol=role)
                except Role.DoesNotExist:
                    pass
        
        return instance