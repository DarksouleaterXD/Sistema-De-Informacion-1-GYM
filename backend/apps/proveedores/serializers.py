"""
CU29 - Registrar Proveedor
Serializers con DTOs y validaciones
"""
from rest_framework import serializers
from django.core.validators import EmailValidator
import re
from .models import Proveedor


class ProveedorCreateSerializer(serializers.ModelSerializer):
    """
    DTO de entrada para crear proveedor
    Validaciones:
    - razon_social: requerido, único
    - nit: requerido, único
    - email: formato válido
    - telefono: 7-15 dígitos
    """
    
    class Meta:
        model = Proveedor
        fields = [
            'razon_social',
            'nit',
            'telefono',
            'email',
            'direccion',
            'contacto_nombre',
            'notas'
        ]
    
    def validate_razon_social(self, value):
        """Validar razón social: requerido, único, no vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("La razón social es obligatoria.")
        
        value_clean = value.strip()
        
        # Validar longitud
        if len(value_clean) < 2:
            raise serializers.ValidationError("La razón social debe tener al menos 2 caracteres.")
        
        if len(value_clean) > 200:
            raise serializers.ValidationError("La razón social no puede exceder 200 caracteres.")
        
        # Validar unicidad (solo en creación)
        if self.instance is None:  # CREATE
            if Proveedor.objects.filter(razon_social__iexact=value_clean).exists():
                raise serializers.ValidationError(
                    "Ya existe un proveedor con esta razón social."
                )
        else:  # UPDATE
            if Proveedor.objects.filter(razon_social__iexact=value_clean).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Ya existe otro proveedor con esta razón social."
                )
        
        return value_clean
    
    def validate_nit(self, value):
        """Validar NIT: requerido, único, formato válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("El NIT es obligatorio.")
        
        value_clean = value.strip().upper()
        
        # Validar longitud
        if len(value_clean) < 3:
            raise serializers.ValidationError("El NIT debe tener al menos 3 caracteres.")
        
        if len(value_clean) > 50:
            raise serializers.ValidationError("El NIT no puede exceder 50 caracteres.")
        
        # Validar formato: alfanumérico y algunos caracteres especiales permitidos (-, /)
        if not re.match(r'^[A-Z0-9\-/]+$', value_clean):
            raise serializers.ValidationError(
                "El NIT solo puede contener letras, números, guiones y barras."
            )
        
        # Validar unicidad (solo en creación)
        if self.instance is None:  # CREATE
            if Proveedor.objects.filter(nit=value_clean).exists():
                raise serializers.ValidationError(
                    "Ya existe un proveedor con este NIT."
                )
        else:  # UPDATE
            if Proveedor.objects.filter(nit=value_clean).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Ya existe otro proveedor con este NIT."
                )
        
        return value_clean
    
    def validate_email(self, value):
        """Validar formato de email"""
        if not value or not value.strip():
            return ""  # Email es opcional
        
        value_clean = value.strip().lower()
        
        # Validar formato con EmailValidator
        validator = EmailValidator(message='Ingrese un correo electrónico válido.')
        try:
            validator(value_clean)
        except Exception:
            raise serializers.ValidationError('Ingrese un correo electrónico válido.')
        
        return value_clean
    
    def validate_telefono(self, value):
        """Validar teléfono: 7-15 dígitos numéricos"""
        if not value or not value.strip():
            return ""  # Teléfono es opcional
        
        # Extraer solo dígitos
        digits_only = ''.join(filter(str.isdigit, value))
        
        if not digits_only:
            raise serializers.ValidationError(
                "El teléfono debe contener al menos un dígito numérico."
            )
        
        # Validar longitud: 7-15 dígitos
        if len(digits_only) < 7:
            raise serializers.ValidationError(
                "El teléfono debe tener al menos 7 dígitos."
            )
        
        if len(digits_only) > 15:
            raise serializers.ValidationError(
                "El teléfono no puede exceder 15 dígitos."
            )
        
        return digits_only
    
    def validate_direccion(self, value):
        """Validar dirección (opcional)"""
        if not value:
            return ""
        
        value_clean = value.strip()
        
        if len(value_clean) > 500:
            raise serializers.ValidationError(
                "La dirección no puede exceder 500 caracteres."
            )
        
        return value_clean
    
    def validate_contacto_nombre(self, value):
        """Validar nombre de contacto (opcional)"""
        if not value:
            return ""
        
        value_clean = value.strip()
        
        if len(value_clean) > 100:
            raise serializers.ValidationError(
                "El nombre de contacto no puede exceder 100 caracteres."
            )
        
        return value_clean


class ProveedorResponseSerializer(serializers.ModelSerializer):
    """
    DTO de salida para respuestas de proveedor
    Incluye todos los campos relevantes incluyendo timestamps
    """
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Proveedor
        fields = [
            'id',
            'razon_social',
            'nit',
            'telefono',
            'email',
            'direccion',
            'contacto_nombre',
            'notas',
            'estado',
            'estado_display',
            'esta_activo',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProveedorListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listados
    Solo campos esenciales para optimizar respuesta
    """
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Proveedor
        fields = [
            'id',
            'razon_social',
            'nit',
            'telefono',
            'email',
            'estado',
            'estado_display',
            'created_at'
        ]
        read_only_fields = fields


class ProveedorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización de proveedor
    Permite modificar todos los campos excepto NIT (identificador único)
    """
    
    class Meta:
        model = Proveedor
        fields = [
            'razon_social',
            'telefono',
            'email',
            'direccion',
            'contacto_nombre',
            'notas',
            'estado'
        ]
    
    def validate_razon_social(self, value):
        """Reutiliza validación de ProveedorCreateSerializer"""
        serializer = ProveedorCreateSerializer(instance=self.instance)
        return serializer.validate_razon_social(value)
    
    def validate_email(self, value):
        """Reutiliza validación de ProveedorCreateSerializer"""
        serializer = ProveedorCreateSerializer(instance=self.instance)
        return serializer.validate_email(value)
    
    def validate_telefono(self, value):
        """Reutiliza validación de ProveedorCreateSerializer"""
        serializer = ProveedorCreateSerializer(instance=self.instance)
        return serializer.validate_telefono(value)
    
    def validate_direccion(self, value):
        """Reutiliza validación de ProveedorCreateSerializer"""
        serializer = ProveedorCreateSerializer(instance=self.instance)
        return serializer.validate_direccion(value)
    
    def validate_contacto_nombre(self, value):
        """Reutiliza validación de ProveedorCreateSerializer"""
        serializer = ProveedorCreateSerializer(instance=self.instance)
        return serializer.validate_contacto_nombre(value)
