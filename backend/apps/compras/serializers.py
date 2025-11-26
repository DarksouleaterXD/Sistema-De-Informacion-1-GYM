"""
Serializers para Compras
"""
from rest_framework import serializers
from decimal import Decimal
from .models import OrdenCompra, ItemOrdenCompra


class ItemOrdenCompraSerializer(serializers.ModelSerializer):
    """Serializer para Item de Orden de Compra"""
    
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    
    class Meta:
        model = ItemOrdenCompra
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_codigo',
            'cantidad', 'precio_unitario', 'descuento', 'subtotal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['subtotal', 'created_at', 'updated_at']


class ItemOrdenCompraCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear Item de Orden de Compra"""
    
    class Meta:
        model = ItemOrdenCompra
        fields = ['producto', 'cantidad', 'precio_unitario', 'descuento']


class OrdenCompraListSerializer(serializers.ModelSerializer):
    """Serializer para listar Órdenes de Compra"""
    
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    proveedor_nit = serializers.CharField(source='proveedor.nit', read_only=True)
    creado_por_nombre = serializers.SerializerMethodField()
    cantidad_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = OrdenCompra
        fields = [
            'id', 'numero_orden', 'fecha_orden', 'fecha_esperada', 'proveedor',
            'proveedor_nombre', 'proveedor_nit', 'estado', 'subtotal', 'descuento',
            'total', 'creado_por_nombre', 'cantidad_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_creado_por_nombre(self, obj):
        """Retorna el nombre del usuario que creó la orden"""
        if obj.creado_por:
            return f"{obj.creado_por.first_name} {obj.creado_por.last_name}".strip() or obj.creado_por.username
        return None


class OrdenCompraDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de Orden de Compra con items incluidos"""
    
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    proveedor_nit = serializers.CharField(source='proveedor.nit', read_only=True)
    proveedor_telefono = serializers.CharField(source='proveedor.telefono', read_only=True)
    proveedor_email = serializers.CharField(source='proveedor.email', read_only=True)
    proveedor_direccion = serializers.CharField(source='proveedor.direccion', read_only=True)
    creado_por_nombre = serializers.SerializerMethodField()
    items = ItemOrdenCompraSerializer(many=True, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = OrdenCompra
        fields = [
            'id', 'numero_orden', 'fecha_orden', 'fecha_esperada', 'proveedor',
            'proveedor_nombre', 'proveedor_nit', 'proveedor_telefono',
            'proveedor_email', 'proveedor_direccion', 'estado', 'subtotal',
            'descuento', 'total', 'observaciones', 'creado_por', 'creado_por_nombre',
            'items', 'cantidad_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['numero_orden', 'created_at', 'updated_at']
    
    def get_creado_por_nombre(self, obj):
        """Retorna el nombre del usuario que creó la orden"""
        if obj.creado_por:
            return f"{obj.creado_por.first_name} {obj.creado_por.last_name}".strip() or obj.creado_por.username
        return None


class OrdenCompraCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear Orden de Compra con items"""
    
    items = ItemOrdenCompraCreateSerializer(many=True)
    
    class Meta:
        model = OrdenCompra
        fields = [
            'proveedor', 'fecha_esperada', 'descuento', 'observaciones', 'items'
        ]
    
    def validate_items(self, value):
        """Validar que haya al menos un item"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Debe incluir al menos un producto en la orden.")
        return value
    
    def create(self, validated_data):
        """Crear orden de compra con items"""
        items_data = validated_data.pop('items')
        orden = OrdenCompra.objects.create(**validated_data)
        
        # Crear items
        for item_data in items_data:
            producto = item_data['producto']
            cantidad = item_data['cantidad']
            precio_unitario = item_data.get('precio_unitario', producto.costo or Decimal('0.00'))
            descuento = item_data.get('descuento', Decimal('0.00'))
            
            # Crear item
            ItemOrdenCompra.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento=descuento
            )
        
        # Asignar usuario creador
        orden.creado_por = self.context['request'].user
        orden.save()
        
        return orden


class OrdenCompraUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar Orden de Compra (solo campos permitidos)"""
    
    class Meta:
        model = OrdenCompra
        fields = ['fecha_esperada', 'descuento', 'observaciones', 'estado']
    
    def validate_estado(self, value):
        """Validar cambio de estado y actualizar stock"""
        instance = self.instance
        
        # Si se confirma la orden, actualizar stock
        if instance.estado == OrdenCompra.ESTADO_PENDIENTE and value == OrdenCompra.ESTADO_CONFIRMADA:
            # Al confirmar, no se actualiza stock aún
            pass
        
        # Si se recibe la orden, actualizar stock
        if instance.estado != OrdenCompra.ESTADO_RECIBIDA and value == OrdenCompra.ESTADO_RECIBIDA:
            # Actualizar stock de todos los items
            for item in instance.items.all():
                item.producto.actualizar_stock(item.cantidad, operacion='sumar')
                item.producto.save()
        
        # Si se cancela una orden recibida, revertir stock
        if instance.estado == OrdenCompra.ESTADO_RECIBIDA and value == OrdenCompra.ESTADO_CANCELADA:
            # Revertir stock de todos los items
            for item in instance.items.all():
                item.producto.actualizar_stock(item.cantidad, operacion='restar')
                item.producto.save()
        
        # No permitir cambiar de recibida a confirmada
        if instance.estado == OrdenCompra.ESTADO_RECIBIDA and value == OrdenCompra.ESTADO_CONFIRMADA:
            raise serializers.ValidationError(
                "No se puede cambiar una orden recibida a confirmada."
            )
        
        return value

