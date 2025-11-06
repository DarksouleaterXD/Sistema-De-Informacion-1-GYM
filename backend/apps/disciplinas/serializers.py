from rest_framework import serializers
from .models import Disciplina


class DisciplinaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Disciplina (CU19)
    """
    
    class Meta:
        model = Disciplina
        fields = [
            'id',
            'nombre',
            'descripcion',
            'activa',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_nombre(self, value):
        """Validar que el nombre no esté vacío y sea único"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la disciplina es obligatorio")
        
        # Verificar duplicidad (excepto en edición)
        instance = self.instance
        if Disciplina.objects.filter(nombre__iexact=value.strip()).exclude(
            id=instance.id if instance else None
        ).exists():
            raise serializers.ValidationError(
                f"Ya existe una disciplina con el nombre '{value}'"
            )
        
        return value.strip()


class DisciplinaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listados
    """
    
    class Meta:
        model = Disciplina
        fields = ['id', 'nombre', 'descripcion', 'activa']
