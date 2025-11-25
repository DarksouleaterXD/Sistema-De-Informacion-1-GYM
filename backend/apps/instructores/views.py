"""
Views para el módulo de Instructores
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Instructor
from .serializers import (
    InstructorListSerializer,
    InstructorDetailSerializer,
    InstructorCreateSerializer,
    InstructorUpdateSerializer
)
from apps.core.permissions import PermissionCodes, user_has_permission


class InstructorPermission(permissions.BasePermission):
    """
    Permiso personalizado para el ViewSet de Instructores.
    Verifica permisos específicos según la acción.
    """
    
    # Mapeo de acciones a permisos requeridos
    action_permissions = {
        'list': PermissionCodes.INSTRUCTOR_VIEW,
        'retrieve': PermissionCodes.INSTRUCTOR_VIEW,
        'create': PermissionCodes.INSTRUCTOR_CREATE,
        'update': PermissionCodes.INSTRUCTOR_EDIT,
        'partial_update': PermissionCodes.INSTRUCTOR_EDIT,
        'destroy': PermissionCodes.INSTRUCTOR_DELETE,
        'activar': PermissionCodes.INSTRUCTOR_EDIT,
        'clases': PermissionCodes.INSTRUCTOR_VIEW,
    }
    
    def has_permission(self, request, view):
        # Superusuario siempre tiene permiso
        if request.user and request.user.is_superuser:
            return True
        
        # Obtener la acción actual
        action = view.action
        
        # Obtener el permiso requerido para esta acción
        required_permission = self.action_permissions.get(action)
        
        if not required_permission:
            # Si no hay mapeo definido, denegar por defecto
            return False
        
        # Verificar si el usuario tiene el permiso
        return user_has_permission(request.user, required_permission)


@extend_schema(tags=['Instructores'])
class InstructorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar instructores
    
    Permisos requeridos:
    - list: instructor.view
    - retrieve: instructor.view
    - create: instructor.create
    - update/partial_update: instructor.edit
    - destroy: instructor.delete
    """
    queryset = Instructor.objects.select_related('usuario').all()
    permission_classes = [permissions.IsAuthenticated, InstructorPermission]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        'usuario__first_name', 
        'usuario__last_name', 
        'usuario__email',
        'especialidades'
    ]
    filterset_fields = ['activo', 'experiencia_anos']
    ordering_fields = ['created_at', 'experiencia_anos', 'fecha_ingreso']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return InstructorListSerializer
        elif self.action == 'retrieve':
            return InstructorDetailSerializer
        elif self.action == 'create':
            return InstructorCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InstructorUpdateSerializer
        return InstructorListSerializer
    
    @extend_schema(
        summary="Listar instructores",
        description="Obtiene la lista de instructores con filtros y búsqueda",
        parameters=[
            OpenApiParameter(
                name='activo',
                type=bool,
                description='Filtrar por instructores activos/inactivos'
            ),
            OpenApiParameter(
                name='search',
                type=str,
                description='Buscar por nombre, email o especialidades'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Listar instructores"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Obtener instructor",
        description="Obtiene los detalles de un instructor específico"
    )
    def retrieve(self, request, *args, **kwargs):
        """Obtener detalles de un instructor"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Crear instructor",
        description="Crea un nuevo perfil de instructor para un usuario"
    )
    def create(self, request, *args, **kwargs):
        """Crear un nuevo instructor"""
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar instructor",
        description="Actualiza la información de un instructor"
    )
    def update(self, request, *args, **kwargs):
        """Actualizar un instructor"""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar parcialmente instructor",
        description="Actualiza parcialmente la información de un instructor"
    )
    def partial_update(self, request, *args, **kwargs):
        """Actualización parcial de un instructor"""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Eliminar instructor",
        description="Elimina el perfil de un instructor (soft delete)"
    )
    def destroy(self, request, *args, **kwargs):
        """Eliminar un instructor"""
        instructor = self.get_object()
        instructor.activo = False
        instructor.save()
        return Response(
            {"detail": "Instructor desactivado exitosamente"},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Activar instructor",
        description="Reactiva un instructor desactivado"
    )
    @action(detail=True, methods=['post'], url_path='activar')
    def activar(self, request, pk=None):
        """Activar un instructor desactivado"""
        instructor = self.get_object()
        instructor.activo = True
        instructor.save()
        serializer = self.get_serializer(instructor)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Clases del instructor",
        description="Obtiene las clases asignadas a un instructor"
    )
    @action(detail=True, methods=['get'], url_path='clases')
    def clases(self, request, pk=None):
        """Obtener las clases de un instructor"""
        instructor = self.get_object()
        from apps.clases.serializers import ClaseListSerializer
        clases = instructor.usuario.clases_instructor.all()
        serializer = ClaseListSerializer(clases, many=True)
        return Response(serializer.data)
