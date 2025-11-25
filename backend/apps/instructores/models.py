"""
Modelos para el módulo de Instructores
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel

User = get_user_model()


class Instructor(TimeStampedModel):
    """
    Modelo Instructor - Extiende la información del usuario con rol Instructor
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        verbose_name='Usuario'
    )
    
    # Información profesional
    especialidades = models.TextField(
        verbose_name='Especialidades',
        help_text='Disciplinas en las que se especializa (ej: Yoga, Spinning, CrossFit)'
    )
    
    certificaciones = models.TextField(
        blank=True,
        verbose_name='Certificaciones',
        help_text='Certificaciones y títulos profesionales'
    )
    
    experiencia_anos = models.PositiveIntegerField(
        default=0,
        verbose_name='Años de Experiencia'
    )
    
    # Información de contacto adicional
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    telefono_emergencia = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono de Emergencia'
    )
    
    # Información adicional
    biografia = models.TextField(
        blank=True,
        verbose_name='Biografía',
        help_text='Breve descripción del instructor'
    )
    
    foto_url = models.URLField(
        blank=True,
        verbose_name='URL de Foto',
        help_text='URL de la foto de perfil del instructor'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el instructor está actualmente activo'
    )
    
    fecha_ingreso = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Ingreso'
    )
    
    class Meta:
        db_table = 'instructor'
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructores'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario'], name='instructor_usuario_idx'),
            models.Index(fields=['activo'], name='instructor_activo_idx'),
        ]
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.especialidades}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del instructor"""
        return self.usuario.get_full_name()
    
    @property
    def email(self):
        """Retorna el email del usuario"""
        return self.usuario.email
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que el usuario tenga el rol de Instructor
        if self.usuario:
            from apps.roles.models import UserRole, Role
            try:
                rol_instructor = Role.objects.get(nombre='Instructor')
                if not UserRole.objects.filter(usuario=self.usuario, rol=rol_instructor).exists():
                    raise ValidationError({
                        'usuario': 'El usuario debe tener el rol de Instructor.'
                    })
            except Role.DoesNotExist:
                pass  # Si no existe el rol, permitir la creación
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
