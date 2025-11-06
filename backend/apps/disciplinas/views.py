from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Disciplina
from .serializers import DisciplinaSerializer, DisciplinaListSerializer
from apps.audit.helpers import registrar_bitacora


class DisciplinaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    tags=["Disciplinas"],
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nombre', required=False, type=str),
        OpenApiParameter(name='activa', description='Filtrar por estado activo', required=False, type=bool),
        OpenApiParameter(name='page', description='Número de página', required=False, type=int),
    ],
    responses={200: DisciplinaListSerializer(many=True)}
)
class DisciplinaListCreateView(APIView):
    """
    CU19: Gestionar Disciplinas - Listar y Crear
    
    GET: Lista todas las disciplinas con paginación y búsqueda
    POST: Crea una nueva disciplina
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Listar disciplinas con búsqueda y filtros"""
        search = request.query_params.get('search', '').strip()
        activa_filter = request.query_params.get('activa', '').strip()
        
        queryset = Disciplina.objects.all()
        
        # Aplicar búsqueda por nombre
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Filtrar por estado activo
        if activa_filter:
            is_active = activa_filter.lower() == 'true'
            queryset = queryset.filter(activa=is_active)
        
        # Paginación
        paginator = DisciplinaPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = DisciplinaListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = DisciplinaListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=DisciplinaSerializer,
        responses={201: DisciplinaSerializer}
    )
    def post(self, request):
        """Crear una nueva disciplina"""
        serializer = DisciplinaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        disciplina = serializer.save()
        
        # Registrar en auditoría
        try:
            registrar_bitacora(
                request=request,
                accion="Crear Disciplina",
                descripcion=f"Disciplina '{disciplina.nombre}' creada exitosamente",
                modulo="DISCIPLINAS",
                tipo_accion="create",
                nivel="info",
                datos_adicionales={
                    'disciplina_id': disciplina.id,
                    'nombre': disciplina.nombre
                }
            )
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")
        
        return Response(
            DisciplinaSerializer(disciplina).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Disciplinas"],
    responses={200: DisciplinaSerializer}
)
class DisciplinaDetailView(APIView):
    """
    CU19: Gestionar Disciplinas - Detalle, Actualizar y Eliminar
    
    GET: Obtiene los detalles de una disciplina
    PUT/PATCH: Actualiza una disciplina
    DELETE: Elimina una disciplina
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Helper para obtener la disciplina"""
        try:
            return Disciplina.objects.get(pk=pk)
        except Disciplina.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtener detalle de una disciplina"""
        disciplina = self.get_object(pk)
        
        if not disciplina:
            return Response(
                {"detail": "Disciplina no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DisciplinaSerializer(disciplina)
        return Response(serializer.data)
    
    @extend_schema(request=DisciplinaSerializer, responses={200: DisciplinaSerializer})
    def put(self, request, pk):
        """Actualizar completamente una disciplina"""
        disciplina = self.get_object(pk)
        
        if not disciplina:
            return Response(
                {"detail": "Disciplina no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardar datos anteriores para auditoría
        datos_anteriores = {
            'nombre': disciplina.nombre,
            'descripcion': disciplina.descripcion,
            'activa': disciplina.activa
        }
        
        serializer = DisciplinaSerializer(disciplina, data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_disciplina = serializer.save()
        
        # Registrar en auditoría
        try:
            registrar_bitacora(
                request=request,
                accion="Actualizar Disciplina",
                descripcion=f"Disciplina '{updated_disciplina.nombre}' actualizada",
                modulo="DISCIPLINAS",
                tipo_accion="update",
                nivel="info",
                datos_adicionales={
                    'disciplina_id': updated_disciplina.id,
                    'datos_anteriores': datos_anteriores,
                    'datos_nuevos': {
                        'nombre': updated_disciplina.nombre,
                        'descripcion': updated_disciplina.descripcion,
                        'activa': updated_disciplina.activa
                    }
                }
            )
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")
        
        return Response(DisciplinaSerializer(updated_disciplina).data)
    
    @extend_schema(request=DisciplinaSerializer, responses={200: DisciplinaSerializer})
    def patch(self, request, pk):
        """Actualizar parcialmente una disciplina"""
        disciplina = self.get_object(pk)
        
        if not disciplina:
            return Response(
                {"detail": "Disciplina no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DisciplinaSerializer(disciplina, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_disciplina = serializer.save()
        
        # Registrar en auditoría
        try:
            registrar_bitacora(
                request=request,
                accion="Actualizar Disciplina (Parcial)",
                descripcion=f"Disciplina '{updated_disciplina.nombre}' actualizada parcialmente",
                modulo="DISCIPLINAS",
                tipo_accion="update",
                nivel="info",
                datos_adicionales={
                    'disciplina_id': updated_disciplina.id,
                    'campos_actualizados': list(request.data.keys())
                }
            )
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")
        
        return Response(DisciplinaSerializer(updated_disciplina).data)
    
    def delete(self, request, pk):
        """Eliminar una disciplina"""
        disciplina = self.get_object(pk)
        
        if not disciplina:
            return Response(
                {"detail": "Disciplina no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardar datos antes de eliminar
        disciplina_data = {
            "id": disciplina.id,
            "nombre": disciplina.nombre,
            "descripcion": disciplina.descripcion,
            "activa": disciplina.activa
        }
        
        disciplina.delete()
        
        # Registrar en auditoría
        try:
            registrar_bitacora(
                request=request,
                accion="Eliminar Disciplina",
                descripcion=f"Disciplina '{disciplina_data['nombre']}' eliminada",
                modulo="DISCIPLINAS",
                tipo_accion="delete",
                nivel="warning",
                datos_adicionales=disciplina_data
            )
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")
        
        return Response(
            {"detail": "Disciplina eliminada correctamente.", "data": disciplina_data},
            status=status.HTTP_200_OK
        )
