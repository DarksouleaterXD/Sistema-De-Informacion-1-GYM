from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import datetime, timedelta

from .models import AsistenciaClase, EstadoAsistencia
from .serializers import (
    AsistenciaClaseSerializer,
    AsistenciaClaseListSerializer,
    RegistrarAsistenciaSerializer,
    RegistrarAsistenciasMasivasSerializer
)
from apps.core.permissions import HasPermission, PermissionCodes
from apps.clases.models import Clase, InscripcionClase


class AsistenciaClaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de asistencias a clases
    
    CU22: Controlar Asistencia a Clase
    - Superusuario, Administrador e Instructor pueden registrar asistencias
    - Se puede registrar asistencia individual o masiva
    - Consultas por clase, cliente, rango de fechas
    """
    
    permission_classes = [IsAuthenticated, HasPermission]
    serializer_class = AsistenciaClaseSerializer
    filterset_fields = ['estado', 'clase', 'cliente']
    search_fields = ['cliente__nombre', 'cliente__apellido', 'cliente__ci', 'observaciones']
    ordering_fields = ['fecha_registro', 'hora_llegada', 'estado']
    ordering = ['-fecha_registro']
    
    def get_queryset(self):
        """
        Filtrar asistencias según permisos del usuario
        """
        queryset = AsistenciaClase.objects.select_related(
            'cliente', 'clase', 'clase__disciplina', 'clase__salon',
            'inscripcion', 'registrado_por'
        ).all()
        
        # Filtros opcionales
        clase_id = self.request.query_params.get('clase_id')
        if clase_id:
            queryset = queryset.filter(clase_id=clase_id)
        
        cliente_id = self.request.query_params.get('cliente_id')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(clase__fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(clase__fecha__lte=fecha_hasta)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer simplificado para listados"""
        if self.action == 'list':
            return AsistenciaClaseListSerializer
        return AsistenciaClaseSerializer
    
    def get_permissions_required(self):
        """Definir permisos según la acción"""
        permission_map = {
            'list': [PermissionCodes.ASISTENCIA_VIEW],
            'retrieve': [PermissionCodes.ASISTENCIA_VIEW_DETAILS],
            'create': [PermissionCodes.ASISTENCIA_CREATE],
            'update': [PermissionCodes.ASISTENCIA_EDIT],
            'partial_update': [PermissionCodes.ASISTENCIA_EDIT],
            'destroy': [PermissionCodes.ASISTENCIA_DELETE],
            'registrar_asistencia': [PermissionCodes.ASISTENCIA_CREATE],
            'registrar_masivo': [PermissionCodes.ASISTENCIA_CREATE],
            'obtener_inscritos': [PermissionCodes.ASISTENCIA_VIEW],
            'estadisticas_clase': [PermissionCodes.ASISTENCIA_VIEW],
            'estadisticas_cliente': [PermissionCodes.ASISTENCIA_VIEW],
        }
        return permission_map.get(self.action, [])
    
    def perform_create(self, serializer):
        """Registrar usuario que crea la asistencia"""
        serializer.save(registrado_por=self.request.user)
    
    def perform_update(self, serializer):
        """Actualizar asistencia"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Eliminar asistencia"""
        instance.delete()
    
    @action(detail=False, methods=['post'], url_path='registrar')
    def registrar_asistencia(self, request):
        """
        POST /api/asistencias/registrar/
        
        Registrar asistencia de forma simplificada
        Body: { "inscripcion_id": 1, "estado": "presente", "observaciones": "..." }
        """
        import sys
        print("=" * 80, file=sys.stderr)
        print(f"📥 DATOS RECIBIDOS: {request.data}", file=sys.stderr)
        print(f"📥 USUARIO: {request.user}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        sys.stderr.flush()
        
        serializer = RegistrarAsistenciaSerializer(
            data=request.data,
            context={'request': request}
        )
        
        is_valid = serializer.is_valid()
        print(f"🔍 Serializer válido: {is_valid}", file=sys.stderr)
        if not is_valid:
            print(f"❌ ERRORES: {serializer.errors}", file=sys.stderr)
            sys.stderr.flush()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # El serializer es válido, intentar guardar
        try:
            print(f"💾 Intentando guardar asistencia...", file=sys.stderr)
            sys.stderr.flush()
            asistencia = serializer.save()
            print(f"✅ Asistencia guardada: {asistencia.id}", file=sys.stderr)
            sys.stderr.flush()
            
            return Response(
                AsistenciaClaseSerializer(asistencia).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"💥 ERROR AL GUARDAR: {type(e).__name__}: {str(e)}", file=sys.stderr)
            sys.stderr.flush()
            raise
    
    @action(detail=False, methods=['post'], url_path='registrar-masivo')
    def registrar_masivo(self, request):
        """
        POST /api/asistencias/registrar-masivo/
        
        Registrar múltiples asistencias de una clase
        Body: {
            "clase_id": 1,
            "asistencias": [
                {"inscripcion_id": 1, "estado": "presente"},
                {"inscripcion_id": 2, "estado": "ausente", "observaciones": "..."}
            ]
        }
        """
        serializer = RegistrarAsistenciasMasivasSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            resultado = serializer.save()
            
            return Response({
                'message': f"Se registraron {resultado['creadas']} asistencias",
                'creadas': resultado['creadas'],
                'errores': resultado['errores'],
                'asistencias': AsistenciaClaseListSerializer(
                    resultado['asistencias'], many=True
                ).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='inscritos/(?P<clase_id>[^/.]+)')
    def obtener_inscritos(self, request, clase_id=None):
        """
        GET /api/asistencias/inscritos/{clase_id}/
        
        Obtener lista de inscritos a una clase con su estado de asistencia
        Útil para mostrar lista de asistencia en el frontend
        """
        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response(
                {'error': 'Clase no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener inscripciones confirmadas
        inscripciones = InscripcionClase.objects.filter(
            clase=clase,
            estado='confirmada'
        ).select_related('cliente').prefetch_related(
            Prefetch(
                'asistencias',
                queryset=AsistenciaClase.objects.filter(clase=clase)
            )
        )
        
        data = []
        for inscripcion in inscripciones:
            asistencia = inscripcion.asistencias.first()
            
            data.append({
                'inscripcion_id': inscripcion.id,
                'cliente_id': inscripcion.cliente.id,
                'cliente_nombre': inscripcion.cliente.nombre_completo,
                'cliente_ci': inscripcion.cliente.ci,
                'tiene_asistencia': asistencia is not None,
                'asistencia_id': asistencia.id if asistencia else None,
                'estado': asistencia.estado if asistencia else None,
                'estado_display': asistencia.get_estado_display() if asistencia else None,
                'hora_llegada': asistencia.hora_llegada if asistencia else None,
                'es_tardia': asistencia.es_tardia if asistencia else False,
                'observaciones': asistencia.observaciones if asistencia else None
            })
        
        return Response({
            'clase_id': clase.id,
            'clase_info': {
                'disciplina': clase.disciplina.nombre,
                'fecha': clase.fecha,
                'hora_inicio': clase.hora_inicio,
                'hora_fin': clase.hora_fin,
                'salon': clase.salon.nombre
            },
            'total_inscritos': len(data),
            'con_asistencia': sum(1 for d in data if d['tiene_asistencia']),
            'inscritos': data
        })
    
    @action(detail=False, methods=['get'], url_path='estadisticas/clase/(?P<clase_id>[^/.]+)')
    def estadisticas_clase(self, request, clase_id=None):
        """
        GET /api/asistencias/estadisticas/clase/{clase_id}/
        
        Estadísticas de asistencia para una clase específica
        """
        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response(
                {'error': 'Clase no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        asistencias = AsistenciaClase.objects.filter(clase=clase)
        
        total_inscritos = InscripcionClase.objects.filter(
            clase=clase, estado='confirmada'
        ).count()
        
        stats = asistencias.aggregate(
            total_registros=Count('id'),
            presentes=Count('id', filter=Q(estado=EstadoAsistencia.PRESENTE)),
            ausentes=Count('id', filter=Q(estado=EstadoAsistencia.AUSENTE)),
            justificados=Count('id', filter=Q(estado=EstadoAsistencia.JUSTIFICADO)),
            tardanzas=Count('id', filter=Q(estado=EstadoAsistencia.TARDANZA))
        )
        
        porcentaje_asistencia = (
            (stats['presentes'] + stats['tardanzas']) / total_inscritos * 100
            if total_inscritos > 0 else 0
        )
        
        return Response({
            'clase_id': clase.id,
            'disciplina': clase.disciplina.nombre,
            'fecha': clase.fecha,
            'total_inscritos': total_inscritos,
            'total_registros': stats['total_registros'],
            'presentes': stats['presentes'],
            'ausentes': stats['ausentes'],
            'justificados': stats['justificados'],
            'tardanzas': stats['tardanzas'],
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
            'sin_registrar': total_inscritos - stats['total_registros']
        })
    
    @action(detail=False, methods=['get'], url_path='estadisticas/cliente/(?P<cliente_id>[^/.]+)')
    def estadisticas_cliente(self, request, cliente_id=None):
        """
        GET /api/asistencias/estadisticas/cliente/{cliente_id}/
        
        Estadísticas de asistencia de un cliente específico
        """
        from apps.clients.models import Client
        
        try:
            cliente = Client.objects.get(id=cliente_id)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Rango de fechas (últimos 30 días por defecto)
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if not fecha_desde:
            fecha_desde = (timezone.now().date() - timedelta(days=30))
        if not fecha_hasta:
            fecha_hasta = timezone.now().date()
        
        asistencias = AsistenciaClase.objects.filter(
            cliente=cliente,
            clase__fecha__gte=fecha_desde,
            clase__fecha__lte=fecha_hasta
        )
        
        total_inscripciones = InscripcionClase.objects.filter(
            cliente=cliente,
            clase__fecha__gte=fecha_desde,
            clase__fecha__lte=fecha_hasta,
            estado='confirmada'
        ).count()
        
        stats = asistencias.aggregate(
            total_asistencias=Count('id'),
            presentes=Count('id', filter=Q(estado=EstadoAsistencia.PRESENTE)),
            ausentes=Count('id', filter=Q(estado=EstadoAsistencia.AUSENTE)),
            justificados=Count('id', filter=Q(estado=EstadoAsistencia.JUSTIFICADO)),
            tardanzas=Count('id', filter=Q(estado=EstadoAsistencia.TARDANZA))
        )
        
        porcentaje_asistencia = (
            (stats['presentes'] + stats['tardanzas']) / total_inscripciones * 100
            if total_inscripciones > 0 else 0
        )
        
        return Response({
            'cliente_id': cliente.id,
            'cliente_nombre': cliente.nombre_completo,
            'periodo': {
                'desde': fecha_desde,
                'hasta': fecha_hasta
            },
            'total_inscripciones': total_inscripciones,
            'total_asistencias_registradas': stats['total_asistencias'],
            'presentes': stats['presentes'],
            'ausentes': stats['ausentes'],
            'justificados': stats['justificados'],
            'tardanzas': stats['tardanzas'],
            'porcentaje_asistencia': round(porcentaje_asistencia, 2)
        })
