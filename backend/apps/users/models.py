from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Usuario - Tabla según PUML
    Campos: ID (PK), Nombre, Email, Contraseña
    """
    # ID es automático (PK)
    # Nombre lo tomamos de first_name y last_name heredados de AbstractUser
    email = models.EmailField(max_length=150, unique=True, verbose_name="Email")
    # Contraseña está manejada por AbstractUser (password field)
    
    # Relación Many-to-Many con Roles a través de Usuario_Rol
    roles = models.ManyToManyField(
        'roles.Role',
        through='roles.UserRole',
        related_name='users',
        verbose_name="Roles"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'usuario'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
