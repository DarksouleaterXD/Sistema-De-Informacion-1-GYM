from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Client
from .serializers import ClientSerializer, ClientListSerializer
from apps.audit.models import HistorialActividad as Bitacora


class ClientPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    tags=["Clientes"],
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nombre, apellido, CI o email', required=False, type=str),
        OpenApiParameter(name='page', description='Número de página', required=False, type=int),
        OpenApiParameter(name='page_size', description='Cantidad de resultados por página', required=False, type=int),
    ],
    responses={200: ClientListSerializer(many=True)}
)
class ClientListCreateView(APIView):
    """
    GET: Lista todos los clientes con paginación y búsqueda
    POST: Crea un nuevo cliente
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Listar clientes con búsqueda y paginación"""
        search = request.query_params.get('search', '').strip()
        
        queryset = Client.objects.all()
        
        # Aplicar búsqueda
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(ci__icontains=search) |
                Q(email__icontains=search) |
                Q(telefono__icontains=search)
            )
        
        # Paginación
        paginator = ClientPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ClientListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ClientListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=ClientSerializer,
        responses={201: ClientSerializer},
        examples=[
            OpenApiExample(
                "Crear Cliente",
                value={
                    "nombre": "Juan Carlos",
                    "apellido": "Pérez López",
                    "ci": "12345678",
                    "telefono": "71234567",
                    "email": "juan.perez@email.com"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """Crear un nuevo cliente"""
        serializer = ClientSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = serializer.save()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            usuario=request.user,
            tipo_accion="create",
            accion="Crear Cliente",
            descripcion=f"Cliente creado: {client.nombre_completo} (CI: {client.ci})",
            nivel="info",
            datos_adicionales={
                "cliente_id": client.id,
                "ci": client.ci
            }
        )
        
        return Response(
            ClientSerializer(client).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Clientes"],
    responses={200: ClientSerializer}
)
class ClientDetailView(APIView):
    """
    GET: Obtiene los detalles de un cliente
    PUT: Actualiza un cliente
    PATCH: Actualiza parcialmente un cliente
    DELETE: Elimina un cliente
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Helper para obtener el cliente"""
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtener detalle de un cliente"""
        client = self.get_object(pk)
        
        if not client:
            return Response(
                {"detail": "Cliente no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ClientSerializer(client)
        return Response(serializer.data)
    
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer})
    def put(self, request, pk):
        """Actualizar completamente un cliente"""
        client = self.get_object(pk)
        
        if not client:
            return Response(
                {"detail": "Cliente no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ClientSerializer(client, data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar datos anteriores para la bitácora
        datos_anteriores = {
            "nombre": client.nombre,
            "apellido": client.apellido,
            "ci": client.ci,
            "telefono": client.telefono,
            "email": client.email
        }
        
        updated_client = serializer.save()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            usuario=request.user,
            tipo_accion="update",
            accion="Actualizar Cliente",
            descripcion=f"Cliente actualizado: {updated_client.nombre_completo} (CI: {updated_client.ci})",
            nivel="info",
            datos_adicionales={
                "cliente_id": updated_client.id,
                "datos_anteriores": datos_anteriores
            }
        )
        
        return Response(ClientSerializer(updated_client).data)
    
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer})
    def patch(self, request, pk):
        """Actualizar parcialmente un cliente"""
        client = self.get_object(pk)
        
        if not client:
            return Response(
                {"detail": "Cliente no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ClientSerializer(client, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_client = serializer.save()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            usuario=request.user,
            tipo_accion="update",
            accion="Actualizar Cliente (Parcial)",
            descripcion=f"Cliente actualizado parcialmente: {updated_client.nombre_completo}",
            nivel="info",
            datos_adicionales={
                "cliente_id": updated_client.id,
                "campos_actualizados": list(request.data.keys())
            }
        )
        
        return Response(ClientSerializer(updated_client).data)
    
    def delete(self, request, pk):
        """Eliminar un cliente"""
        client = self.get_object(pk)
        
        if not client:
            return Response(
                {"detail": "Cliente no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardar datos para la bitácora
        client_data = {
            "id": client.id,
            "nombre_completo": client.nombre_completo,
            "ci": client.ci
        }
        
        client.delete()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            usuario=request.user,
            tipo_accion="delete",
            accion="Eliminar Cliente",
            descripcion=f"Cliente eliminado: {client_data['nombre_completo']} (CI: {client_data['ci']})",
            nivel="warning",
            datos_adicionales=client_data
        )
        
        return Response(
            {"detail": "Cliente eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
