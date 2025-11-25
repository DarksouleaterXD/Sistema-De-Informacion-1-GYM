"""
Serializers para Productos
"""
from rest_framework import serializers
from .models import CategoriaProducto, Producto
from apps.proveedores.serializers import ProveedorResponseSerializer
from apps.promociones.serializers import PromocionSerializer


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
        return obj.productos.filter(estado=Producto.ESTADO_ACTIVO).count()


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de productos"""
    
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    promocion_nombre = serializers.CharField(source='promocion.nombre', read_only=True, allow_null=True)
    precio_con_descuento = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    necesita_reposicion = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo', 'categoria', 'categoria_nombre',
            'proveedor', 'proveedor_nombre', 'precio', 'precio_con_descuento',
            'stock', 'stock_minimo', 'necesita_reposicion', 'estado',
            'promocion', 'promocion_nombre', 'created_at'
        ]


class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de producto"""
    
    categoria_info = CategoriaProductoSerializer(source='categoria', read_only=True)
    proveedor_info = ProveedorResponseSerializer(source='proveedor', read_only=True)
    promocion_info = PromocionSerializer(source='promocion', read_only=True)
    precio_con_descuento = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    necesita_reposicion = serializers.BooleanField(read_only=True)
    margen_ganancia = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, allow_null=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    modificado_por_nombre = serializers.CharField(source='modificado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo', 'descripcion',
            'categoria', 'categoria_info',
            'proveedor', 'proveedor_info',
            'precio', 'costo', 'precio_con_descuento', 'margen_ganancia',
            'stock', 'stock_minimo', 'unidad_medida', 'necesita_reposicion',
            'promocion', 'promocion_info', 'estado',
            'creado_por', 'creado_por_nombre',
            'modificado_por', 'modificado_por_nombre',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'creado_por', 'modificado_por']


class ProductoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar productos"""
    
    class Meta:
        model = Producto
        fields = [
            'nombre', 'codigo', 'descripcion', 'categoria', 'proveedor',
            'precio', 'costo', 'stock', 'stock_minimo', 'unidad_medida',
            'promocion', 'estado'
        ]
    
    def validate_codigo(self, value):
        """Validar que el código sea único"""
        value = value.strip().upper()
        
        # Si es actualización, excluir el producto actual
        if self.instance:
            if Producto.objects.filter(codigo=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe un producto con este código.")
        else:
            if Producto.objects.filter(codigo=value).exists():
                raise serializers.ValidationError("Ya existe un producto con este código.")
        
        return value
    
    def validate(self, data):
        """Validaciones cruzadas"""
        # Validar que el precio sea mayor que el costo
        if 'costo' in data and data.get('costo') and 'precio' in data:
            if data['precio'] < data['costo']:
                raise serializers.ValidationError({
                    'precio': 'El precio de venta no puede ser menor que el costo.'
                })
        
        # Validar stock mínimo
        if 'stock_minimo' in data and 'stock' in data:
            if data['stock'] < 0 or data['stock_minimo'] < 0:
                raise serializers.ValidationError({
                    'stock': 'Los valores de stock no pueden ser negativos.'
                })
        
        return data
    
    def create(self, validated_data):
        """Registrar auditoría al crear"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creado_por'] = request.user
            validated_data['modificado_por'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Registrar auditoría al actualizar"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['modificado_por'] = request.user
        
        return super().update(instance, validated_data)


class ActualizarStockSerializer(serializers.Serializer):
    """Serializer para actualizar stock del producto"""
    
    cantidad = serializers.IntegerField(min_value=1)
    operacion = serializers.ChoiceField(choices=['sumar', 'restar'])
    motivo = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value
