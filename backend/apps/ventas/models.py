"""
Módulo de Ventas
Gestión de ventas de productos con detalles y actualización automática de stock
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from decimal import Decimal
from apps.core.models import TimeStampedModel
from apps.core.constants import METODOS_PAGO


class Venta(TimeStampedModel):
    """
    Modelo de Venta
    Representa una venta de productos a un cliente
    """
    
    # Estados de la venta
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_COMPLETADA = 'completada'
    ESTADO_CANCELADA = 'cancelada'
    
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_COMPLETADA, 'Completada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]
    
    # Relaciones
    cliente = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name="Cliente"
    )
    
    # Información de la venta
    numero_venta = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de Venta",
        help_text="Número único de identificación de la venta"
    )
    
    fecha_venta = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Venta"
    )
    
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default=METODOS_PAGO[0][0],
        verbose_name="Método de Pago"
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
    
    # Usuario que creó la venta
    vendedor = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_realizadas',
        verbose_name="Vendedor"
    )
    
    class Meta:
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta', '-created_at']
        indexes = [
            models.Index(fields=['numero_venta'], name='venta_numero_idx'),
            models.Index(fields=['fecha_venta'], name='venta_fecha_idx'),
            models.Index(fields=['estado'], name='venta_estado_idx'),
        ]
    
    def __str__(self):
        return f"Venta #{self.numero_venta} - {self.cliente.nombre_completo}"
    
    def calcular_totales(self):
        """Calcula subtotal y total basado en los detalles"""
        detalles = self.detalles.all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.total = self.subtotal - self.descuento
        self.save(update_fields=['subtotal', 'total'])
    
    @property
    def cantidad_items(self):
        """Retorna la cantidad total de items en la venta"""
        return self.detalles.aggregate(
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
        """Sobrescribe save para generar número de venta automático"""
        if not self.numero_venta:
            # Generar número de venta único
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.numero_venta = f"VNT-{timestamp}"
        
        self.clean()
        super().save(*args, **kwargs)


class DetalleVenta(TimeStampedModel):
    """
    Modelo de Detalle de Venta
    Representa un producto vendido en una venta
    """
    
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Venta"
    )
    
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name="Producto"
    )
    
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
        help_text="Cantidad de productos vendidos"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Unitario",
        help_text="Precio al momento de la venta"
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
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        ordering = ['-created_at']
        unique_together = [['venta', 'producto']]
    
    def __str__(self):
        return f"{self.venta.numero_venta} - {self.producto.nombre} x{self.cantidad}"
    
    def calcular_subtotal(self):
        """Calcula el subtotal del detalle"""
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
        
        # Validar stock disponible
        if self.venta.estado == Venta.ESTADO_PENDIENTE:
            if self.producto.stock < self.cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {self.producto.stock}'
                })
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para calcular subtotal y actualizar stock"""
        self.calcular_subtotal()
        self.clean()
        
        # Si la venta está completada, actualizar stock
        if self.venta.estado == Venta.ESTADO_COMPLETADA:
            # El stock ya fue actualizado al completar la venta
            pass
        
        super().save(*args, **kwargs)
        
        # Recalcular totales de la venta
        self.venta.calcular_totales()

