"""
Views para Ventas
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
from datetime import datetime

from .models import Venta, DetalleVenta
from .serializers import (
    VentaListSerializer,
    VentaDetailSerializer,
    VentaCreateSerializer,
    VentaUpdateSerializer,
    DetalleVentaSerializer
)
from apps.core.permissions import HasPermission
from apps.audit.helpers import registrar_creacion, registrar_actualizacion, registrar_eliminacion
from .utils import generar_pdf_venta


class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Ventas
    
    list: Listar ventas con filtros
    create: Crear nueva venta (completa automáticamente y actualiza stock)
    retrieve: Ver detalle de venta
    update: Actualizar venta
    partial_update: Actualizar campos específicos
    destroy: Eliminar venta (solo si está cancelada)
    
    Acciones personalizadas:
    - generar_pdf: Generar PDF de la factura/recibo
    - cancelar: Cancelar una venta (revierte stock)
    """
    queryset = Venta.objects.select_related(
        'cliente', 'vendedor'
    ).prefetch_related('detalles__producto').all()
    
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = {
        'list': ['ventas.view'],
        'retrieve': ['ventas.view'],
        'create': ['ventas.create'],
        'update': ['ventas.edit'],
        'partial_update': ['ventas.edit'],
        'destroy': ['ventas.delete'],
        'generar_pdf': ['ventas.view'],
        'cancelar': ['ventas.edit'],
    }
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'metodo_pago', 'cliente']
    search_fields = ['numero_venta', 'cliente__nombre', 'cliente__apellido', 'cliente__ci']
    ordering_fields = ['fecha_venta', 'total', 'numero_venta']
    ordering = ['-fecha_venta', '-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return VentaListSerializer
        elif self.action == 'create':
            return VentaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VentaUpdateSerializer
        return VentaDetailSerializer
    
    def get_queryset(self):
        """Filtrar queryset según permisos y parámetros"""
        queryset = super().get_queryset()
        
        # Filtrar por fecha si se proporciona
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__lte=fecha_hasta)
        
        return queryset
    
    def perform_create(self, serializer):
        """Crear venta con auditoría"""
        venta = serializer.save()
        registrar_creacion(self.request, venta, modulo="Ventas")
    
    def perform_update(self, serializer):
        """Actualizar venta con auditoría"""
        venta = serializer.save()
        registrar_actualizacion(self.request, venta, modulo="Ventas")
    
    def perform_destroy(self, instance):
        """Eliminar venta solo si está cancelada"""
        if instance.estado != Venta.ESTADO_CANCELADA:
            raise ValidationError(
                "Solo se pueden eliminar ventas canceladas. Use la acción 'cancelar' para cancelar una venta."
            )
        
        registrar_eliminacion(self.request, instance, modulo="Ventas")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        """Generar PDF de la factura/recibo de venta"""
        venta = self.get_object()
        
        try:
            pdf_buffer = generar_pdf_venta(venta)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="venta_{venta.numero_venta}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una venta (revierte stock)"""
        venta = self.get_object()
        
        if venta.estado == Venta.ESTADO_CANCELADA:
            return Response(
                {'error': 'La venta ya está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if venta.estado == Venta.ESTADO_COMPLETADA:
            # Revertir stock
            for detalle in venta.detalles.all():
                detalle.producto.actualizar_stock(detalle.cantidad, operacion='sumar')
                detalle.producto.save()
        
        venta.estado = Venta.ESTADO_CANCELADA
        venta.save()
        
        registrar_actualizacion(request, venta, modulo="Ventas")
        
        return Response({
            'message': 'Venta cancelada exitosamente.',
            'venta': VentaDetailSerializer(venta).data
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de ventas"""
        queryset = self.get_queryset()
        
        # Filtrar por rango de fechas
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__lte=fecha_hasta)
        
        # Solo ventas completadas
        ventas_completadas = queryset.filter(estado=Venta.ESTADO_COMPLETADA)
        
        total_ventas = ventas_completadas.count()
        total_ingresos = ventas_completadas.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        return Response({
            'total_ventas': total_ventas,
            'total_ingresos': float(total_ingresos),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        })

