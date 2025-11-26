"""
Views para Compras
CRUD completo con generación de PDF
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from .models import OrdenCompra, ItemOrdenCompra
from .serializers import (
    OrdenCompraListSerializer,
    OrdenCompraDetailSerializer,
    OrdenCompraCreateSerializer,
    OrdenCompraUpdateSerializer,
    ItemOrdenCompraSerializer
)
from apps.core.permissions import HasPermission
from apps.audit.helpers import registrar_creacion, registrar_actualizacion, registrar_eliminacion
from .utils import generar_pdf_orden_compra


class OrdenCompraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Órdenes de Compra
    
    list: Listar órdenes con filtros
    create: Crear nueva orden de compra
    retrieve: Ver detalle de orden
    update: Actualizar orden
    partial_update: Actualizar campos específicos
    destroy: Eliminar orden (solo si está cancelada)
    
    Acciones personalizadas:
    - generar_pdf: Generar PDF de la orden de compra
    - confirmar: Confirmar una orden
    - recibir: Recibir una orden (actualiza stock)
    - cancelar: Cancelar una orden (revierte stock si estaba recibida)
    """
    queryset = OrdenCompra.objects.select_related(
        'proveedor', 'creado_por'
    ).prefetch_related('items__producto').all()
    
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = {
        'list': ['compras.view'],
        'retrieve': ['compras.view'],
        'create': ['compras.create'],
        'update': ['compras.edit'],
        'partial_update': ['compras.edit'],
        'destroy': ['compras.delete'],
        'generar_pdf': ['compras.view'],
        'confirmar': ['compras.edit'],
        'recibir': ['compras.edit'],
        'cancelar': ['compras.edit'],
    }
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'proveedor']
    search_fields = ['numero_orden', 'proveedor__razon_social', 'proveedor__nit']
    ordering_fields = ['fecha_orden', 'total', 'numero_orden']
    ordering = ['-fecha_orden', '-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return OrdenCompraListSerializer
        elif self.action == 'create':
            return OrdenCompraCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrdenCompraUpdateSerializer
        return OrdenCompraDetailSerializer
    
    def get_queryset(self):
        """Filtrar queryset según permisos y parámetros"""
        queryset = super().get_queryset()
        
        # Filtrar por fecha si se proporciona
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_orden__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_orden__lte=fecha_hasta)
        
        return queryset
    
    def perform_create(self, serializer):
        """Crear orden con auditoría"""
        orden = serializer.save()
        registrar_creacion(self.request, orden, modulo="Compras")
    
    def perform_update(self, serializer):
        """Actualizar orden con auditoría"""
        orden = serializer.save()
        registrar_actualizacion(self.request, orden, modulo="Compras")
    
    def perform_destroy(self, instance):
        """Eliminar orden solo si está cancelada"""
        if instance.estado != OrdenCompra.ESTADO_CANCELADA:
            raise ValidationError(
                "Solo se pueden eliminar órdenes canceladas. Use la acción 'cancelar' para cancelar una orden."
            )
        
        registrar_eliminacion(self.request, instance, modulo="Compras")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        """Generar PDF de la orden de compra"""
        orden = self.get_object()
        
        try:
            pdf_buffer = generar_pdf_orden_compra(orden)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="orden_{orden.numero_orden}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar una orden de compra"""
        orden = self.get_object()
        
        if orden.estado != OrdenCompra.ESTADO_PENDIENTE:
            return Response(
                {'error': 'Solo se pueden confirmar órdenes pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orden.estado = OrdenCompra.ESTADO_CONFIRMADA
        orden.save()
        
        registrar_actualizacion(request, orden, modulo="Compras")
        
        return Response({
            'message': 'Orden confirmada exitosamente.',
            'orden': OrdenCompraDetailSerializer(orden).data
        })
    
    @action(detail=True, methods=['post'])
    def recibir(self, request, pk=None):
        """Recibir una orden de compra (actualiza stock)"""
        orden = self.get_object()
        
        if orden.estado not in [OrdenCompra.ESTADO_PENDIENTE, OrdenCompra.ESTADO_CONFIRMADA]:
            return Response(
                {'error': 'Solo se pueden recibir órdenes pendientes o confirmadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar stock de todos los items
        for item in orden.items.all():
            item.producto.actualizar_stock(item.cantidad, operacion='sumar')
            item.producto.save()
        
        orden.estado = OrdenCompra.ESTADO_RECIBIDA
        orden.save()
        
        registrar_actualizacion(request, orden, modulo="Compras")
        
        return Response({
            'message': 'Orden recibida exitosamente. Stock actualizado.',
            'orden': OrdenCompraDetailSerializer(orden).data
        })
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una orden de compra (revierte stock si estaba recibida)"""
        orden = self.get_object()
        
        if orden.estado == OrdenCompra.ESTADO_CANCELADA:
            return Response(
                {'error': 'La orden ya está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if orden.estado == OrdenCompra.ESTADO_RECIBIDA:
            # Revertir stock
            for item in orden.items.all():
                item.producto.actualizar_stock(item.cantidad, operacion='restar')
                item.producto.save()
        
        orden.estado = OrdenCompra.ESTADO_CANCELADA
        orden.save()
        
        registrar_actualizacion(request, orden, modulo="Compras")
        
        return Response({
            'message': 'Orden cancelada exitosamente.',
            'orden': OrdenCompraDetailSerializer(orden).data
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de compras"""
        queryset = self.get_queryset()
        
        # Filtrar por rango de fechas
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_orden__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_orden__lte=fecha_hasta)
        
        # Solo órdenes recibidas
        ordenes_recibidas = queryset.filter(estado=OrdenCompra.ESTADO_RECIBIDA)
        
        total_ordenes = ordenes_recibidas.count()
        total_gastos = ordenes_recibidas.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        return Response({
            'total_ordenes': total_ordenes,
            'total_gastos': float(total_gastos),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        })

