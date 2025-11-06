from django.db import models
from apps.core.models import TimeStampedModel


class Disciplina(TimeStampedModel):
    """
    Disciplina - CU19: Gestionar Disciplinas
    Representa las diferentes disciplinas o actividades que ofrece el gimnasio
    Ejemplo: CrossFit, Yoga, Spinning, Zumba, Boxeo, etc.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Disciplina",
        help_text="Nombre único de la disciplina (ej: CrossFit, Yoga, Spinning)"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de la disciplina"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la disciplina está activa y disponible"
    )
    
    class Meta:
        db_table = 'disciplina'
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
