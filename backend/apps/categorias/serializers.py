"""
Serializers para Categorías de Productos
"""
from rest_framework import serializers
from .models import CategoriaProducto


class CategoriaProductoSerializer(serializers.ModelSerializer):
    """Serializer para Categoría de Productos"""
    
    total_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoriaProducto
        fields = [
            'id', 'nombre', 'codigo', 'descripcion', 'activo',
            'total_productos', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_productos(self, obj):
        """Cuenta productos activos de esta categoría"""
        from apps.productos.models import Producto
        return obj.productos.filter(estado=Producto.ESTADO_ACTIVO).count()

