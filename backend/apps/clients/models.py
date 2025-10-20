from django.db import models
from apps.core.models import TimeStampedModel


class Client(TimeStampedModel):
    """
    Cliente - Tabla según PUML
    Campos: ID (PK), Nombre, Apellido, Telefono, Peso, Altura, Experiencia
    """
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    apellido = models.CharField(max_length=50, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    altura = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="Altura (m)")
    experiencia = models.CharField(max_length=20, null=True, blank=True, verbose_name="Experiencia")

    class Meta:
        db_table = 'cliente'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def full_name(self):
        return f"{self.nombre} {self.apellido}"


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
    metodo_de_pago = models.CharField(max_length=30, verbose_name="Método de Pago")

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
    estado = models.CharField(max_length=20, verbose_name="Estado")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")

    class Meta:
        db_table = 'membresia'
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.inscripcion.cliente} - {self.estado} ({self.fecha_inicio} a {self.fecha_fin})"
