from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class HistorialActividad(TimeStampedModel):
    """
    Historial de Actividad (Bitácora) - Auditoría del sistema
    Registra todas las acciones importantes de los usuarios
    """
    
    TIPO_ACCION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('create_user', 'Crear usuario'),
        ('update_user', 'Actualizar usuario'),
        ('delete_user', 'Eliminar usuario'),
        ('create_role', 'Crear rol'),
        ('update_role', 'Actualizar rol'),
        ('delete_role', 'Eliminar rol'),
        ('assign_role', 'Asignar rol'),
        ('remove_role', 'Remover rol'),
        ('create_client', 'Crear cliente'),
        ('update_client', 'Actualizar cliente'),
        ('delete_client', 'Eliminar cliente'),
        ('other', 'Otra acción'),
    ]
    
    NIVEL_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
    ]
    
    # Usuario que realizó la acción
    usuario = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='historial_actividades',
        verbose_name="Usuario"
    )
    
    # Detalles de la acción
    tipo_accion = models.CharField(
        max_length=50, 
        choices=TIPO_ACCION_CHOICES,
        default='other',
        verbose_name="Tipo de Acción"
    )
    accion = models.CharField(max_length=100, verbose_name="Acción")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # Nivel de severidad
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='info',
        verbose_name="Nivel"
    )
    
    # Información de la sesión
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    # Timestamp
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")
    
    # Datos adicionales en JSON
    datos_adicionales = models.JSONField(default=dict, blank=True, verbose_name="Datos Adicionales")
    
    # Campos legacy (para compatibilidad)
    fecha = models.DateField(null=True, blank=True, verbose_name="Fecha")
    hora = models.TimeField(null=True, blank=True, verbose_name="Hora")
    ip = models.CharField(max_length=45, null=True, blank=True, verbose_name="IP (Legacy)")
    
    class Meta:
        db_table = 'historial_actividad'
        verbose_name = "Historial de Actividad"
        verbose_name_plural = "Historial de Actividades"
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['usuario', '-fecha_hora']),
            models.Index(fields=['tipo_accion', '-fecha_hora']),
            models.Index(fields=['nivel', '-fecha_hora']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"{usuario_str} - {self.accion} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def save(self, *args, **kwargs):
        # Sincronizar fecha y hora con fecha_hora para compatibilidad
        if self.fecha_hora and not self.fecha:
            self.fecha = self.fecha_hora.date()
        if self.fecha_hora and not self.hora:
            self.hora = self.fecha_hora.time()
        if self.ip_address and not self.ip:
            self.ip = str(self.ip_address)
        super().save(*args, **kwargs)
    
    @classmethod
    def log_activity(cls, usuario, tipo_accion, accion, descripcion="", nivel="info", 
                     ip_address=None, user_agent=None, datos_adicionales=None):
        """
        Método helper para registrar actividades fácilmente.
        
        Uso:
            Bitacora.log_activity(
                usuario=request.user,
                tipo_accion="login",
                accion="Inicio de sesión",
                descripcion="Usuario ingresó al sistema",
                nivel="info",
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0...",
                datos_adicionales={"some": "data"}
            )
        """
        return cls.objects.create(
            usuario=usuario,
            tipo_accion=tipo_accion,
            accion=accion,
            descripcion=descripcion,
            nivel=nivel,
            ip_address=ip_address,
            user_agent=user_agent,
            datos_adicionales=datos_adicionales or {},
        )
