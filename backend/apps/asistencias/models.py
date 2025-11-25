from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.clases.models import Clase, InscripcionClase
from apps.clients.models import Client
from apps.users.models import User


class EstadoAsistencia(models.TextChoices):
    """Estados posibles de una asistencia"""
    PRESENTE = 'presente', 'Presente'
    AUSENTE = 'ausente', 'Ausente'
    JUSTIFICADO = 'justificado', 'Justificado'
    TARDANZA = 'tardanza', 'Tardanza'


class AsistenciaClase(TimeStampedModel):
    """
    CU22: Modelo para el control de asistencia a clases
    Permite registrar la asistencia de clientes inscritos a una clase
    """
    
    inscripcion = models.ForeignKey(
        InscripcionClase,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name="Inscripción"
    )
    clase = models.ForeignKey(
        Clase,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name="Clase"
    )
    cliente = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name="Cliente"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.PRESENTE,
        verbose_name="Estado de Asistencia"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    hora_llegada = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de Llegada",
        help_text="Hora real de llegada del cliente"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones",
        help_text="Notas adicionales sobre la asistencia"
    )
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='asistencias_registradas',
        verbose_name="Registrado por",
        help_text="Usuario que registró la asistencia (Instructor, Admin, etc.)"
    )
    
    class Meta:
        db_table = 'asistencia_clase'
        verbose_name = "Asistencia a Clase"
        verbose_name_plural = "Asistencias a Clases"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['clase', 'fecha_registro']),
            models.Index(fields=['cliente', 'fecha_registro']),
            models.Index(fields=['estado']),
        ]
        # Un cliente solo puede tener un registro de asistencia por clase
        constraints = [
            models.UniqueConstraint(
                fields=['inscripcion', 'clase'],
                name='unique_asistencia_inscripcion_clase'
            )
        ]

    def __str__(self):
        return f"{self.cliente.nombre_completo} - {self.clase} ({self.get_estado_display()})"

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que la inscripción corresponde a la clase
        if self.inscripcion and self.clase:
            if self.inscripcion.clase_id != self.clase_id:
                raise ValidationError({
                    'inscripcion': 'La inscripción no corresponde a la clase seleccionada'
                })
        
        # Validar que el cliente de la inscripción coincide
        if self.inscripcion and self.cliente:
            if self.inscripcion.cliente_id != self.cliente_id:
                raise ValidationError({
                    'cliente': 'El cliente no corresponde a la inscripción seleccionada'
                })
        
        # Validar que la inscripción esté confirmada
        if self.inscripcion and self.inscripcion.estado != 'confirmada':
            raise ValidationError({
                'inscripcion': 'Solo se puede registrar asistencia para inscripciones confirmadas'
            })
        
        # Validar que no se registre asistencia antes de la fecha de la clase
        # Permitir registro el mismo día o después
        if self.clase and self.clase.fecha > timezone.now().date():
            raise ValidationError({
                'clase': f'No se puede registrar asistencia antes de la fecha de la clase. Fecha de la clase: {self.clase.fecha}, Fecha actual: {timezone.now().date()}'
            })

    def save(self, *args, **kwargs):
        # Si no se especifica hora de llegada y está presente, usar hora actual
        if self.estado == EstadoAsistencia.PRESENTE and not self.hora_llegada:
            self.hora_llegada = timezone.now().time()
        
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def es_tardia(self):
        """Verifica si la llegada fue después del inicio de la clase"""
        if self.hora_llegada and self.clase.hora_inicio:
            return self.hora_llegada > self.clase.hora_inicio
        return False

    @property
    def minutos_retraso(self):
        """Calcula minutos de retraso respecto al inicio de la clase"""
        if self.es_tardia:
            from datetime import datetime, timedelta
            inicio = datetime.combine(timezone.now().date(), self.clase.hora_inicio)
            llegada = datetime.combine(timezone.now().date(), self.hora_llegada)
            delta = llegada - inicio
            return int(delta.total_seconds() / 60)
        return 0
