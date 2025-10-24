from rest_framework import serializers
from apps.promociones.models import Promocion


class PromocionSerializer(serializers.ModelSerializer):
    esta_vigente = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Promocion
        fields = [
            'id',
            'nombre',
            'descripcion',
            'tipo_descuento',
            'valor_descuento',
            'fecha_inicio',
            'fecha_fin',
            'activo',
            'codigo',
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

    def validate_valor_descuento(self, value):
        """Validar valor de descuento según el tipo"""
        if value <= 0:
            raise serializers.ValidationError("El valor del descuento debe ser mayor a 0")
        return value

    def validate_codigo(self, value):
        """Validar código promocional único (si se proporciona)"""
        if value:
            instance = self.instance
            qs = Promocion.objects.filter(codigo__iexact=value.strip())
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Ya existe una promoción con este código")
            return value.strip().upper()
        return value
