"""
Views para Productos
CRUD completo con filtros, búsqueda y paginación
"""

from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Producto, MovimientoInventario
from .serializers import (
    ProductoListSerializer,
    ProductoDetailSerializer,
    ProductoCreateUpdateSerializer,
    ActualizarStockSerializer,
    MovimientoInventarioSerializer,
    AjustarStockSerializer,
)
from apps.core.permissions import HasPermission
from apps.audit.helpers import (
    registrar_creacion,
    registrar_actualizacion,
    registrar_eliminacion,
)


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
        "categoria", "proveedor", "promocion", "creado_por", "modificado_por"
    ).all()
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = {
        "list": ["productos.view"],
        "retrieve": ["productos.view"],
        "create": ["productos.create"],
        "update": ["productos.edit"],
        "partial_update": ["productos.edit"],
        "destroy": ["productos.delete"],
        "actualizar_stock": ["productos.edit"],
        "alertas": ["productos.view"],
        "bajo_stock": ["productos.view"],
        "activos": ["productos.view"],
        "estadisticas": ["productos.view"],
    }
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["categoria", "proveedor", "estado", "promocion"]
    search_fields = ["nombre", "codigo", "descripcion"]
    ordering_fields = ["nombre", "codigo", "precio", "stock", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_context(self):
        """Agregar request al contexto para generar URLs absolutas de imágenes"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        if self.action == "list":
            return ProductoListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProductoCreateUpdateSerializer
        elif self.action == "actualizar_stock":
            return ActualizarStockSerializer
        return ProductoDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por búsqueda general
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(codigo__icontains=search)
                | Q(descripcion__icontains=search)
            )

        # Filtro por rango de precio
        precio_min = self.request.query_params.get("precio_min", None)
        precio_max = self.request.query_params.get("precio_max", None)
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)

        # Filtro por stock bajo
        from django.db.models import F

        stock_bajo = self.request.query_params.get("stock_bajo", None)
        if stock_bajo == "true":
            queryset = queryset.filter(stock__lte=F("stock_minimo"))

        return queryset

    def perform_create(self, serializer):
        producto = serializer.save()
        registrar_creacion(self.request, producto, modulo="Productos")

    def perform_update(self, serializer):
        producto = serializer.save()
        registrar_actualizacion(self.request, producto, modulo="Productos")

    def perform_destroy(self, instance):
        """
        Eliminar producto con validaciones previas

        No se puede eliminar si tiene:
        - Ventas asociadas (DetalleVenta)
        - Órdenes de compra asociadas (ItemOrdenCompra)
        """
        from apps.ventas.models import DetalleVenta
        from apps.compras.models import ItemOrdenCompra

        # Verificar si tiene ventas asociadas
        ventas_count = DetalleVenta.objects.filter(producto=instance).count()
        if ventas_count > 0:
            raise serializers.ValidationError(
                f"No se puede eliminar el producto '{instance.nombre}' porque tiene {ventas_count} venta(s) asociada(s). "
                "Considere cambiar el estado a 'DESCONTINUADO' en lugar de eliminar."
            )

        # Verificar si tiene órdenes de compra asociadas
        compras_count = ItemOrdenCompra.objects.filter(producto=instance).count()
        if compras_count > 0:
            raise serializers.ValidationError(
                f"No se puede eliminar el producto '{instance.nombre}' porque tiene {compras_count} orden(es) de compra asociada(s). "
                "Considere cambiar el estado a 'DESCONTINUADO' en lugar de eliminar."
            )

        registrar_eliminacion(self.request, instance, modulo="Productos")
        instance.delete()

    @action(detail=True, methods=["post"], url_path="actualizar-stock")
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
            cantidad = serializer.validated_data["cantidad"]
            operacion = serializer.validated_data["operacion"]
            motivo = serializer.validated_data.get("motivo", "")

            stock_anterior = producto.stock

            try:
                producto.actualizar_stock(cantidad, operacion)

                # Log de auditoría
                registrar_actualizacion(request, producto, modulo="Productos")

                return Response(
                    {
                        "message": f"Stock actualizado correctamente",
                        "stock_anterior": stock_anterior,
                        "stock_actual": producto.stock,
                        "operacion": operacion,
                        "cantidad": cantidad,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="bajo-stock")
    def bajo_stock(self, request):
        """
        Listar productos con stock bajo (stock <= stock_mínimo)

        GET /api/productos/bajo-stock/
        """
        from django.db.models import F

        productos = self.get_queryset().filter(
            stock__lte=F("stock_minimo"), estado=Producto.ESTADO_ACTIVO
        )

        page = self.paginate_queryset(productos)
        if page is not None:
            serializer = ProductoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
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

    @action(detail=False, methods=["get"])
    def estadisticas(self, request):
        """
        Estadísticas generales de productos

        GET /api/productos/estadisticas/
        """
        from django.db.models import Sum, Count, Avg, F

        queryset = self.get_queryset()

        stats = {
            "total_productos": queryset.count(),
            "productos_activos": queryset.filter(estado=Producto.ESTADO_ACTIVO).count(),
            "productos_agotados": queryset.filter(
                estado=Producto.ESTADO_AGOTADO
            ).count(),
            "productos_bajo_stock": queryset.filter(
                stock__lte=F("stock_minimo")
            ).count(),
            "valor_total_inventario": queryset.aggregate(
                total=Sum(F("stock") * F("precio"))
            )["total"]
            or 0,
            "stock_total": queryset.aggregate(total=Sum("stock"))["total"] or 0,
            "precio_promedio": queryset.aggregate(promedio=Avg("precio"))["promedio"]
            or 0,
        }

        return Response(stats)

    @action(detail=False, methods=["get"])
    def alertas(self, request):
        """
        Consultar alertas de inventario

        Identifica productos con condiciones de riesgo:
        - Stock bajo (stock <= stock_minimo)
        - Stock crítico (stock <= 50% stock_minimo)
        - Próximos a vencer (<=30 días)
        - Vencidos

        GET /api/productos/productos/alertas/

        Query params:
        - tipo: filtrar por tipo de alerta (stock_bajo, stock_critico, proximo_vencer, vencido)
        """
        from datetime import date, timedelta
        from django.db.models import F, Q

        queryset = self.get_queryset().filter(estado=Producto.ESTADO_ACTIVO)
        tipo_alerta = request.query_params.get("tipo", None)

        alertas = {
            "stock_bajo": [],
            "stock_critico": [],
            "proximo_vencer": [],
            "vencido": [],
            "total_alertas": 0,
        }

        # Productos con stock bajo
        productos_stock_bajo = queryset.filter(stock__lte=F("stock_minimo"))

        for producto in productos_stock_bajo:
            alerta_data = {
                "id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "stock_actual": producto.stock,
                "stock_minimo": producto.stock_minimo,
                "categoria": producto.categoria.nombre if producto.categoria else None,
                "proveedor": producto.proveedor.razon_social
                if producto.proveedor
                else None,
                "unidad_medida": producto.unidad_medida,
            }

            # Determinar si es crítico o solo bajo
            if producto.stock_critico:
                alerta_data["tipo"] = "stock_critico"
                alerta_data["severidad"] = "critica"
                alerta_data["mensaje"] = (
                    f"Stock crítico: {producto.stock} unidades (mínimo: {producto.stock_minimo})"
                )
                alertas["stock_critico"].append(alerta_data)
            else:
                alerta_data["tipo"] = "stock_bajo"
                alerta_data["severidad"] = "alta"
                alerta_data["mensaje"] = (
                    f"Stock bajo: {producto.stock} unidades (mínimo: {producto.stock_minimo})"
                )
                alertas["stock_bajo"].append(alerta_data)

        # Productos próximos a vencer o vencidos
        fecha_limite = date.today() + timedelta(days=30)
        productos_con_vencimiento = queryset.filter(fecha_vencimiento__isnull=False)

        for producto in productos_con_vencimiento:
            alerta_data = {
                "id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "stock_actual": producto.stock,
                "fecha_vencimiento": producto.fecha_vencimiento.isoformat(),
                "dias_hasta_vencimiento": producto.dias_hasta_vencimiento,
                "categoria": producto.categoria.nombre if producto.categoria else None,
                "proveedor": producto.proveedor.razon_social
                if producto.proveedor
                else None,
                "unidad_medida": producto.unidad_medida,
            }

            if producto.esta_vencido:
                alerta_data["tipo"] = "vencido"
                alerta_data["severidad"] = "critica"
                alerta_data["mensaje"] = (
                    f"Producto vencido desde hace {abs(producto.dias_hasta_vencimiento)} días"
                )
                alertas["vencido"].append(alerta_data)
            elif producto.proximo_a_vencer:
                alerta_data["tipo"] = "proximo_vencer"
                alerta_data["severidad"] = "alta"
                alerta_data["mensaje"] = (
                    f"Vence en {producto.dias_hasta_vencimiento} días"
                )
                alertas["proximo_vencer"].append(alerta_data)

        # Calcular total
        alertas["total_alertas"] = (
            len(alertas["stock_bajo"])
            + len(alertas["stock_critico"])
            + len(alertas["proximo_vencer"])
            + len(alertas["vencido"])
        )

        # Si se especifica un tipo, mantener el formato completo pero destacar el tipo filtrado
        # El frontend siempre espera el formato completo con todas las categorías

        # Registrar consulta en auditoría
        from apps.audit.helpers import registrar_bitacora

        registrar_bitacora(
            request=request,
            accion="Consultar Alertas de Inventario",
            descripcion=f"Usuario consultó alertas de inventario. Total: {alertas['total_alertas']}",
            modulo="Inventario",
            tipo_accion="read",
            nivel="info",
        )

        return Response(alertas)

    @action(detail=False, methods=["post"], url_path="ajustar-stock")
    def ajustar_stock(self, request):
        """
        Ajustar stock de un producto - CU Ajuste de Inventario

        Permite corregir diferencias entre inventario físico y registrado.
        Calcula automáticamente la diferencia y genera movimiento de tipo AJUSTE.

        POST /api/productos/ajustar-stock/
        Body: {
            "producto_id": 1,
            "cantidad_real": 50,
            "motivo": "Ajuste por inventario físico - Faltante detectado en revisión mensual",
            "referencia": "INV-2024-001"
        }
        """
        serializer = AjustarStockSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        producto_id = serializer.validated_data["producto_id"]
        cantidad_real = serializer.validated_data["cantidad_real"]
        motivo = serializer.validated_data["motivo"]
        referencia = serializer.validated_data.get("referencia", "")

        try:
            producto = Producto.objects.get(id=producto_id)

            # Guardar stock anterior
            stock_anterior = producto.stock

            # Calcular diferencia
            diferencia = cantidad_real - stock_anterior

            # Si no hay diferencia, no hacer nada
            if diferencia == 0:
                return Response(
                    {
                        "message": "El stock registrado coincide con el stock físico. No se requiere ajuste.",
                        "stock_actual": stock_anterior,
                        "cantidad_real": cantidad_real,
                        "diferencia": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Actualizar stock directamente
            producto.stock = cantidad_real

            # Actualizar estado según stock
            if producto.stock == 0:
                producto.estado = Producto.ESTADO_AGOTADO
            elif producto.estado == Producto.ESTADO_AGOTADO and producto.stock > 0:
                producto.estado = Producto.ESTADO_ACTIVO

            producto.modificado_por = request.user
            producto.save()

            # Crear movimiento de inventario
            movimiento = MovimientoInventario.objects.create(
                producto=producto,
                usuario=request.user,
                tipo=MovimientoInventario.TIPO_AJUSTE,
                cantidad=abs(diferencia),
                cantidad_anterior=stock_anterior,
                cantidad_nueva=cantidad_real,
                motivo=motivo,
                referencia=referencia,
            )

            # Registrar en auditoría
            registrar_actualizacion(request, producto, modulo="Inventario")

            return Response(
                {
                    "message": "Ajuste de inventario realizado exitosamente",
                    "producto": {
                        "id": producto.id,
                        "nombre": producto.nombre,
                        "codigo": producto.codigo,
                    },
                    "ajuste": {
                        "stock_anterior": stock_anterior,
                        "stock_actual": cantidad_real,
                        "diferencia": diferencia,
                        "tipo_ajuste": "Positivo (Exceso)"
                        if diferencia > 0
                        else "Negativo (Faltante)",
                        "motivo": motivo,
                        "referencia": referencia,
                    },
                    "movimiento_id": movimiento.id,
                },
                status=status.HTTP_200_OK,
            )

        except Producto.DoesNotExist:
            return Response(
                {"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error al ajustar stock: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar movimientos de inventario (solo lectura)

    list: Listar todos los movimientos con filtros
    retrieve: Ver detalle de un movimiento

    Filtros disponibles:
    - producto: ID del producto
    - tipo: ENTRADA, SALIDA, AJUSTE
    - fecha_desde, fecha_hasta
    """

    queryset = MovimientoInventario.objects.select_related("producto", "usuario").all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = {
        "list": ["productos.view"],
        "retrieve": ["productos.view"],
    }
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["producto", "tipo", "usuario"]
    search_fields = ["producto__nombre", "producto__codigo", "motivo", "referencia"]
    ordering_fields = ["created_at", "tipo"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get("fecha_desde", None)
        fecha_hasta = self.request.query_params.get("fecha_hasta", None)

        if fecha_desde:
            queryset = queryset.filter(created_at__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(created_at__lte=fecha_hasta)

        return queryset
