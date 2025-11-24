"""
CU29 - Registrar Proveedor
Controller/Views con separación de capas y manejo de excepciones
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Proveedor
from .serializers import (
    ProveedorCreateSerializer,
    ProveedorResponseSerializer,
    ProveedorListSerializer,
    ProveedorUpdateSerializer
)
from apps.audit.helpers import registrar_bitacora


class ProveedorPagination(PageNumberPagination):
    """Paginación estándar para proveedores"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    tags=["Proveedores"],
    parameters=[
        OpenApiParameter(
            name='search',
            description='Buscar por razón social, NIT, email o teléfono',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='estado',
            description='Filtrar por estado (A=Activo, I=Inactivo, S=Suspendido)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='page',
            description='Número de página',
            required=False,
            type=int
        ),
        OpenApiParameter(
            name='page_size',
            description='Cantidad de resultados por página',
            required=False,
            type=int
        ),
    ],
    responses={200: ProveedorListSerializer(many=True)}
)
class ProveedorListCreateView(APIView):
    """
    GET: Lista todos los proveedores con paginación y búsqueda
    POST: Crea un nuevo proveedor (CU29)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Listar proveedores con búsqueda, filtros y paginación
        """
        try:
            search = request.query_params.get('search', '').strip()
            estado_filter = request.query_params.get('estado', '').strip().upper()
            
            queryset = Proveedor.objects.all()
            
            # Aplicar filtro por estado
            if estado_filter and estado_filter in ['A', 'I', 'S']:
                queryset = queryset.filter(estado=estado_filter)
            
            # Aplicar búsqueda
            if search:
                queryset = queryset.filter(
                    Q(razon_social__icontains=search) |
                    Q(nit__icontains=search) |
                    Q(email__icontains=search) |
                    Q(telefono__icontains=search) |
                    Q(contacto_nombre__icontains=search)
                )
            
            # Paginación
            paginator = ProveedorPagination()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ProveedorListSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = ProveedorListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Error inesperado
            registrar_bitacora(
                request=request,
                accion="Error al listar proveedores",
                descripcion=f"Error inesperado: {str(e)}",
                modulo="PROVEEDORES",
                tipo_accion="read",
                nivel="error"
            )
            return Response(
                {
                    "error": "Error al obtener la lista de proveedores",
                    "detail": str(e) if request.user.is_staff else "Error interno del servidor"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=ProveedorCreateSerializer,
        responses={
            201: ProveedorResponseSerializer,
            400: OpenApiExample(
                "Error de validación",
                value={
                    "error": "Datos de entrada inválidos",
                    "detail": {"campo": ["mensaje de error"]}
                }
            ),
            403: OpenApiExample(
                "Permiso denegado",
                value={"error": "No tiene permisos para crear proveedores"}
            ),
            409: OpenApiExample(
                "NIT duplicado",
                value={"error": "NIT duplicado", "detail": "Ya existe un proveedor con este NIT"}
            ),
            422: OpenApiExample(
                "Validación de negocio",
                value={"error": "Validación fallida", "detail": "Formato de email inválido"}
            ),
            500: OpenApiExample(
                "Error de servidor",
                value={"error": "Error al guardar proveedor", "detail": "Error de persistencia"}
            )
        },
        examples=[
            OpenApiExample(
                "Crear Proveedor - Ejemplo Completo",
                value={
                    "razon_social": "Distribuidora ABC S.A.",
                    "nit": "1234567890",
                    "telefono": "71234567",
                    "email": "contacto@abc.com",
                    "direccion": "Av. Principal #123, La Paz",
                    "contacto_nombre": "Juan Pérez",
                    "notas": "Proveedor de equipamiento deportivo"
                },
                request_only=True
            ),
            OpenApiExample(
                "Crear Proveedor - Datos Mínimos",
                value={
                    "razon_social": "Proveedor XYZ",
                    "nit": "9876543210"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        CU29: Registrar Proveedor
        
        Crea un nuevo proveedor con validaciones completas:
        - Campos obligatorios: razon_social, nit
        - Validaciones: email (formato), telefono (7-15 dígitos)
        - Unicidad: NIT y razón social
        - Estado inicial: Activo
        - Registra evento en bitácora
        
        Errores:
        - 400: Datos de entrada inválidos
        - 403: Permisos insuficientes
        - 409: NIT o razón social duplicados
        - 422: Validación de formato
        - 500: Error de persistencia
        """
        try:
            # Validar datos de entrada con serializer
            serializer = ProveedorCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                # Error 422: Validación de formato/negocio
                return Response(
                    {
                        "error": "Validación fallida",
                        "detail": serializer.errors
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            
            # Guardar proveedor (estado inicial: Activo por defecto)
            try:
                proveedor = serializer.save()
            except IntegrityError as e:
                # Error 409: NIT o razón social duplicados
                error_msg = str(e).lower()
                if 'nit' in error_msg:
                    detail = "Ya existe un proveedor con este NIT"
                elif 'razon_social' in error_msg:
                    detail = "Ya existe un proveedor con esta razón social"
                else:
                    detail = "Violación de restricción de unicidad"
                
                registrar_bitacora(
                    request=request,
                    accion="Intento de crear proveedor duplicado",
                    descripcion=f"NIT: {request.data.get('nit')} - {detail}",
                    modulo="PROVEEDORES",
                    tipo_accion="create",
                    nivel="warning"
                )
                
                return Response(
                    {
                        "error": "Proveedor duplicado",
                        "detail": detail
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Registrar en bitácora
            registrar_bitacora(
                request=request,
                usuario=request.user,
                accion="Proveedor creado",
                descripcion=f"Proveedor '{proveedor.razon_social}' (NIT: {proveedor.nit}) creado exitosamente",
                modulo="PROVEEDORES",
                tipo_accion="create",
                nivel="info",
                datos_adicionales={
                    'proveedor_id': proveedor.id,
                    'nit': proveedor.nit,
                    'razon_social': proveedor.razon_social,
                    'estado': proveedor.estado
                }
            )
            
            # Respuesta exitosa con DTO de salida
            response_serializer = ProveedorResponseSerializer(proveedor)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            # Error 500: Error inesperado de persistencia o servidor
            registrar_bitacora(
                request=request,
                accion="Error al crear proveedor",
                descripcion=f"Error inesperado: {str(e)}",
                modulo="PROVEEDORES",
                tipo_accion="create",
                nivel="error",
                datos_adicionales={
                    'data': request.data
                }
            )
            
            return Response(
                {
                    "error": "Error al guardar proveedor",
                    "detail": str(e) if request.user.is_staff else "Error interno del servidor"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=["Proveedores"])
class ProveedorDetailView(APIView):
    """
    GET: Obtiene detalle de un proveedor
    PUT/PATCH: Actualiza un proveedor
    DELETE: Elimina (desactiva) un proveedor
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Helper para obtener proveedor por ID"""
        try:
            return Proveedor.objects.get(pk=pk)
        except Proveedor.DoesNotExist:
            return None
    
    @extend_schema(responses={200: ProveedorResponseSerializer})
    def get(self, request, pk):
        """Obtener detalle de un proveedor"""
        proveedor = self.get_object(pk)
        
        if not proveedor:
            return Response(
                {"error": "Proveedor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProveedorResponseSerializer(proveedor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=ProveedorUpdateSerializer,
        responses={200: ProveedorResponseSerializer}
    )
    def put(self, request, pk):
        """Actualizar proveedor (actualización completa)"""
        proveedor = self.get_object(pk)
        
        if not proveedor:
            return Response(
                {"error": "Proveedor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProveedorUpdateSerializer(proveedor, data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validación fallida",
                    "detail": serializer.errors
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        try:
            updated_proveedor = serializer.save()
            
            # Registrar en bitácora
            registrar_bitacora(
                request=request,
                usuario=request.user,
                accion="Proveedor actualizado",
                descripcion=f"Proveedor '{updated_proveedor.razon_social}' (ID: {updated_proveedor.id}) actualizado",
                modulo="PROVEEDORES",
                tipo_accion="update",
                nivel="info",
                datos_adicionales={
                    'proveedor_id': updated_proveedor.id,
                    'cambios': request.data
                }
            )
            
            response_serializer = ProveedorResponseSerializer(updated_proveedor)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            registrar_bitacora(
                request=request,
                accion="Error al actualizar proveedor",
                descripcion=f"Error: {str(e)}",
                modulo="PROVEEDORES",
                tipo_accion="update",
                nivel="error"
            )
            
            return Response(
                {
                    "error": "Error al actualizar proveedor",
                    "detail": str(e) if request.user.is_staff else "Error interno del servidor"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=ProveedorUpdateSerializer,
        responses={200: ProveedorResponseSerializer}
    )
    def patch(self, request, pk):
        """Actualizar proveedor (actualización parcial)"""
        proveedor = self.get_object(pk)
        
        if not proveedor:
            return Response(
                {"error": "Proveedor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProveedorUpdateSerializer(proveedor, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validación fallida",
                    "detail": serializer.errors
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        try:
            updated_proveedor = serializer.save()
            
            # Registrar en bitácora
            registrar_bitacora(
                request=request,
                usuario=request.user,
                accion="Proveedor actualizado (parcial)",
                descripcion=f"Proveedor '{updated_proveedor.razon_social}' (ID: {updated_proveedor.id}) actualizado parcialmente",
                modulo="PROVEEDORES",
                tipo_accion="update",
                nivel="info",
                datos_adicionales={
                    'proveedor_id': updated_proveedor.id,
                    'cambios': request.data
                }
            )
            
            response_serializer = ProveedorResponseSerializer(updated_proveedor)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            registrar_bitacora(
                request=request,
                accion="Error al actualizar proveedor",
                descripcion=f"Error: {str(e)}",
                modulo="PROVEEDORES",
                tipo_accion="update",
                nivel="error"
            )
            
            return Response(
                {
                    "error": "Error al actualizar proveedor",
                    "detail": str(e) if request.user.is_staff else "Error interno del servidor"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """
        Eliminar (desactivar) proveedor
        Soft delete: cambia estado a Inactivo
        """
        proveedor = self.get_object(pk)
        
        if not proveedor:
            return Response(
                {"error": "Proveedor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Soft delete: desactivar en lugar de eliminar
            proveedor.desactivar()
            
            # Registrar en bitácora
            registrar_bitacora(
                request=request,
                usuario=request.user,
                accion="Proveedor desactivado",
                descripcion=f"Proveedor '{proveedor.razon_social}' (ID: {proveedor.id}) desactivado",
                modulo="PROVEEDORES",
                tipo_accion="delete",
                nivel="info",
                datos_adicionales={
                    'proveedor_id': proveedor.id,
                    'nit': proveedor.nit
                }
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            registrar_bitacora(
                request=request,
                accion="Error al desactivar proveedor",
                descripcion=f"Error: {str(e)}",
                modulo="PROVEEDORES",
                tipo_accion="delete",
                nivel="error"
            )
            
            return Response(
                {
                    "error": "Error al desactivar proveedor",
                    "detail": str(e) if request.user.is_staff else "Error interno del servidor"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
