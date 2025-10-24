from django.db import models
from apps.core.models import TimeStampedModel


class Promocion(TimeStampedModel):
    """
    Modelo para gestionar promociones y descuentos del gimnasio
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la promoción")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    tipo_descuento = models.CharField(
        max_length=20,
        choices=[
            ('PORCENTAJE', 'Porcentaje'),
            ('MONTO_FIJO', 'Monto Fijo')
        ],
        default='PORCENTAJE',
        verbose_name="Tipo de descuento"
    )
    valor_descuento = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Valor del descuento"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de fin")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código promocional"
    )

    class Meta:
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nombre} - {self.valor_descuento}{'%' if self.tipo_descuento == 'PORCENTAJE' else ' Bs.'}"

    @property
    def esta_vigente(self):
        """Verifica si la promoción está vigente"""
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.activo and self.fecha_inicio <= hoy <= self.fecha_fin
