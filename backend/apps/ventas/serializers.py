"""
Serializers para Ventas
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Venta, DetalleVenta
from apps.clients.models import Client
from apps.productos.models import Producto


class DetalleVentaSerializer(serializers.ModelSerializer):
    """Serializer para Detalle de Venta"""
    
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_codigo',
            'cantidad', 'precio_unitario', 'descuento', 'subtotal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['subtotal', 'created_at', 'updated_at']


class DetalleVentaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear Detalle de Venta"""
    
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario', 'descuento']
    
    def validate(self, data):
        """Validar stock disponible"""
        producto = data.get('producto')
        cantidad = data.get('cantidad')
        
        if producto and cantidad:
            if producto.stock < cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {producto.stock}'
                })
        
        return data


class VentaListSerializer(serializers.ModelSerializer):
    """Serializer para listar Ventas"""
    
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_ci = serializers.CharField(source='cliente.ci', read_only=True)
    vendedor_nombre = serializers.SerializerMethodField()
    cantidad_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'numero_venta', 'fecha_venta', 'cliente', 'cliente_nombre',
            'cliente_ci', 'metodo_pago', 'estado', 'subtotal', 'descuento',
            'total', 'vendedor_nombre', 'cantidad_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_vendedor_nombre(self, obj):
        """Retorna el nombre del vendedor"""
        if obj.vendedor:
            return f"{obj.vendedor.first_name} {obj.vendedor.last_name}".strip() or obj.vendedor.username
        return None


class VentaDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de Venta con detalles incluidos"""
    
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_ci = serializers.CharField(source='cliente.ci', read_only=True)
    cliente_telefono = serializers.CharField(source='cliente.telefono', read_only=True)
    cliente_email = serializers.CharField(source='cliente.email', read_only=True)
    vendedor_nombre = serializers.SerializerMethodField()
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'numero_venta', 'fecha_venta', 'cliente', 'cliente_nombre',
            'cliente_ci', 'cliente_telefono', 'cliente_email', 'metodo_pago',
            'estado', 'subtotal', 'descuento', 'total', 'observaciones',
            'vendedor', 'vendedor_nombre', 'detalles', 'cantidad_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['numero_venta', 'created_at', 'updated_at']
    
    def get_vendedor_nombre(self, obj):
        """Retorna el nombre del vendedor"""
        if obj.vendedor:
            return f"{obj.vendedor.first_name} {obj.vendedor.last_name}".strip() or obj.vendedor.username
        return None


class VentaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear Venta con detalles"""
    
    detalles = DetalleVentaCreateSerializer(many=True)
    
    class Meta:
        model = Venta
        fields = [
            'cliente', 'metodo_pago', 'descuento', 'observaciones', 'detalles'
        ]
    
    def validate_detalles(self, value):
        """Validar que haya al menos un detalle"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Debe incluir al menos un producto en la venta.")
        return value
    
    def validate(self, data):
        """Validar stock de todos los productos"""
        detalles = data.get('detalles', [])
        
        for detalle in detalles:
            producto = detalle.get('producto')
            cantidad = detalle.get('cantidad')
            
            if producto and cantidad:
                if producto.stock < cantidad:
                    raise serializers.ValidationError({
                        'detalles': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}'
                    })
        
        return data
    
    def create(self, validated_data):
        """Crear venta con detalles y actualizar stock"""
        detalles_data = validated_data.pop('detalles')
        venta = Venta.objects.create(**validated_data)
        
        # Crear detalles y actualizar stock
        for detalle_data in detalles_data:
            producto = detalle_data['producto']
            cantidad = detalle_data['cantidad']
            precio_unitario = detalle_data.get('precio_unitario', producto.precio)
            descuento = detalle_data.get('descuento', Decimal('0.00'))
            
            # Crear detalle
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento=descuento
            )
        
        # Completar venta y actualizar stock
        venta.estado = Venta.ESTADO_COMPLETADA
        venta.vendedor = self.context['request'].user
        venta.save()
        
        # Actualizar stock de todos los productos
        for detalle in venta.detalles.all():
            detalle.producto.actualizar_stock(detalle.cantidad, operacion='restar')
            detalle.producto.save()
        
        return venta


class VentaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar Venta (solo campos permitidos)"""
    
    class Meta:
        model = Venta
        fields = ['metodo_pago', 'descuento', 'observaciones', 'estado']
    
    def validate_estado(self, value):
        """Validar cambio de estado"""
        instance = self.instance
        
        # No permitir cambiar de completada a pendiente
        if instance.estado == Venta.ESTADO_COMPLETADA and value == Venta.ESTADO_PENDIENTE:
            raise serializers.ValidationError(
                "No se puede cambiar una venta completada a pendiente."
            )
        
        # Si se cancela una venta completada, revertir stock
        if instance.estado == Venta.ESTADO_COMPLETADA and value == Venta.ESTADO_CANCELADA:
            # Revertir stock de todos los detalles
            for detalle in instance.detalles.all():
                detalle.producto.actualizar_stock(detalle.cantidad, operacion='sumar')
                detalle.producto.save()
        
        return value

