"""
Módulo de Compras
Gestión de órdenes de compra con items y actualización automática de stock
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal
from apps.core.models import TimeStampedModel


class OrdenCompra(TimeStampedModel):
    """
    Modelo de Orden de Compra
    Representa una orden de compra a un proveedor
    """
    
    # Estados de la orden
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CONFIRMADA = 'confirmada'
    ESTADO_RECIBIDA = 'recibida'
    ESTADO_CANCELADA = 'cancelada'
    
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_RECIBIDA, 'Recibida'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]
    
    # Relaciones
    proveedor = models.ForeignKey(
        'proveedores.Proveedor',
        on_delete=models.PROTECT,
        related_name='ordenes_compra',
        verbose_name="Proveedor"
    )
    
    # Información de la orden
    numero_orden = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de Orden",
        help_text="Número único de identificación de la orden"
    )
    
    fecha_orden = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Orden"
    )
    
    fecha_esperada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha Esperada de Entrega",
        help_text="Fecha esperada de recepción de la orden"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado"
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Subtotal"
    )
    
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Descuento"
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total"
    )
    
    # Observaciones
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # Usuario que creó la orden
    creado_por = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_compra_creadas',
        verbose_name="Creado por"
    )
    
    class Meta:
        db_table = 'orden_compra'
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-fecha_orden', '-created_at']
        indexes = [
            models.Index(fields=['numero_orden'], name='orden_compra_numero_idx'),
            models.Index(fields=['fecha_orden'], name='orden_compra_fecha_idx'),
            models.Index(fields=['estado'], name='orden_compra_estado_idx'),
        ]
    
    def __str__(self):
        return f"Orden #{self.numero_orden} - {self.proveedor.razon_social}"
    
    def calcular_totales(self):
        """Calcula subtotal y total basado en los items"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.total = self.subtotal - self.descuento
        self.save(update_fields=['subtotal', 'total'])
    
    @property
    def cantidad_items(self):
        """Retorna la cantidad total de items en la orden"""
        return self.items.aggregate(
            total=Sum('cantidad')
        )['total'] or 0
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        if self.total < 0:
            raise ValidationError({
                'total': 'El total no puede ser negativo.'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para generar número de orden automático"""
        if not self.numero_orden:
            # Generar número de orden único
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.numero_orden = f"ORD-{timestamp}"
        
        self.clean()
        super().save(*args, **kwargs)


class ItemOrdenCompra(TimeStampedModel):
    """
    Modelo de Item de Orden de Compra
    Representa un producto en una orden de compra
    """
    
    orden = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Orden de Compra"
    )
    
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='ordenes_compra',
        verbose_name="Producto"
    )
    
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
        help_text="Cantidad de productos a comprar"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Unitario",
        help_text="Precio de compra unitario"
    )
    
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Descuento"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal",
        help_text="Cantidad × Precio Unitario - Descuento"
    )
    
    class Meta:
        db_table = 'item_orden_compra'
        verbose_name = 'Item de Orden de Compra'
        verbose_name_plural = 'Items de Orden de Compra'
        ordering = ['-created_at']
        unique_together = [['orden', 'producto']]
    
    def __str__(self):
        return f"{self.orden.numero_orden} - {self.producto.nombre} x{self.cantidad}"
    
    def calcular_subtotal(self):
        """Calcula el subtotal del item"""
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento
        return self.subtotal
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        if self.cantidad <= 0:
            raise ValidationError({
                'cantidad': 'La cantidad debe ser mayor a cero.'
            })
        
        if self.precio_unitario < 0:
            raise ValidationError({
                'precio_unitario': 'El precio unitario no puede ser negativo.'
            })
        
        if self.descuento < 0:
            raise ValidationError({
                'descuento': 'El descuento no puede ser negativo.'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para calcular subtotal y actualizar stock"""
        self.calcular_subtotal()
        self.clean()
        
        # Si la orden está recibida, el stock ya fue actualizado
        if self.orden.estado == OrdenCompra.ESTADO_RECIBIDA:
            pass
        
        super().save(*args, **kwargs)
        
        # Recalcular totales de la orden
        self.orden.calcular_totales()

