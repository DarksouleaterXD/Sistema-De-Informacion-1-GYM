"""
CU24 - Categorías de Productos
Modelo independiente para gestión de categorías
"""

from django.db import models
from apps.core.models import TimeStampedModel


class CategoriaProducto(TimeStampedModel):
    """
    Categoría de Productos
    Permite organizar los productos por tipo
    """

    nombre = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre de Categoría"
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código",
        help_text="Código único de la categoría",
    )

    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = "categoria_producto"
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
