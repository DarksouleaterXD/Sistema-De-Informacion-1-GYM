from django.db import models  # type: ignore
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.core.utils import validar_ci, normalizar_telefono
from apps.core.constants import NIVELES_EXPERIENCIA, EXPERIENCIA_PRINCIPIANTE


class Client(TimeStampedModel):
    """
    Cliente - Tabla según PUML
    Campos: ID (PK), Nombre, Apellido, Telefono, Peso, Altura, Experiencia
    """
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    apellido = models.CharField(max_length=50, verbose_name="Apellido")
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    # Campos adicionales según PUML
    peso = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Peso (kg)"
    )
    altura = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Altura (m)"
    )
    experiencia = models.CharField(
        max_length=20,
        choices=NIVELES_EXPERIENCIA,
        default=EXPERIENCIA_PRINCIPIANTE,
        verbose_name="Nivel de Experiencia"
    )
    
    fecha_registro = models.DateField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['ci'], name='cliente_ci_idx'),
            models.Index(fields=['telefono'], name='cliente_telefono_idx'),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.ci}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellido}"
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar CI
        if self.ci and not validar_ci(self.ci):
            raise ValidationError({
                'ci': 'La cédula de identidad debe ser un número válido entre 6 y 10 dígitos.'
            })
        
        # Normalizar teléfono
        if self.telefono:
            self.telefono = normalizar_telefono(self.telefono)
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para ejecutar validaciones"""
        self.clean()
        super().save(*args, **kwargs)
