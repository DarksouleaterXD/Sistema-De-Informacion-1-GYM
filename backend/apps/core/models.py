from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo base abstracto que proporciona campos de timestamp
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        abstract = True
