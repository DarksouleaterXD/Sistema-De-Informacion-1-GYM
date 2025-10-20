from django.db import models
from apps.core.models import TimeStampedModel


class HistorialActividad(TimeStampedModel):
    """
    Historial_Actividad - Tabla según PUML
    Campos: ID (PK), UserId (FK), Accion, Fecha, IP, Hora
    """
    usuario = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='historial_actividades',
        verbose_name="Usuario"
    )
    accion = models.CharField(max_length=100, verbose_name="Acción")
    fecha = models.DateField(verbose_name="Fecha")
    ip = models.CharField(max_length=45, null=True, blank=True, verbose_name="IP")
    hora = models.TimeField(verbose_name="Hora")
    
    class Meta:
        db_table = 'historial_actividad'
        verbose_name = "Historial de Actividad"
        verbose_name_plural = "Historial de Actividades"
        ordering = ['-fecha', '-hora']
    
    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha} {self.hora}"
