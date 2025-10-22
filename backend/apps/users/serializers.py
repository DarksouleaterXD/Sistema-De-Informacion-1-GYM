
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
    username = serializers.CharField()  
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