"""
Views para Productos
CRUD completo con filtros, búsqueda y paginación
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Producto
from .serializers import (
    ProductoListSerializer,
    ProductoDetailSerializer,
    ProductoCreateUpdateSerializer,
    ActualizarStockSerializer
)
from apps.core.permissions import HasPermission
from apps.audit.helpers import registrar_creacion, registrar_actualizacion, registrar_eliminacion


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Productos
    
    list: Listar productos con filtros
    create: Registrar nuevo producto
    retrieve: Ver detalle de producto
    update: Actualizar producto completo
    partial_update: Actualizar campos específicos
    destroy: Eliminar producto
    
    Acciones personalizadas:
    - actualizar_stock: Sumar o restar stock
    - bajo_stock: Productos con stock bajo
    - activos: Solo productos activos
    """
    queryset = Producto.objects.select_related(
        'categoria', 'proveedor', 'promocion', 'creado_por', 'modificado_por'
    ).all()
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = {
        'list': ['productos.view'],
        'retrieve': ['productos.view'],
        'create': ['productos.create'],
        'update': ['productos.edit'],
        'partial_update': ['productos.edit'],
        'destroy': ['productos.delete'],
        'actualizar_stock': ['productos.edit'],
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'proveedor', 'estado', 'promocion']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'codigo', 'precio', 'stock', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_context(self):
        """Agregar request al contexto para generar URLs absolutas de imágenes"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductoCreateUpdateSerializer
        elif self.action == 'actualizar_stock':
            return ActualizarStockSerializer
        return ProductoDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por búsqueda general
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(codigo__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Filtro por rango de precio
        precio_min = self.request.query_params.get('precio_min', None)
        precio_max = self.request.query_params.get('precio_max', None)
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)
        
        # Filtro por stock bajo
        from django.db.models import F
        stock_bajo = self.request.query_params.get('stock_bajo', None)
        if stock_bajo == 'true':
            queryset = queryset.filter(stock__lte=F('stock_minimo'))
        
        return queryset
    
    def perform_create(self, serializer):
        producto = serializer.save()
        registrar_creacion(self.request, producto, modulo="Productos")
    
    def perform_update(self, serializer):
        producto = serializer.save()
        registrar_actualizacion(self.request, producto, modulo="Productos")
    
    def perform_destroy(self, instance):
        registrar_eliminacion(self.request, instance, modulo="Productos")
        instance.delete()
    
    @action(detail=True, methods=['post'], url_path='actualizar-stock')
    def actualizar_stock(self, request, pk=None):
        """
        Actualizar stock del producto (sumar o restar)
        
        POST /api/productos/{id}/actualizar-stock/
        Body: {
            "cantidad": 10,
            "operacion": "sumar",  # o "restar"
            "motivo": "Compra a proveedor"
        }
        """
        producto = self.get_object()
        serializer = ActualizarStockSerializer(data=request.data)
        
        if serializer.is_valid():
            cantidad = serializer.validated_data['cantidad']
            operacion = serializer.validated_data['operacion']
            motivo = serializer.validated_data.get('motivo', '')
            
            stock_anterior = producto.stock
            
            try:
                producto.actualizar_stock(cantidad, operacion)
                
                # Log de auditoría
                registrar_actualizacion(request, producto, modulo="Productos")
                
                return Response({
                    'message': f'Stock actualizado correctamente',
                    'stock_anterior': stock_anterior,
                    'stock_actual': producto.stock,
                    'operacion': operacion,
                    'cantidad': cantidad
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='bajo-stock')
    def bajo_stock(self, request):
        """
        Listar productos con stock bajo (stock <= stock_mínimo)
        
        GET /api/productos/bajo-stock/
        """
        from django.db.models import F
        
        productos = self.get_queryset().filter(
            stock__lte=F('stock_minimo'),
            estado=Producto.ESTADO_ACTIVO
        )
        
        page = self.paginate_queryset(productos)
        if page is not None:
            serializer = ProductoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Listar solo productos activos
        
        GET /api/productos/activos/
        """
        productos = self.get_queryset().filter(estado=Producto.ESTADO_ACTIVO)
        
        page = self.paginate_queryset(productos)
        if page is not None:
            serializer = ProductoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Estadísticas generales de productos
        
        GET /api/productos/estadisticas/
        """
        from django.db.models import Sum, Count, Avg, F
        
        queryset = self.get_queryset()
        
        stats = {
            'total_productos': queryset.count(),
            'productos_activos': queryset.filter(estado=Producto.ESTADO_ACTIVO).count(),
            'productos_agotados': queryset.filter(estado=Producto.ESTADO_AGOTADO).count(),
            'productos_bajo_stock': queryset.filter(stock__lte=F('stock_minimo')).count(),
            'valor_total_inventario': queryset.aggregate(
                total=Sum(F('stock') * F('precio'))
            )['total'] or 0,
            'stock_total': queryset.aggregate(total=Sum('stock'))['total'] or 0,
            'precio_promedio': queryset.aggregate(promedio=Avg('precio'))['promedio'] or 0,
        }
        
        return Response(stats)
