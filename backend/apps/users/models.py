from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import TimeStampedModel
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import uuid


def _reset_token_ttl_hours():
    """Retorna el TTL (Time To Live) en horas para los tokens de reseteo de contraseña."""
    return getattr(settings, 'PASSWORD_RESET_TOKEN_TTL_HOURS', 24)


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
class PasswordResetToken(models.Model):
    """
    Token de recuperación de contraseña por email.
    - ÚNICO por token (UUID).
    - Expira automáticamente (TTL configurable).
    - Marcado como 'used' al confirmar.
    - Guarda IP y User-Agent para auditoría/seguridad.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    used = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "used"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"ResetToken({self.user_id}) - {self.created_at:%Y-%m-%d %H:%M}"

    # Helpers
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=_reset_token_ttl_hours())
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return timezone.now() > (self.expires_at or timezone.now())

    def is_valid(self) -> bool:
        return not self.used and not self.is_expired()

    def mark_as_used(self):
        if not self.used:
            self.used = True
            self.save(update_fields=["used"])