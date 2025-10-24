from rest_framework import serializers
from apps.promociones.models import Promocion


class PromocionSerializer(serializers.ModelSerializer):
    """Serializer para Promoción según PUML"""
    esta_vigente = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Promocion
        fields = [
            'id',
            'nombre',
            'meses',
            'descuento',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'estado_display',
            'esta_vigente',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'esta_vigente']

    def validate(self, data):
        """Validar que fecha_fin sea mayor a fecha_inicio"""
        if data.get('fecha_inicio') and data.get('fecha_fin'):
            if data['fecha_fin'] < data['fecha_inicio']:
                raise serializers.ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        return data

    def validate_descuento(self, value):
        """Validar valor de descuento (porcentaje)"""
        if value <= 0:
            raise serializers.ValidationError("El descuento debe ser mayor a 0")
        if value > 100:
            raise serializers.ValidationError("El descuento no puede ser mayor a 100%")
        return value
    
    def validate_meses(self, value):
        """Validar que los meses sean positivos"""
        if value <= 0:
            raise serializers.ValidationError("Los meses deben ser mayor a 0")
        return value
