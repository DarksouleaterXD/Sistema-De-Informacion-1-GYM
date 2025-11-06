from rest_framework import serializers
from .models import Membresia, InscripcionMembresia, PlanMembresia, MembresiaPromocion
from apps.clients.serializers import ClientListSerializer


class PlanMembresiaSerializer(serializers.ModelSerializer):
    """Serializer para Plan de Membresía"""
    
    class Meta:
        model = PlanMembresia
        fields = [
            'id',
            'nombre',
            'duracion',
            'precio_base',
            'descripcion',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_duracion(self, value):
        """Validar que la duración sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La duración debe ser mayor a 0 días")
        return value
    
    def validate_precio_base(self, value):
        """Validar que el precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio base debe ser mayor a 0")
        return value


class InscripcionMembresiaSerializer(serializers.ModelSerializer):
    """Serializer para Inscripción de Membresía"""
    cliente_info = ClientListSerializer(source='cliente', read_only=True)
    metodo_de_pago_display = serializers.CharField(source='get_metodo_de_pago_display', read_only=True)
    
    class Meta:
        model = InscripcionMembresia
        fields = [
            'id',
            'cliente',
            'cliente_info',
            'monto',
            'metodo_de_pago',
            'metodo_de_pago_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_monto(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class MembresiaPromocionSerializer(serializers.ModelSerializer):
    """Serializer para la relación Membresía-Promoción"""
    promocion_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MembresiaPromocion
        fields = [
            'id',
            'membresia',
            'promocion',
            'promocion_info',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_promocion_info(self, obj):
        """Información de la promoción"""
        return {
            'id': obj.promocion.id,
            'nombre': obj.promocion.nombre,
            'descuento': obj.promocion.descuento,
            'meses': obj.promocion.meses
        }


class MembresiaSerializer(serializers.ModelSerializer):
    """Serializer completo para Membresía"""
    inscripcion_info = InscripcionMembresiaSerializer(source='inscripcion', read_only=True)
    plan_info = PlanMembresiaSerializer(source='plan', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    usuario_registro_info = serializers.SerializerMethodField()
    promociones_aplicadas = serializers.SerializerMethodField()
    dias_restantes = serializers.ReadOnlyField()
    esta_activa = serializers.ReadOnlyField()
    duracion_dias = serializers.ReadOnlyField()
    
    class Meta:
        model = Membresia
        fields = [
            'id',
            'inscripcion',
            'inscripcion_info',
            'plan',
            'plan_info',
            'usuario_registro',
            'usuario_registro_info',
            'estado',
            'estado_display',
            'fecha_inicio',
            'fecha_fin',
            'promociones_aplicadas',
            'dias_restantes',
            'esta_activa',
            'duracion_dias',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_usuario_registro_info(self, obj):
        """Información del usuario que registró"""
        if obj.usuario_registro:
            return {
                'id': obj.usuario_registro.id,
                'username': obj.usuario_registro.username,
                'email': obj.usuario_registro.email
            }
        return None
    
    def get_promociones_aplicadas(self, obj):
        """Lista de promociones aplicadas a esta membresía"""
        return [
            {
                'id': promo.id,
                'nombre': promo.nombre,
                'descuento': promo.descuento,
                'meses': promo.meses
            }
            for promo in obj.promociones.all()
        ]
    
    def validate(self, data):
        """Validaciones cruzadas"""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        
        return data


class MembresiaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de Membresías"""
    cliente_nombre = serializers.CharField(source='inscripcion.cliente.nombre_completo', read_only=True)
    cliente_ci = serializers.CharField(source='inscripcion.cliente.ci', read_only=True)
    plan_nombre = serializers.CharField(source='plan.nombre', read_only=True)
    monto = serializers.DecimalField(source='inscripcion.monto', max_digits=10, decimal_places=2, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dias_restantes = serializers.ReadOnlyField()
    esta_activa = serializers.ReadOnlyField()
    
    class Meta:
        model = Membresia
        fields = [
            'id',
            'cliente_nombre',
            'cliente_ci',
            'plan_nombre',
            'monto',
            'estado',
            'estado_display',
            'fecha_inicio',
            'fecha_fin',
            'dias_restantes',
            'esta_activa'
        ]


class MembresiaCreateSerializer(serializers.Serializer):
    """Serializer para crear Membresía con Inscripción en una sola operación"""
    # Datos de Inscripción
    cliente = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)
    metodo_de_pago = serializers.ChoiceField(choices=['efectivo', 'tarjeta', 'transferencia', 'qr'])
    
    # Datos de Membresía
    plan = serializers.IntegerField()  # ✨ NUEVO: Campo plan requerido
    promociones = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )  # ✨ NUEVO: Promociones opcionales (M2M)
    estado = serializers.ChoiceField(choices=['activo', 'vencido', 'suspendido'])
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    
    def validate_monto(self, value):
        """Validar monto positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value
    
    def validate(self, data):
        """Validaciones cruzadas"""
        from apps.clients.models import Client
        from apps.promociones.models import Promocion
        
        # Validar que el cliente existe
        try:
            Client.objects.get(pk=data['cliente'])
        except Client.DoesNotExist:
            raise serializers.ValidationError({
                'cliente': 'El cliente no existe'
            })
        
        # ✨ NUEVO: Validar que el plan existe
        try:
            PlanMembresia.objects.get(pk=data['plan'])
        except PlanMembresia.DoesNotExist:
            raise serializers.ValidationError({
                'plan': 'El plan de membresía no existe'
            })
        
        # ✨ NUEVO: Validar promociones si se proporcionan
        if 'promociones' in data and data['promociones']:
            promociones_ids = data['promociones']
            promociones_count = Promocion.objects.filter(id__in=promociones_ids).count()
            if promociones_count != len(promociones_ids):
                raise serializers.ValidationError({
                    'promociones': 'Una o más promociones no existen'
                })
        
        # Validar fechas
        if data['fecha_fin'] <= data['fecha_inicio']:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
            })
        
        return data
    
    def create(self, validated_data):
        """Crear Inscripción y Membresía en una transacción"""
        from apps.clients.models import Client
        from django.db import transaction
        
        # Extraer promociones (opcional)
        promociones_ids = validated_data.pop('promociones', [])
        
        with transaction.atomic():
            # Crear Inscripción
            inscripcion = InscripcionMembresia.objects.create(
                cliente_id=validated_data['cliente'],
                monto=validated_data['monto'],
                metodo_de_pago=validated_data['metodo_de_pago']
            )
            
            # Crear Membresía
            membresia = Membresia.objects.create(
                inscripcion=inscripcion,
                plan_id=validated_data['plan'],  # ✨ NUEVO: Asignar plan
                usuario_registro=self.context['request'].user,
                estado=validated_data['estado'],
                fecha_inicio=validated_data['fecha_inicio'],
                fecha_fin=validated_data['fecha_fin']
            )
            
            # ✨ NUEVO: Asociar promociones si se proporcionan
            if promociones_ids:
                membresia.promociones.set(promociones_ids)
            
            return membresia


class MembresiaEstadoVigenciaSerializer(serializers.ModelSerializer):
    """
    Serializer para consultar Estado y Vigencia de Membresía
    CU17: Consultar Estado/Vigencia de Membresía
    """
    cliente = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dias_restantes = serializers.ReadOnlyField()
    dias_transcurridos = serializers.SerializerMethodField()
    porcentaje_uso = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()
    promociones = serializers.SerializerMethodField()
    
    class Meta:
        model = Membresia
        fields = [
            'id',
            'cliente',
            'plan',
            'estado',
            'estado_display',
            'fecha_inicio',
            'fecha_fin',
            'dias_restantes',
            'dias_transcurridos',
            'porcentaje_uso',
            'vigente',
            'promociones',
            'created_at',
        ]
    
    def get_cliente(self, obj):
        """Información del cliente"""
        return {
            'id': obj.inscripcion.cliente.id,
            'nombre_completo': obj.inscripcion.cliente.nombre_completo,
            'ci': obj.inscripcion.cliente.ci,
            'telefono': obj.inscripcion.cliente.telefono,
        }
    
    def get_plan(self, obj):
        """Información del plan"""
        return {
            'id': obj.plan.id,
            'nombre': obj.plan.nombre,
            'duracion': obj.plan.duracion,
            'precio_base': str(obj.plan.precio_base),
        }
    
    def get_dias_transcurridos(self, obj):
        """Calcula los días transcurridos desde el inicio"""
        from datetime import date
        if obj.fecha_inicio:
            dias = (date.today() - obj.fecha_inicio).days
            return max(0, dias)
        return 0
    
    def get_porcentaje_uso(self, obj):
        """Calcula el porcentaje de uso de la membresía"""
        if obj.duracion_dias > 0:
            dias_transcurridos = self.get_dias_transcurridos(obj)
            porcentaje = (dias_transcurridos / obj.duracion_dias) * 100
            return round(min(100, porcentaje), 2)
        return 0
    
    def get_vigente(self, obj):
        """Determina si la membresía está vigente"""
        from datetime import date
        from apps.core.constants import ESTADO_ACTIVO, ESTADO_SUSPENDIDO
        
        # Vigente si está activa o suspendida y no ha vencido
        esta_en_periodo = obj.fecha_fin >= date.today()
        estado_valido = obj.estado in [ESTADO_ACTIVO, ESTADO_SUSPENDIDO]
        
        return esta_en_periodo and estado_valido
    
    def get_promociones(self, obj):
        """Lista de promociones aplicadas"""
        return [
            {
                'id': promo.id,
                'nombre': promo.nombre,
                'descuento': str(promo.descuento),
            }
            for promo in obj.promociones.all()
        ]
