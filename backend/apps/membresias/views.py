from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Sum
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from datetime import date

from apps.core.constants import (
    METODO_EFECTIVO, 
    METODOS_PAGO, 
    ESTADOS_MEMBRESIA,
    ESTADO_ACTIVO,
    ESTADO_VENCIDO
)
from .models import Membresia, InscripcionMembresia, PlanMembresia
from .serializers import (
    MembresiaSerializer,
    MembresiaListSerializer,
    MembresiaCreateSerializer,
    InscripcionMembresiaSerializer,
    PlanMembresiaSerializer,
    MembresiaEstadoVigenciaSerializer
)
from apps.audit.helpers import registrar_bitacora


class MembresiaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    tags=["Membresías"],
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nombre o CI del cliente', required=False, type=str),
        OpenApiParameter(name='estado', description='Filtrar por estado', required=False, type=str),
        OpenApiParameter(name='page', description='Número de página', required=False, type=int),
    ],
    responses={200: MembresiaListSerializer(many=True)}
)
class MembresiaListCreateView(APIView):
    """
    GET: Lista todas las membresías con paginación y búsqueda
    POST: Crea una nueva membresía con su inscripción
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Listar membresías con búsqueda y filtros"""
        search = request.query_params.get('search', '').strip()
        estado_filter = request.query_params.get('estado', '').strip()
        
        queryset = Membresia.objects.select_related(
            'inscripcion__cliente',
            'usuario_registro'
        ).all()
        
        # Aplicar búsqueda por nombre o CI del cliente
        if search:
            queryset = queryset.filter(
                Q(inscripcion__cliente__nombre__icontains=search) |
                Q(inscripcion__cliente__apellido__icontains=search) |
                Q(inscripcion__cliente__ci__icontains=search)
            )
        
        # Filtrar por estado
        if estado_filter:
            queryset = queryset.filter(estado=estado_filter)
        
        # Paginación
        paginator = MembresiaPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = MembresiaListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = MembresiaListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=MembresiaCreateSerializer,
        responses={201: MembresiaSerializer},
        examples=[
            OpenApiExample(
                "Crear Membresía",
                value={
                    "cliente": 1,
                    "monto": 150.00,
                    "metodo_de_pago": METODO_EFECTIVO,
                    "estado": ESTADO_ACTIVO,
                    "fecha_inicio": "2025-10-23",
                    "fecha_fin": "2025-11-23"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """Crear una nueva membresía con inscripción"""
        serializer = MembresiaCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membresia = serializer.save()
        
        # Retornar con el serializer completo
        response_serializer = MembresiaSerializer(membresia)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Membresías"],
    responses={200: MembresiaSerializer}
)
class MembresiaDetailView(APIView):
    """
    GET: Obtiene los detalles de una membresía
    PUT: Actualiza una membresía
    PATCH: Actualiza parcialmente una membresía
    DELETE: Elimina una membresía
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Helper para obtener la membresía"""
        try:
            return Membresia.objects.select_related(
                'inscripcion__cliente',
                'usuario_registro'
            ).get(pk=pk)
        except Membresia.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtener detalle de una membresía"""
        membresia = self.get_object(pk)
        
        if not membresia:
            return Response(
                {"detail": "Membresía no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MembresiaSerializer(membresia)
        return Response(serializer.data)
    
    @extend_schema(request=MembresiaSerializer, responses={200: MembresiaSerializer})
    def put(self, request, pk):
        """Actualizar completamente una membresía"""
        membresia = self.get_object(pk)
        
        if not membresia:
            return Response(
                {"detail": "Membresía no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MembresiaSerializer(membresia, data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_membresia = serializer.save()
        
        return Response(MembresiaSerializer(updated_membresia).data)
    
    @extend_schema(request=MembresiaSerializer, responses={200: MembresiaSerializer})
    def patch(self, request, pk):
        """Actualizar parcialmente una membresía"""
        membresia = self.get_object(pk)
        
        if not membresia:
            return Response(
                {"detail": "Membresía no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MembresiaSerializer(membresia, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_membresia = serializer.save()
        
        return Response(MembresiaSerializer(updated_membresia).data)
    
    def delete(self, request, pk):
        """Eliminar una membresía"""
        membresia = self.get_object(pk)
        
        if not membresia:
            return Response(
                {"detail": "Membresía no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardar datos antes de eliminar
        membresia_data = {
            "id": membresia.id,
            "cliente": membresia.inscripcion.cliente.nombre_completo,
            "estado": membresia.estado,
            "fecha_inicio": str(membresia.fecha_inicio),
            "fecha_fin": str(membresia.fecha_fin)
        }
        
        membresia.delete()
        
        return Response(
            {"detail": "Membresía eliminada correctamente.", "data": membresia_data},
            status=status.HTTP_204_NO_CONTENT
        )


@extend_schema(
    tags=["Membresías"],
    responses={200: dict}
)
class MembresiaStatsView(APIView):
    """
    GET: Obtiene estadísticas de membresías
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener estadísticas de membresías"""
        # Total de membresías
        total = Membresia.objects.count()
        
        # Membresías activas
        activas = Membresia.objects.filter(
            estado=ESTADO_ACTIVO,
            fecha_fin__gte=date.today()
        ).count()
        
        # Membresías vencidas
        vencidas = Membresia.objects.filter(
            Q(estado=ESTADO_VENCIDO) | Q(fecha_fin__lt=date.today())
        ).count()
        
        # Ingresos totales
        ingresos = InscripcionMembresia.objects.aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        # Ingresos del mes actual
        from datetime import datetime
        mes_actual = datetime.now().month
        año_actual = datetime.now().year
        
        ingresos_mes = InscripcionMembresia.objects.filter(
            created_at__month=mes_actual,
            created_at__year=año_actual
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        return Response({
            "total_membresias": total,
            "activas": activas,
            "vencidas": vencidas,
            "ingresos_totales": float(ingresos),
            "ingresos_mes_actual": float(ingresos_mes)
        })


@extend_schema(
    tags=["Planes de Membresía"],
    responses={200: PlanMembresiaSerializer(many=True)}
)
class PlanMembresiaListView(APIView):
    """
    GET: Lista todos los planes de membresía disponibles
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Listar todos los planes de membresía"""
        planes = PlanMembresia.objects.all().order_by('duracion')
        serializer = PlanMembresiaSerializer(planes, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Membresías"],
    parameters=[
        OpenApiParameter(
            name='membresia_id',
            description='ID de la membresía a consultar',
            required=False,
            type=int,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='cliente_id',
            description='ID del cliente para obtener su membresía activa',
            required=False,
            type=int,
            location=OpenApiParameter.QUERY
        ),
    ],
    responses={
        200: MembresiaEstadoVigenciaSerializer,
        404: {"description": "Membresía no encontrada"}
    }
)
class ConsultarEstadoVigenciaView(APIView):
    """
    CU17: Consultar Estado/Vigencia de Membresía
    
    GET: Consulta el estado y vigencia de una membresía específica o de un cliente
    
    Permite a los actores (Superusuario, Administrador, Instructor) consultar
    el estado y vigencia de una membresía en el sistema.
    
    Query Params:
    - membresia_id: ID de la membresía específica
    - cliente_id: ID del cliente (retorna su membresía más reciente)
    
    Retorna:
    - Estado actual (activo, suspendido, cancelado, vencido)
    - Vigencia (fechas de inicio y fin)
    - Días restantes y días transcurridos
    - Porcentaje de uso
    - Promociones aplicadas
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Consultar estado y vigencia de membresía"""
        membresia_id = request.query_params.get('membresia_id')
        cliente_id = request.query_params.get('cliente_id')
        
        # Validar que se proporcione al menos un parámetro
        if not membresia_id and not cliente_id:
            return Response(
                {
                    "error": "Debe proporcionar 'membresia_id' o 'cliente_id'",
                    "detail": "Especifique una membresía específica o un cliente"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Buscar por ID de membresía específica
            if membresia_id:
                membresia = Membresia.objects.select_related(
                    'inscripcion__cliente',
                    'plan'
                ).prefetch_related('promociones').get(id=membresia_id)
            
            # Buscar por cliente (última membresía)
            elif cliente_id:
                membresia = Membresia.objects.select_related(
                    'inscripcion__cliente',
                    'plan'
                ).prefetch_related('promociones').filter(
                    inscripcion__cliente_id=cliente_id
                ).order_by('-fecha_inicio').first()
                
                if not membresia:
                    return Response(
                        {
                            "error": "Cliente sin membresías",
                            "detail": f"El cliente con ID {cliente_id} no tiene membresías registradas"
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        except Membresia.DoesNotExist:
            return Response(
                {
                    "error": "Membresía no encontrada",
                    "detail": f"No existe una membresía con ID {membresia_id}"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "error": "Error en la carga de datos",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Serializar la información
        serializer = MembresiaEstadoVigenciaSerializer(membresia)
        
        # Registrar la consulta en auditoría (Post-Condición del CU17)
        try:
            registrar_bitacora(
                request=request,
                usuario=request.user,
                accion="Consultar Estado/Vigencia",
                descripcion=f"Consultó estado/vigencia de membresía #{membresia.id} del cliente {membresia.inscripcion.cliente.nombre_completo}",
                modulo="MEMBRESÍAS",
                tipo_accion="view",
                nivel="info",
                datos_adicionales={
                    'membresia_id': membresia.id,
                    'cliente_id': membresia.inscripcion.cliente.id,
                    'estado': membresia.estado,
                    'dias_restantes': membresia.dias_restantes
                }
            )
        except Exception as audit_error:
            # No fallar la consulta si falla el registro de auditoría
            print(f"Error al registrar auditoría: {audit_error}")
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# =============================================================================
# VIEWS PARA PLANES DE MEMBRESÍA (CRUD independiente)
# =============================================================================

@extend_schema(
    tags=["Planes de Membresía"],
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nombre', required=False, type=str),
        OpenApiParameter(name='page', description='Número de página', required=False, type=int),
    ],
    responses={200: PlanMembresiaSerializer(many=True)}
)
class PlanMembresiaListCreateView(APIView):
    """
    GET: Lista todos los planes de membresía con paginación y búsqueda
    POST: Crea un nuevo plan de membresía
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Listar todos los planes de membresía"""
        try:
            # Obtener parámetros de búsqueda
            search = request.query_params.get('search', '')
            
            # Filtros
            planes = PlanMembresia.objects.all()
            
            if search:
                planes = planes.filter(
                    Q(nombre__icontains=search) |
                    Q(descripcion__icontains=search)
                )
            
            # Ordenar por duración
            planes = planes.order_by('duracion')
            
            # Paginación
            paginator = MembresiaPagination()
            paginated_planes = paginator.paginate_queryset(planes, request)
            
            serializer = PlanMembresiaSerializer(paginated_planes, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Error al obtener planes: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Crear un nuevo plan de membresía"""
        try:
            serializer = PlanMembresiaSerializer(data=request.data)
            
            if serializer.is_valid():
                plan = serializer.save()
                
                # Registrar en auditoría
                try:
                    registrar_bitacora(
                        request=request,
                        usuario=request.user,
                        accion="Crear Plan de Membresía",
                        descripcion=f"Creó plan '{plan.nombre}' - {plan.duracion} días - Bs. {plan.precio_base}",
                        modulo="PLANES DE MEMBRESÍA",
                        tipo_accion="create",
                        nivel="info",
                        datos_adicionales={
                            'plan_id': plan.id,
                            'nombre': plan.nombre,
                            'duracion': plan.duracion,
                            'precio_base': float(plan.precio_base)
                        }
                    )
                except Exception as audit_error:
                    print(f"Error al registrar auditoría: {audit_error}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {"error": f"Error al crear plan: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["Planes de Membresía"],
    responses={200: PlanMembresiaSerializer}
)
class PlanMembresiaDetailView(APIView):
    """
    GET: Obtiene detalle de un plan
    PUT: Actualiza un plan completo
    PATCH: Actualiza un plan parcialmente
    DELETE: Elimina un plan
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Obtener plan por ID"""
        try:
            return PlanMembresia.objects.get(pk=pk)
        except PlanMembresia.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtener detalle de un plan"""
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Plan no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PlanMembresiaSerializer(plan)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Actualizar plan completo"""
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Plan no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            serializer = PlanMembresiaSerializer(plan, data=request.data)
            
            if serializer.is_valid():
                plan_actualizado = serializer.save()
                
                # Registrar en auditoría
                try:
                    registrar_bitacora(
                        request=request,
                        usuario=request.user,
                        accion="Actualizar Plan de Membresía",
                        descripcion=f"Actualizó plan '{plan_actualizado.nombre}'",
                        modulo="PLANES DE MEMBRESÍA",
                        tipo_accion="update",
                        nivel="info",
                        datos_adicionales={
                            'plan_id': plan_actualizado.id,
                            'nombre': plan_actualizado.nombre,
                            'duracion': plan_actualizado.duracion,
                            'precio_base': float(plan_actualizado.precio_base)
                        }
                    )
                except Exception as audit_error:
                    print(f"Error al registrar auditoría: {audit_error}")
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {"error": f"Error al actualizar plan: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, pk):
        """Actualizar plan parcialmente"""
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Plan no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            serializer = PlanMembresiaSerializer(plan, data=request.data, partial=True)
            
            if serializer.is_valid():
                plan_actualizado = serializer.save()
                
                # Registrar en auditoría
                try:
                    registrar_bitacora(
                        request=request,
                        usuario=request.user,
                        accion="Actualizar Plan de Membresía (Parcial)",
                        descripcion=f"Actualizó parcialmente plan '{plan_actualizado.nombre}'",
                        modulo="PLANES DE MEMBRESÍA",
                        tipo_accion="update",
                        nivel="info",
                        datos_adicionales={
                            'plan_id': plan_actualizado.id,
                            'campos_actualizados': list(request.data.keys())
                        }
                    )
                except Exception as audit_error:
                    print(f"Error al registrar auditoría: {audit_error}")
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {"error": f"Error al actualizar plan: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Eliminar un plan"""
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Plan no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Verificar si hay membresías usando este plan
            membresias_count = Membresia.objects.filter(plan=plan).count()
            
            if membresias_count > 0:
                return Response(
                    {
                        "error": f"No se puede eliminar el plan porque tiene {membresias_count} membresía(s) asociada(s)",
                        "membresias_count": membresias_count
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Guardar info antes de eliminar
            plan_info = {
                'id': plan.id,
                'nombre': plan.nombre,
                'duracion': plan.duracion,
                'precio_base': float(plan.precio_base)
            }
            
            plan.delete()
            
            # Registrar en auditoría
            try:
                registrar_bitacora(
                    request=request,
                    usuario=request.user,
                    accion="Eliminar Plan de Membresía",
                    descripcion=f"Eliminó plan '{plan_info['nombre']}'",
                    modulo="PLANES DE MEMBRESÍA",
                    tipo_accion="delete",
                    nivel="warning",
                    datos_adicionales=plan_info
                )
            except Exception as audit_error:
                print(f"Error al registrar auditoría: {audit_error}")
            
            return Response(
                {"message": "Plan eliminado exitosamente"},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response(
                {"error": f"Error al eliminar plan: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )