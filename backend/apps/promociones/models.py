from django.db import models
from apps.core.models import TimeStampedModel


class Promocion(TimeStampedModel):
    """
    Promocion - Tabla según PUML
    Campos: ID (PK), Nombre, Meses, Descuento, Fecha_Inicio, Fecha_Fin, Estado
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Promoción")
    meses = models.IntegerField(
        verbose_name="Meses de Duración",
        help_text="Cantidad de meses que dura la promoción"
    )
    descuento = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Descuento (%)",
        help_text="Porcentaje de descuento (ej: 15.00 para 15%)"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVA', 'Activa'),
            ('INACTIVA', 'Inactiva'),
            ('VENCIDA', 'Vencida'),
        ],
        default='ACTIVA',
        verbose_name="Estado"
    )

    class Meta:
        db_table = 'promocion'
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} - {self.descuento}% ({self.meses} meses)"

    @property
    def esta_vigente(self):
        """Verifica si la promoción está vigente"""
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.estado == 'ACTIVA' and self.fecha_inicio <= hoy <= self.fecha_fin
