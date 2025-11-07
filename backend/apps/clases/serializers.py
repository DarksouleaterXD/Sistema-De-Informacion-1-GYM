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
    clase_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = InscripcionClase
        fields = [
            'id', 'clase', 'clase_info', 'cliente', 'cliente_nombre',
            'estado', 'estado_display', 'fecha_inscripcion', 'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['fecha_inscripcion', 'created_at', 'updated_at']

    def get_clase_info(self, obj):
        return f"{obj.clase.disciplina.nombre} - {obj.clase.fecha} {obj.clase.hora_inicio}"

    def validate(self, data):
        """Validar que haya cupos disponibles"""
        clase = data.get('clase')
        
        if clase and not self.instance:  # Solo al crear
            if clase.esta_llena:
                raise serializers.ValidationError({
                    'clase': 'La clase ya está llena. No hay cupos disponibles.'
                })

        return data
