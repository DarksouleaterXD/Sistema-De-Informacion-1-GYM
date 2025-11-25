from django.db import models
from apps.core.models import TimeStampedModel

class Category(TimeStampedModel):
    """
    Categoría de Productos
    Campos: ID (PK), Nombre, Descripción, Activo
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = 'categoria_producto'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
