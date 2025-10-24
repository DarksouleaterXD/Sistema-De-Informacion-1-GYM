from django.db import models
from apps.core.models import TimeStampedModel
from apps.core.constants import METODOS_PAGO, ESTADOS_MEMBRESIA
from apps.clients.models import Client


class InscripcionMembresia(TimeStampedModel):
    """
    Inscripcion_Membresia - Tabla según PUML
    Campos: ID (PK), ClienteId (FK), Monto, MetodoDePago
    """
    cliente = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='inscripciones',
        verbose_name="Cliente"
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    metodo_de_pago = models.CharField(
        max_length=30, 
        choices=METODOS_PAGO,
        verbose_name="Método de Pago"
    )

    class Meta:
        db_table = 'inscripcion_membresia'
        verbose_name = 'Inscripción Membresía'
        verbose_name_plural = 'Inscripciones Membresía'

    def __str__(self):
        return f"{self.cliente} - ${self.monto}"


class Membresia(TimeStampedModel):
    """
    Membresia - Tabla según PUML
    Campos: ID (PK), InscripcionId (FK), PlanId (FK), UsuarioRegistroId (FK), 
            Estado, Fecha_Inicio, Fecha_Fin
    """
    inscripcion = models.OneToOneField(
        InscripcionMembresia,
        on_delete=models.CASCADE,
        related_name='membresia',
        verbose_name="Inscripción"
    )
    # plan_id lo agregaremos cuando implementemos Plan_Membresia
    usuario_registro = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='membresias_registradas',
        verbose_name="Usuario que Registró"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_MEMBRESIA,
        verbose_name="Estado"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")

    class Meta:
        db_table = 'membresia'
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.inscripcion.cliente} - {self.estado} ({self.fecha_inicio} a {self.fecha_fin})"
    
    @property
    def dias_restantes(self):
        """Retorna los días restantes de la membresía"""
        from apps.core.utils import dias_restantes
        return dias_restantes(self.fecha_fin)
    
    @property
    def esta_activa(self):
        """Verifica si la membresía está activa"""
        from apps.core.utils import esta_activo
        from apps.core.constants import ESTADO_ACTIVO
        return self.estado == ESTADO_ACTIVO and esta_activo(self.fecha_fin)
    
    @property
    def duracion_dias(self):
        """Calcula la duración total en días de la membresía"""
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days
        return 0