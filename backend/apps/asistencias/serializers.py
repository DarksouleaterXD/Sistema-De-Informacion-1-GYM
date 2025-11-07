from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from .models import AsistenciaClase, EstadoAsistencia
from apps.clases.models import Clase, InscripcionClase
from apps.clients.models import Client
from apps.clients.serializers import ClientListSerializer
from apps.clases.serializers import ClaseListSerializer


class AsistenciaClaseSerializer(serializers.ModelSerializer):
    """Serializer completo para asistencias"""
    
    # Campos relacionados (solo lectura)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    clase_info = serializers.SerializerMethodField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    registrado_por_nombre = serializers.CharField(source='registrado_por.get_full_name', read_only=True)
    es_tardia = serializers.ReadOnlyField()
    minutos_retraso = serializers.ReadOnlyField()
    
    class Meta:
        model = AsistenciaClase
        fields = [
            'id', 'inscripcion', 'clase', 'cliente', 'cliente_nombre',
            'estado', 'estado_display', 'fecha_registro', 'hora_llegada',
            'observaciones', 'registrado_por', 'registrado_por_nombre',
            'clase_info', 'es_tardia', 'minutos_retraso',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['fecha_registro', 'created_at', 'updated_at']

    def get_clase_info(self, obj):
        """Información resumida de la clase"""
        return {
            'id': obj.clase.id,
            'disciplina': obj.clase.disciplina.nombre,
            'fecha': obj.clase.fecha,
            'hora_inicio': obj.clase.hora_inicio,
            'hora_fin': obj.clase.hora_fin,
            'salon': obj.clase.salon.nombre,
        }

    def validate(self, data):
        """Validaciones personalizadas"""
        inscripcion = data.get('inscripcion')
        clase = data.get('clase')
        cliente = data.get('cliente')
        
        # Validar que la inscripción corresponde a la clase
        if inscripcion and clase:
            if inscripcion.clase_id != clase.id:
                raise serializers.ValidationError({
                    'inscripcion': 'La inscripción no corresponde a la clase seleccionada'
                })
        
        # Validar que el cliente corresponde a la inscripción
        if inscripcion and cliente:
            if inscripcion.cliente_id != cliente.id:
                raise serializers.ValidationError({
                    'cliente': 'El cliente no corresponde a la inscripción'
                })
        
        # Validar que la inscripción está confirmada
        if inscripcion and inscripcion.estado != 'confirmada':
            raise serializers.ValidationError({
                'inscripcion': 'Solo se puede registrar asistencia para inscripciones confirmadas'
            })
        
        # Validar que no existe ya un registro de asistencia
        if inscripcion and clase:
            if self.instance is None:  # Solo en creación
                if AsistenciaClase.objects.filter(inscripcion=inscripcion, clase=clase).exists():
                    raise serializers.ValidationError(
                        'Ya existe un registro de asistencia para este cliente en esta clase'
                    )
        
        return data


class AsistenciaClaseListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_ci = serializers.CharField(source='cliente.ci', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    disciplina = serializers.CharField(source='clase.disciplina.nombre', read_only=True)
    es_tardia = serializers.ReadOnlyField()
    
    class Meta:
        model = AsistenciaClase
        fields = [
            'id', 'cliente', 'cliente_nombre', 'cliente_ci',
            'estado', 'estado_display', 'hora_llegada', 'fecha_registro',
            'disciplina', 'es_tardia', 'observaciones'
        ]


class RegistrarAsistenciaSerializer(serializers.Serializer):
    """
    Serializer para registrar asistencia de forma simplificada
    Solo requiere la inscripción y el estado
    """
    inscripcion_id = serializers.IntegerField()
    estado = serializers.ChoiceField(
        choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.PRESENTE
    )
    hora_llegada = serializers.TimeField(required=False, allow_null=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    def validate_inscripcion_id(self, value):
        """Validar que existe la inscripción"""
        try:
            inscripcion = InscripcionClase.objects.select_related(
                'clase', 'cliente'
            ).get(id=value)
            return inscripcion
        except InscripcionClase.DoesNotExist:
            raise serializers.ValidationError('La inscripción no existe')
    
    def validate(self, data):
        """Validaciones adicionales"""
        inscripcion = data['inscripcion_id']  # Ya es el objeto
        
        # Validar que no existe asistencia previa
        if AsistenciaClase.objects.filter(inscripcion=inscripcion).exists():
            raise serializers.ValidationError(
                'Ya existe un registro de asistencia para esta inscripción'
            )
        
        return data
    
    def create(self, validated_data):
        """Crear registro de asistencia"""
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        inscripcion = validated_data['inscripcion_id']
        user = self.context['request'].user
        
        try:
            asistencia = AsistenciaClase.objects.create(
                inscripcion=inscripcion,
                clase=inscripcion.clase,
                cliente=inscripcion.cliente,
                estado=validated_data['estado'],
                hora_llegada=validated_data.get('hora_llegada'),
                observaciones=validated_data.get('observaciones', ''),
                registrado_por=user
            )
            return asistencia
        except DjangoValidationError as e:
            # Convertir ValidationError de Django a DRF
            if hasattr(e, 'message_dict'):
                raise serializers.ValidationError(e.message_dict)
            else:
                raise serializers.ValidationError(str(e))


class RegistrarAsistenciasMasivasSerializer(serializers.Serializer):
    """
    Serializer para registrar múltiples asistencias a la vez
    Útil para marcar asistencia de toda una clase
    """
    clase_id = serializers.IntegerField()
    asistencias = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_clase_id(self, value):
        """Validar que existe la clase"""
        try:
            clase = Clase.objects.get(id=value)
            return clase
        except Clase.DoesNotExist:
            raise serializers.ValidationError('La clase no existe')
    
    def validate_asistencias(self, value):
        """Validar estructura de cada asistencia"""
        for item in value:
            if 'inscripcion_id' not in item:
                raise serializers.ValidationError('Falta inscripcion_id en algún registro')
            if 'estado' not in item:
                raise serializers.ValidationError('Falta estado en algún registro')
            if item['estado'] not in dict(EstadoAsistencia.choices):
                raise serializers.ValidationError(f"Estado inválido: {item['estado']}")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Registrar múltiples asistencias en una transacción"""
        clase = validated_data['clase_id']
        asistencias_data = validated_data['asistencias']
        user = self.context['request'].user
        
        asistencias_creadas = []
        errores = []
        
        for data in asistencias_data:
            try:
                inscripcion = InscripcionClase.objects.select_related(
                    'cliente'
                ).get(id=data['inscripcion_id'], clase=clase)
                
                # Verificar que no existe ya
                if AsistenciaClase.objects.filter(inscripcion=inscripcion).exists():
                    errores.append(f"Cliente {inscripcion.cliente.nombre_completo}: Ya registrado")
                    continue
                
                asistencia = AsistenciaClase.objects.create(
                    inscripcion=inscripcion,
                    clase=clase,
                    cliente=inscripcion.cliente,
                    estado=data['estado'],
                    hora_llegada=data.get('hora_llegada'),
                    observaciones=data.get('observaciones', ''),
                    registrado_por=user
                )
                asistencias_creadas.append(asistencia)
                
            except InscripcionClase.DoesNotExist:
                errores.append(f"Inscripción {data['inscripcion_id']}: No encontrada")
            except Exception as e:
                errores.append(f"Inscripción {data['inscripcion_id']}: {str(e)}")
        
        return {
            'creadas': len(asistencias_creadas),
            'errores': errores,
            'asistencias': asistencias_creadas
        }
