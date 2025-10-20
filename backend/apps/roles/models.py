from django.db import models
from apps.core.models import TimeStampedModel


class Role(TimeStampedModel):
    """
    Roles - Tabla según PUML
    Campos: ID (PK), Nombre, Descripcion
    """
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción")
    
    # Relación Many-to-Many con Permiso a través de Rol_Permiso
    permisos = models.ManyToManyField(
        'Permiso',
        through='RolPermiso',
        related_name='roles',
        verbose_name="Permisos"
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Permiso(TimeStampedModel):
    """
    Permiso - Tabla según PUML
    Campos: ID (PK), Nombre, Descripcion
    """
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción")
    
    class Meta:
        db_table = 'permiso'
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class UserRole(TimeStampedModel):
    """
    Usuario_Rol - Tabla de relación Many-to-Many según PUML
    Campos: ID (PK), UsuarioId (FK), RolId (FK)
    """
    usuario = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    rol = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="Rol"
    )
    
    class Meta:
        db_table = 'usuario_rol'
        verbose_name = "Usuario-Rol"
        verbose_name_plural = "Usuarios-Roles"
        unique_together = [['usuario', 'rol']]
    
    def __str__(self):
        return f"{self.usuario} - {self.rol}"


class RolPermiso(TimeStampedModel):
    """
    Rol_Permiso - Tabla de relación Many-to-Many según PUML
    Campos: ID (PK), RolId (FK), PermisoId (FK)
    """
    rol = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="Rol"
    )
    permiso = models.ForeignKey(
        Permiso,
        on_delete=models.CASCADE,
        verbose_name="Permiso"
    )
    
    class Meta:
        db_table = 'rol_permiso'
        verbose_name = "Rol-Permiso"
        verbose_name_plural = "Roles-Permisos"
        unique_together = [['rol', 'permiso']]
    
    def __str__(self):
        return f"{self.rol} - {self.permiso}"
    
    def __str__(self):
        return self.name
