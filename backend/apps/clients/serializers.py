from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Client con validaciones"""
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = [
            'id',
            'nombre',
            'apellido',
            'nombre_completo',
            'ci',
            'telefono',
            'email',
            'peso',
            'altura',
            'experiencia',
            'fecha_registro',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'fecha_registro', 'created_at', 'updated_at']
    
    def validate_ci(self, value):
        """Validar que el CI sea único y válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("La cédula de identidad es obligatoria.")
        
        # Validar formato (solo números, entre 6 y 10 dígitos)
        ci_clean = value.strip()
        if not ci_clean.isdigit():
            raise serializers.ValidationError("La cédula de identidad debe contener solo números.")
        
        if len(ci_clean) < 6 or len(ci_clean) > 10:
            raise serializers.ValidationError("La cédula de identidad debe tener entre 6 y 10 dígitos.")
        
        # Validar unicidad al crear
        if self.instance is None:  # CREATE
            if Client.objects.filter(ci=ci_clean).exists():
                raise serializers.ValidationError("Ya existe un cliente con esta cédula de identidad.")
        else:  # UPDATE
            if Client.objects.filter(ci=ci_clean).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe otro cliente con esta cédula de identidad.")
        
        return ci_clean
    
    def validate_telefono(self, value):
        """Validar formato de teléfono boliviano"""
        if not value:
            return value
        
        telefono_clean = value.strip()
        
        # Remover espacios y caracteres especiales
        telefono_clean = ''.join(filter(str.isdigit, telefono_clean))
        
        # Validar longitud (teléfonos bolivianos: 8 dígitos)
        if len(telefono_clean) != 8:
            raise serializers.ValidationError("El teléfono debe tener 8 dígitos.")
        
        # Validar que empiece con 6, 7, 2, 3, 4 (prefijos bolivianos)
        if telefono_clean[0] not in ['2', '3', '4', '6', '7']:
            raise serializers.ValidationError("El teléfono debe empezar con un prefijo válido (2, 3, 4, 6 o 7).")
        
        return telefono_clean
    
    def validate_email(self, value):
        """Validar formato de email"""
        if not value:
            return value
        
        email_clean = value.strip().lower()
        
        # Validar que no exista otro cliente con el mismo email (opcional)
        if self.instance is None:  # CREATE
            if Client.objects.filter(email=email_clean).exists():
                raise serializers.ValidationError("Ya existe un cliente con este email.")
        else:  # UPDATE
            if Client.objects.filter(email=email_clean).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe otro cliente con este email.")
        
        return email_clean
    
    def validate_nombre(self, value):
        """Validar que el nombre no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio.")
        return value.strip().title()
    
    def validate_apellido(self, value):
        """Validar que el apellido no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El apellido es obligatorio.")
        return value.strip().title()


class ClientListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = [
            'id',
            'nombre',
            'apellido',
            'nombre_completo',
            'ci',
            'telefono',
            'email',
            'fecha_registro'
        ]
