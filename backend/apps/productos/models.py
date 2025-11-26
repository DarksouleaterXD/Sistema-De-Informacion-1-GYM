"""
CU24 - Registrar Producto
Modelos para gestión de productos
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.categorias.models import CategoriaProducto
from apps.proveedores.models import Proveedor
from apps.promociones.models import Promocion
from apps.users.models import User


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
    ESTADO_ACTIVO = "ACTIVO"
    ESTADO_INACTIVO = "INACTIVO"
    ESTADO_AGOTADO = "AGOTADO"
    ESTADO_DESCONTINUADO = "DESCONTINUADO"

    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
        (ESTADO_AGOTADO, "Agotado"),
        (ESTADO_DESCONTINUADO, "Descontinuado"),
    ]

    # Unidades de medida
    UNIDAD_UNIDAD = "UNIDAD"
    UNIDAD_KG = "KG"
    UNIDAD_GR = "GR"
    UNIDAD_LB = "LB"
    UNIDAD_LITRO = "LITRO"
    UNIDAD_ML = "ML"
    UNIDAD_CAJA = "CAJA"
    UNIDAD_PAQUETE = "PAQUETE"

    UNIDAD_CHOICES = [
        (UNIDAD_UNIDAD, "Unidad"),
        (UNIDAD_KG, "Kilogramo"),
        (UNIDAD_GR, "Gramo"),
        (UNIDAD_LB, "Libra"),
        (UNIDAD_LITRO, "Litro"),
        (UNIDAD_ML, "Mililitro"),
        (UNIDAD_CAJA, "Caja"),
        (UNIDAD_PAQUETE, "Paquete"),
    ]

    # Información básica
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Producto",
        help_text="Nombre comercial del producto",
    )

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código/SKU",
        help_text="Código único del producto (puede ser código de barras, SKU, etc.)",
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del producto",
    )

    # Imagen del producto
    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
        verbose_name="Imagen del Producto",
        help_text="Imagen representativa del producto",
    )

    # Categoría
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="Categoría",
    )

    # Proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="Proveedor",
        help_text="Proveedor que suministra el producto",
    )

    # Precios
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Venta",
        help_text="Precio de venta al público (Bs.)",
    )

    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name="Costo",
        help_text="Costo de adquisición (Bs.) - Opcional",
    )

    # Inventario
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual",
        help_text="Cantidad disponible en inventario",
    )

    stock_minimo = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima antes de reorden",
    )

    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_CHOICES,
        default=UNIDAD_UNIDAD,
        verbose_name="Unidad de Medida",
    )

    # Fecha de vencimiento (para productos perecederos)
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Vencimiento",
        help_text="Fecha de vencimiento del producto (si aplica)",
    )

    # Promoción (opcional)
    promocion = models.ForeignKey(
        Promocion,
        on_delete=models.SET_NULL,
        related_name="productos",
        blank=True,
        null=True,
        verbose_name="Promoción",
        help_text="Promoción vigente aplicable al producto",
    )

    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado",
    )

    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="productos_creados",
        null=True,
        verbose_name="Creado por",
    )

    modificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="productos_modificados",
        null=True,
        verbose_name="Modificado por",
    )

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["categoria", "estado"]),
            models.Index(fields=["proveedor"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def clean(self):
        """Validaciones de negocio"""
        super().clean()

        # Validar que el precio sea mayor que el costo (solo si costo está presente y es mayor a 0)
        if self.costo and self.costo > 0 and self.precio < self.costo:
            raise ValidationError(
                {"precio": "El precio de venta no puede ser menor que el costo."}
            )

        # Validar código único
        if self.codigo:
            self.codigo = self.codigo.strip().upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def precio_con_descuento(self):
        """
        Calcula el precio con descuento si hay promoción vigente

        NOTA: Las promociones están diseñadas principalmente para membresías.
        Para productos, se usa el campo 'descuento' (porcentaje) de la promoción.
        """
        if self.promocion and self.promocion.esta_vigente:
            # El modelo Promocion tiene 'descuento' como porcentaje (ej: 15.00 para 15%)
            descuento = self.precio * (self.promocion.descuento / 100)
            return max(self.precio - descuento, 0)
        return self.precio

    @property
    def necesita_reposicion(self):
        """Indica si el producto necesita reposición"""
        return self.stock <= self.stock_minimo

    @property
    def stock_critico(self):
        """Indica si el stock está en nivel crítico (50% o menos del mínimo)"""
        if self.stock_minimo > 0:
            return self.stock <= (self.stock_minimo * 0.5)
        return self.stock == 0

    @property
    def dias_hasta_vencimiento(self):
        """Calcula los días hasta el vencimiento"""
        if self.fecha_vencimiento:
            from datetime import date

            delta = self.fecha_vencimiento - date.today()
            return delta.days
        return None

    @property
    def esta_vencido(self):
        """Indica si el producto está vencido"""
        dias = self.dias_hasta_vencimiento
        return dias is not None and dias < 0

    @property
    def proximo_a_vencer(self):
        """Indica si el producto está próximo a vencer (30 días o menos)"""
        dias = self.dias_hasta_vencimiento
        return dias is not None and 0 <= dias <= 30

    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia porcentual"""
        if self.costo and self.costo > 0:
            return ((self.precio - self.costo) / self.costo) * 100
        return None

    def actualizar_stock(self, cantidad, operacion="sumar"):
        """
        Actualiza el stock del producto
        operacion: 'sumar' (entrada) o 'restar' (venta)
        """
        if operacion == "sumar":
            self.stock += cantidad
        elif operacion == "restar":
            if self.stock >= cantidad:
                self.stock -= cantidad
            else:
                raise ValidationError("Stock insuficiente para realizar la operación.")

        # Actualizar estado si se agota
        if self.stock == 0:
            self.estado = self.ESTADO_AGOTADO
        elif self.estado == self.ESTADO_AGOTADO and self.stock > 0:
            self.estado = self.ESTADO_ACTIVO

        self.save()


