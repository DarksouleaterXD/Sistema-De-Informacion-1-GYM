"""
CU24 - Registrar Producto
Modelos para gestión de productos y categorías
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.proveedores.models import Proveedor
from apps.promociones.models import Promocion
from apps.users.models import User


class CategoriaProducto(TimeStampedModel):
    """
    Categoría de Productos
    Permite organizar los productos por tipo
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de Categoría"
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código",
        help_text="Código único de la categoría"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        db_table = 'categoria_producto'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Producto(TimeStampedModel):
    """
    Producto - Entidad principal para gestión de productos del gimnasio
    Incluye: suplementos, equipamiento, merchandising, etc.
    
    Relaciones:
    - CategoriaProducto: Clasificación del producto
    - Proveedor: Quien suministra el producto
    - Promocion: Descuentos aplicables (opcional)
    - User: Auditoría de creación/modificación
    """
    
    # Estados del producto
    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_INACTIVO = 'INACTIVO'
    ESTADO_AGOTADO = 'AGOTADO'
    ESTADO_DESCONTINUADO = 'DESCONTINUADO'
    
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
        (ESTADO_AGOTADO, 'Agotado'),
        (ESTADO_DESCONTINUADO, 'Descontinuado'),
    ]
    
    # Unidades de medida
    UNIDAD_UNIDAD = 'UNIDAD'
    UNIDAD_KG = 'KG'
    UNIDAD_GR = 'GR'
    UNIDAD_LB = 'LB'
    UNIDAD_LITRO = 'LITRO'
    UNIDAD_ML = 'ML'
    UNIDAD_CAJA = 'CAJA'
    UNIDAD_PAQUETE = 'PAQUETE'
    
    UNIDAD_CHOICES = [
        (UNIDAD_UNIDAD, 'Unidad'),
        (UNIDAD_KG, 'Kilogramo'),
        (UNIDAD_GR, 'Gramo'),
        (UNIDAD_LB, 'Libra'),
        (UNIDAD_LITRO, 'Litro'),
        (UNIDAD_ML, 'Mililitro'),
        (UNIDAD_CAJA, 'Caja'),
        (UNIDAD_PAQUETE, 'Paquete'),
    ]
    
    # Información básica
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Producto",
        help_text="Nombre comercial del producto"
    )
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código/SKU",
        help_text="Código único del producto (puede ser código de barras, SKU, etc.)"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del producto"
    )
    
    # Categoría
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Categoría"
    )
    
    # Proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Proveedor",
        help_text="Proveedor que suministra el producto"
    )
    
    # Precios
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Venta",
        help_text="Precio de venta al público (Bs.)"
    )
    
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name="Costo",
        help_text="Costo de adquisición (Bs.) - Opcional"
    )
    
    # Inventario
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual",
        help_text="Cantidad disponible en inventario"
    )
    
    stock_minimo = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima antes de reorden"
    )
    
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_CHOICES,
        default=UNIDAD_UNIDAD,
        verbose_name="Unidad de Medida"
    )
    
    # Promoción (opcional)
    promocion = models.ForeignKey(
        Promocion,
        on_delete=models.SET_NULL,
        related_name='productos',
        blank=True,
        null=True,
        verbose_name="Promoción",
        help_text="Promoción vigente aplicable al producto"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado"
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='productos_creados',
        null=True,
        verbose_name="Creado por"
    )
    
    modificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='productos_modificados',
        null=True,
        verbose_name="Modificado por"
    )
    
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria', 'estado']),
            models.Index(fields=['proveedor']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def clean(self):
        """Validaciones de negocio"""
        super().clean()
        
        # Validar que el precio sea mayor que el costo
        if self.costo and self.precio < self.costo:
            raise ValidationError({
                'precio': 'El precio de venta no puede ser menor que el costo.'
            })
        
        # Validar código único
        if self.codigo:
            self.codigo = self.codigo.strip().upper()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def precio_con_descuento(self):
        """Calcula el precio con descuento si hay promoción vigente"""
        if self.promocion and self.promocion.estado == 'activa':
            if self.promocion.tipo == 'porcentaje':
                descuento = self.precio * (self.promocion.valor / 100)
            else:  # monto_fijo
                descuento = self.promocion.valor
            return max(self.precio - descuento, 0)
        return self.precio
    
    @property
    def necesita_reposicion(self):
        """Indica si el producto necesita reposición"""
        return self.stock <= self.stock_minimo
    
    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia porcentual"""
        if self.costo and self.costo > 0:
            return ((self.precio - self.costo) / self.costo) * 100
        return None
    
    def actualizar_stock(self, cantidad, operacion='sumar'):
        """
        Actualiza el stock del producto
        operacion: 'sumar' (entrada) o 'restar' (venta)
        """
        if operacion == 'sumar':
            self.stock += cantidad
        elif operacion == 'restar':
            if self.stock >= cantidad:
                self.stock -= cantidad
            else:
                raise ValidationError('Stock insuficiente para realizar la operación.')
        
        # Actualizar estado si se agota
        if self.stock == 0:
            self.estado = self.ESTADO_AGOTADO
        elif self.estado == self.ESTADO_AGOTADO and self.stock > 0:
            self.estado = self.ESTADO_ACTIVO
        
        self.save()
