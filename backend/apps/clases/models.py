from django.db import models
from apps.core.models import TimeStampedModel
from apps.core.constants import (
    ESTADOS_CLASE, CLASE_PROGRAMADA,
    ESTADOS_INSCRIPCION_CLASE, INSCRIPCION_CONFIRMADA
)
from apps.disciplinas.models import Disciplina
from apps.users.models import User


class Salon(TimeStampedModel):
    """
    Modelo para salones/salas del gimnasio
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Salón",
        help_text="Ej: Sala A, Sala Spinning, Sala Yoga"
    )
    capacidad = models.PositiveIntegerField(
        verbose_name="Capacidad Máxima",
        help_text="Número máximo de personas"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el salón está disponible"
    )

    class Meta:
        db_table = 'salon'
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad})"


class Clase(TimeStampedModel):
    """
    CU20: Modelo para clases programadas del gimnasio
    """
    
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name='clases',
        verbose_name="Disciplina"
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='clases_instructor',
        verbose_name="Instructor",
        help_text="Usuario con rol de instructor"
    )
    salon = models.ForeignKey(
        Salon,
        on_delete=models.PROTECT,
        related_name='clases',
        verbose_name="Salón"
    )
    fecha = models.DateField(
        verbose_name="Fecha de la Clase"
    )
    hora_inicio = models.TimeField(
        verbose_name="Hora de Inicio"
    )
    hora_fin = models.TimeField(
        verbose_name="Hora de Fin"
    )
    cupo_maximo = models.PositiveIntegerField(
        verbose_name="Cupo Máximo",
        help_text="Número máximo de participantes (basado en capacidad del salón)"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_CLASE,
        default=CLASE_PROGRAMADA,
        verbose_name="Estado"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    class Meta:
        db_table = 'clase'
        verbose_name = "Clase"
        verbose_name_plural = "Clases"
        ordering = ['-fecha', '-hora_inicio']
        # Constraint para evitar solapamiento de horarios por salón
        constraints = [
            models.UniqueConstraint(
                fields=['salon', 'fecha', 'hora_inicio'],
                name='unique_salon_fecha_hora'
            )
        ]

    def __str__(self):
        return f"{self.disciplina.nombre} - {self.fecha} {self.hora_inicio} ({self.instructor.get_full_name()})"

    @property
    def cupos_disponibles(self):
        """Calcula cupos disponibles basado en inscripciones"""
        inscritos = self.inscripciones.filter(estado='confirmada').count()
        return self.cupo_maximo - inscritos

    @property
    def esta_llena(self):
        """Verifica si la clase está llena"""
        return self.cupos_disponibles <= 0


class InscripcionClase(TimeStampedModel):
    """
    Modelo para inscripciones de clientes a clases
    """
    
    clase = models.ForeignKey(
        Clase,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name="Clase"
    )
    cliente = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='inscripciones_clases',
        verbose_name="Cliente"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_INSCRIPCION_CLASE,
        default=INSCRIPCION_CONFIRMADA,
        verbose_name="Estado"
    )
    fecha_inscripcion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Inscripción"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    class Meta:
        db_table = 'inscripcion_clase'
        verbose_name = "Inscripción a Clase"
        verbose_name_plural = "Inscripciones a Clases"
        ordering = ['-fecha_inscripcion']
        # Un cliente no puede inscribirse dos veces a la misma clase
        constraints = [
            models.UniqueConstraint(
                fields=['clase', 'cliente'],
                name='unique_cliente_clase'
            )
        ]

    def __str__(self):
        return f"{self.cliente.nombre_completo} - {self.clase}"