class MovimientoInventario(TimeStampedModel):
    """
    Registro de movimientos de inventario para auditoría y trazabilidad
    Tipos: ENTRADA, SALIDA, AJUSTE
    """

    # Tipos de movimiento
    TIPO_ENTRADA = "ENTRADA"
    TIPO_SALIDA = "SALIDA"
    TIPO_AJUSTE = "AJUSTE"

    TIPO_CHOICES = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SALIDA, "Salida"),
        (TIPO_AJUSTE, "Ajuste"),
    ]

    # Relaciones
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="movimientos",
        verbose_name="Producto",
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="movimientos_inventario",
        verbose_name="Usuario que realizó el movimiento",
    )

    # Información del movimiento
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento",
    )

    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad",
        help_text="Cantidad del movimiento (siempre positivo)",
    )

    cantidad_anterior = models.IntegerField(
        verbose_name="Stock Anterior",
        help_text="Stock antes del movimiento",
    )

    cantidad_nueva = models.IntegerField(
        verbose_name="Stock Nuevo",
        help_text="Stock después del movimiento",
    )

    motivo = models.TextField(
        verbose_name="Motivo",
        help_text="Descripción del motivo del movimiento",
    )

    # Metadatos adicionales
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia",
        help_text="Número de documento, orden de compra, etc.",
    )

    class Meta:
        db_table = "movimiento_inventario"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["producto", "-created_at"]),
            models.Index(fields=["tipo", "-created_at"]),
            models.Index(fields=["usuario", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} - {self.cantidad} ({self.created_at.strftime('%Y-%m-%d')})"

    def clean(self):
        """Validaciones de negocio"""
        super().clean()

        if self.cantidad <= 0:
            raise ValidationError({"cantidad": "La cantidad debe ser mayor a 0."})

        if self.cantidad_nueva < 0:
            raise ValidationError(
                {"cantidad_nueva": "El stock resultante no puede ser negativo."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
