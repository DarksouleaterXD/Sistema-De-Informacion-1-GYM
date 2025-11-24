"""
CU29 - Registrar Proveedor
Modelo de Proveedor con validaciones de negocio
"""
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel


class Proveedor(TimeStampedModel):
    """
    Proveedor - Entidad para gestión de proveedores
    Campos obligatorios: razón_social, nit
    Validaciones: email válido, teléfono 7-15 dígitos
    Unicidad: NIT, razón_social
    Estado inicial: Activo
    """
    
    # Estados del proveedor
    ESTADO_ACTIVO = 'A'
    ESTADO_INACTIVO = 'I'
    ESTADO_SUSPENDIDO = 'S'
    
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
        (ESTADO_SUSPENDIDO, 'Suspendido'),
    ]
    
    # Validador de teléfono: 7-15 dígitos
    phone_validator = RegexValidator(
        regex=r'^\d{7,15}$',
        message='El teléfono debe contener entre 7 y 15 dígitos numéricos.'
    )
    
    # Campos obligatorios
    razon_social = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Razón Social",
        help_text="Nombre legal o comercial del proveedor"
    )
    
    nit = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="NIT/ID Fiscal",
        help_text="Número de Identificación Tributaria o ID fiscal"
    )
    
    # Campos opcionales con validaciones
    telefono = models.CharField(
        max_length=15,
        validators=[phone_validator],
        blank=True,
        verbose_name="Teléfono"
    )
    
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator(message='Ingrese un correo electrónico válido.')],
        blank=True,
        verbose_name="Email"
    )
    
    direccion = models.TextField(
        blank=True,
        verbose_name="Dirección",
        help_text="Dirección física del proveedor"
    )
    
    # Estado del proveedor
    estado = models.CharField(
        max_length=1,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado"
    )
    
    # Campos adicionales útiles
    contacto_nombre = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nombre de Contacto",
        help_text="Persona de contacto en la empresa proveedora"
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Observaciones adicionales sobre el proveedor"
    )
    
    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nit'], name='proveedor_nit_idx'),
            models.Index(fields=['razon_social'], name='proveedor_razon_idx'),
            models.Index(fields=['estado'], name='proveedor_estado_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['nit'],
                name='unique_proveedor_nit'
            ),
            models.UniqueConstraint(
                fields=['razon_social'],
                name='unique_proveedor_razon_social'
            ),
        ]
    
    def __str__(self):
        return f"{self.razon_social} (NIT: {self.nit})"
    
    def clean(self):
        """Validaciones a nivel de modelo"""
        super().clean()
        
        # Normalizar y validar NIT
        if self.nit:
            self.nit = self.nit.strip().upper()
            if not self.nit:
                raise ValidationError({'nit': 'El NIT es obligatorio.'})
        
        # Normalizar razón social
        if self.razon_social:
            self.razon_social = self.razon_social.strip()
            if not self.razon_social:
                raise ValidationError({'razon_social': 'La razón social es obligatoria.'})
        
        # Normalizar teléfono (solo dígitos)
        if self.telefono:
            self.telefono = ''.join(filter(str.isdigit, self.telefono))
        
        # Normalizar email
        if self.email:
            self.email = self.email.strip().lower()
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def esta_activo(self):
        """Verifica si el proveedor está activo"""
        return self.estado == self.ESTADO_ACTIVO
    
    def activar(self):
        """Activa el proveedor"""
        self.estado = self.ESTADO_ACTIVO
        self.save(update_fields=['estado', 'updated_at'])
    
    def desactivar(self):
        """Desactiva el proveedor"""
        self.estado = self.ESTADO_INACTIVO
        self.save(update_fields=['estado', 'updated_at'])
    
    def suspender(self):
        """Suspende el proveedor"""
        self.estado = self.ESTADO_SUSPENDIDO
        self.save(update_fields=['estado', 'updated_at'])
