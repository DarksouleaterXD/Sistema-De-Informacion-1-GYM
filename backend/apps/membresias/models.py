from django.db import models
from apps.core.models import TimeStampedModel
from apps.core.constants import METODOS_PAGO, ESTADOS_MEMBRESIA
from apps.clients.models import Client


class PlanMembresia(TimeStampedModel):
    """
    Plan_Membresia - Tabla según PUML
    Campos: ID (PK), Nombre, Duracion, Precio_base, Descripcion
    """
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Plan")
    duracion = models.IntegerField(
        verbose_name="Duración (días)",
        help_text="Duración del plan en días"
    )
    precio_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio Base"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )

    class Meta:
        db_table = 'plan_membresia'
        verbose_name = 'Plan de Membresía'
        verbose_name_plural = 'Planes de Membresía'
        ordering = ['duracion']

    def __str__(self):
        return f"{self.nombre} - {self.duracion} días (Bs. {self.precio_base})"


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
    plan = models.ForeignKey(
        PlanMembresia,
        on_delete=models.PROTECT,
        related_name='membresias',
        verbose_name="Plan de Membresía"
    )
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
    
    # Relación Many-to-Many con Promocion a través de Membresia_Promocion
    promociones = models.ManyToManyField(
        'promociones.Promocion',
        through='MembresiaPromocion',
        related_name='membresias',
        blank=True,
        verbose_name="Promociones Aplicadas"
    )

    class Meta:
        db_table = 'membresia'
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.inscripcion.cliente} - {self.plan.nombre} ({self.estado})"
    
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


class MembresiaPromocion(TimeStampedModel):
    """
    Membresia_Promocion - Tabla de relación Many-to-Many según PUML
    Campos: ID (PK), MembresiaId (FK), PromocionId (FK)
    """
    membresia = models.ForeignKey(
        Membresia,
        on_delete=models.CASCADE,
        verbose_name="Membresía"
    )
    promocion = models.ForeignKey(
        'promociones.Promocion',
        on_delete=models.CASCADE,
        verbose_name="Promoción"
    )

    class Meta:
        db_table = 'membresia_promocion'
        verbose_name = "Membresía-Promoción"
        verbose_name_plural = "Membresías-Promociones"
        unique_together = [['membresia', 'promocion']]

    def __str__(self):
        return f"{self.membresia} - {self.promocion}"
