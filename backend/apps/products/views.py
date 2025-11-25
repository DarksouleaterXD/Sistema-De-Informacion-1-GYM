from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Category
from .serializers import CategorySerializer
from apps.audit.helpers import registrar_bitacora

class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema(
    tags=["Productos - Categorías"],
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nombre o descripción', required=False, type=str),
        OpenApiParameter(name='activo', description='Filtrar por estado activo', required=False, type=bool),
        OpenApiParameter(name='page', description='Número de página', required=False, type=int),
    ],
    responses={200: CategorySerializer(many=True)}
)
class CategoryListCreateView(APIView):
    """
    GET: Lista todas las categorías con paginación y búsqueda
    POST: Crea una nueva categoría
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Listar categorías con búsqueda y filtros"""
        search = request.query_params.get('search', '').strip()
        activo_param = request.query_params.get('activo')

        queryset = Category.objects.all()

        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        if activo_param is not None:
            es_activo = activo_param.lower() == 'true'
            queryset = queryset.filter(activo=es_activo)

        paginator = CategoryPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = CategorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={201: CategorySerializer},
        examples=[
            OpenApiExample(
                "Crear Categoría",
                value={
                    "nombre": "Suplementos",
                    "descripcion": "Proteínas, vitaminas y otros suplementos",
                    "activo": True
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """Crear una nueva categoría"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()

            # Registrar en auditoría
            try:
                registrar_bitacora(
                    request=request,
                    usuario=request.user,
                    accion="Crear Categoría",
                    descripcion=f"Creó categoría '{category.nombre}'",
                    modulo="PRODUCTOS",
                    tipo_accion="create",
                    nivel="info",
                    datos_adicionales={
                        'categoria_id': category.id,
                        'nombre': category.nombre
                    }
                )
            except Exception as e:
                print(f"Error auditoría: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Productos - Categorías"],
    responses={200: CategorySerializer}
)
class CategoryDetailView(APIView):
    """
    GET: Obtiene detalle de una categoría
    PUT: Actualiza una categoría completa
    PATCH: Actualiza una categoría parcialmente
    DELETE: Elimina una categoría (soft delete preferiblemente, pero aquí haremos delete físico por simplicidad inicial, o lógico si se requiere)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"error": "Categoría no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"error": "Categoría no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            updated_category = serializer.save()
            
            # Auditoría
            try:
                registrar_bitacora(
                    request=request,
                    usuario=request.user,
                    accion="Actualizar Categoría",
                    descripcion=f"Actualizó categoría '{updated_category.nombre}'",
                    modulo="PRODUCTOS",
                    tipo_accion="update",
                    nivel="info",
                    datos_adicionales={'categoria_id': updated_category.id}
                )
            except Exception as e:
                print(f"Error auditoría: {e}")

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"error": "Categoría no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            
            # Auditoría
            try:
                registrar_bitacora(
                    request=request,
                    usuario=request.user,
                    accion="Actualizar Categoría (Parcial)",
                    descripcion=f"Actualizó parcialmente categoría '{updated_category.nombre}'",
                    modulo="PRODUCTOS",
                    tipo_accion="update",
                    nivel="info",
                    datos_adicionales={'categoria_id': updated_category.id}
                )
            except Exception as e:
                print(f"Error auditoría: {e}")

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"error": "Categoría no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        category_data = {'id': category.id, 'nombre': category.nombre}
        category.delete()

        # Auditoría
        try:
            registrar_bitacora(
                request=request,
                usuario=request.user,
                accion="Eliminar Categoría",
                descripcion=f"Eliminó categoría '{category_data['nombre']}'",
                modulo="PRODUCTOS",
                tipo_accion="delete",
                nivel="warning",
                datos_adicionales=category_data
            )
        except Exception as e:
            print(f"Error auditoría: {e}")

        return Response(status=status.HTTP_204_NO_CONTENT)
