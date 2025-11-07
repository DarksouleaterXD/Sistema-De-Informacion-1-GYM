from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, time
from apps.core.constants import CLASE_PROGRAMADA, CLASE_EN_CURSO
from .models import Salon, Clase, InscripcionClase
from apps.disciplinas.models import Disciplina
from apps.disciplinas.serializers import DisciplinaSerializer
from apps.users.models import User
from apps.users.serializers import UserListSerializer
from apps.clients.models import Client
from apps.clients.serializers import ClientListSerializer


class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['id', 'nombre', 'capacidad', 'descripcion', 'activo', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_nombre(self, value):
        # Verificar nombre único (case-insensitive)
        nombre_lower = value.lower()
        queryset = Salon.objects.filter(nombre__iexact=nombre_lower)
        
        # Si estamos editando, excluir la instancia actual
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(f"Ya existe un salón con el nombre '{value}'")
        
        return value


class ClaseSerializer(serializers.ModelSerializer):
    disciplina_nombre = serializers.CharField(source='disciplina.nombre', read_only=True)
    instructor_nombre = serializers.SerializerMethodField()
    salon_nombre = serializers.CharField(source='salon.nombre', read_only=True)
    cupos_disponibles = serializers.ReadOnlyField()
    esta_llena = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Clase
        fields = [
            'id', 'disciplina', 'disciplina_nombre', 'instructor', 'instructor_nombre',
            'salon', 'salon_nombre', 'fecha', 'hora_inicio', 'hora_fin',
            'cupo_maximo', 'cupos_disponibles', 'esta_llena', 'estado', 'estado_display',
            'observaciones', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_instructor_nombre(self, obj):
        return obj.instructor.get_full_name()

    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que hora_fin sea mayor a hora_inicio
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise serializers.ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
                })

        # Validar que cupo_maximo no exceda capacidad del salón
        salon = data.get('salon')
        cupo_maximo = data.get('cupo_maximo')
        
        if salon and cupo_maximo:
            if cupo_maximo > salon.capacidad:
                raise serializers.ValidationError({
                    'cupo_maximo': f'El cupo máximo no puede exceder la capacidad del salón ({salon.capacidad})'
                })

        # Validar disponibilidad del salón (no solapamiento de horarios)
        fecha = data.get('fecha')
        salon = data.get('salon')
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')

        if fecha and salon and hora_inicio and hora_fin:
            # Buscar clases en el mismo salón, misma fecha que se solapen
            clases_conflicto = Clase.objects.filter(
                salon=salon,
                fecha=fecha,
                estado__in=[CLASE_PROGRAMADA, CLASE_EN_CURSO]
            ).filter(
                Q(hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)  # Solapamiento
            )

            # Si estamos editando, excluir la clase actual
            if self.instance:
                clases_conflicto = clases_conflicto.exclude(pk=self.instance.pk)

            if clases_conflicto.exists():
                clase_conf = clases_conflicto.first()
                raise serializers.ValidationError({
                    'salon': f'Conflicto de horarios: El salón ya está ocupado de {clase_conf.hora_inicio} a {clase_conf.hora_fin}'
                })

        # Validar disponibilidad del instructor (no puede tener dos clases al mismo tiempo)
        instructor = data.get('instructor')
        
        if fecha and instructor and hora_inicio and hora_fin:
            clases_instructor = Clase.objects.filter(
                instructor=instructor,
                fecha=fecha,
                estado__in=[CLASE_PROGRAMADA, CLASE_EN_CURSO]
            ).filter(
                Q(hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)
            )

            if self.instance:
                clases_instructor = clases_instructor.exclude(pk=self.instance.pk)

            if clases_instructor.exists():
                clase_conf = clases_instructor.first()
                raise serializers.ValidationError({
                    'instructor': f'El instructor ya tiene una clase programada de {clase_conf.hora_inicio} a {clase_conf.hora_fin}'
                })

        return data


class ClaseListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    disciplina_nombre = serializers.CharField(source='disciplina.nombre', read_only=True)
    instructor_nombre = serializers.SerializerMethodField()
    salon_nombre = serializers.CharField(source='salon.nombre', read_only=True)
    cupos_disponibles = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Clase
        fields = [
            'id', 'disciplina_nombre', 'instructor_nombre', 'salon_nombre',
            'fecha', 'hora_inicio', 'hora_fin', 'cupo_maximo', 'cupos_disponibles',
            'estado', 'estado_display'
        ]

    def get_instructor_nombre(self, obj):
        return obj.instructor.get_full_name()


class InscripcionClaseSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_ci = serializers.CharField(source='cliente.ci', read_only=True)
    clase_info = serializers.SerializerMethodField()
    disciplina_nombre = serializers.CharField(source='clase.disciplina.nombre', read_only=True)
    instructor_nombre = serializers.SerializerMethodField()
    fecha_clase = serializers.DateField(source='clase.fecha', read_only=True)
    hora_clase = serializers.TimeField(source='clase.hora_inicio', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = InscripcionClase
        fields = [
            'id', 'clase', 'clase_info', 'disciplina_nombre', 'instructor_nombre',
            'fecha_clase', 'hora_clase', 'cliente', 'cliente_nombre', 'cliente_ci',
            'estado', 'estado_display', 'fecha_inscripcion', 'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['fecha_inscripcion', 'created_at', 'updated_at']

    def get_clase_info(self, obj):
        return f"{obj.clase.disciplina.nombre} - {obj.clase.fecha} {obj.clase.hora_inicio}"

    def get_instructor_nombre(self, obj):
        return obj.clase.instructor.get_full_name()

    def validate(self, data):
        """
        CU21: Validar cupos disponibles y membresía activa del cliente
        """
        clase = data.get('clase')
        cliente = data.get('cliente')
        
        # Solo validar al crear nueva inscripción
        if not self.instance:
            # Validación 1: Verificar cupo disponible
            if clase and clase.esta_llena:
                raise serializers.ValidationError({
                    'clase': 'La clase ya está llena. No hay cupos disponibles.'
                })

            # Validación 2: Verificar que el cliente tenga membresía activa
            if cliente:
                # Importar aquí para evitar importaciones circulares
                from apps.membresias.models import Membresia
                from django.utils import timezone
                
                membresia_activa = Membresia.objects.filter(
                    cliente=cliente,
                    estado='activa',
                    fecha_inicio__lte=timezone.now().date(),
                    fecha_fin__gte=timezone.now().date()
                ).exists()
                
                if not membresia_activa:
                    raise serializers.ValidationError({
                        'cliente': f'El cliente {cliente.nombre_completo} no tiene una membresía activa.'
                    })

            # Validación 3: Verificar que el cliente no esté ya inscrito
            if clase and cliente:
                existe_inscripcion = InscripcionClase.objects.filter(
                    clase=clase,
                    cliente=cliente
                ).exists()
                
                if existe_inscripcion:
                    raise serializers.ValidationError(
                        f'El cliente {cliente.nombre_completo} ya está inscrito en esta clase.'
                    )

        return data


class InscripcionClaseListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de inscripciones"""
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_ci = serializers.CharField(source='cliente.ci', read_only=True)
    disciplina = serializers.CharField(source='clase.disciplina.nombre', read_only=True)
    fecha_clase = serializers.DateField(source='clase.fecha', read_only=True)
    hora_inicio = serializers.TimeField(source='clase.hora_inicio', read_only=True)
    instructor = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = InscripcionClase
        fields = [
            'id', 'cliente_nombre', 'cliente_ci', 'disciplina', 'fecha_clase',
            'hora_inicio', 'instructor', 'estado', 'estado_display', 'fecha_inscripcion'
        ]

    def get_instructor(self, obj):
        return obj.clase.instructor.get_full_name()

