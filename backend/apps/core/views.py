from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema

from apps.membresias.models import Membresia, InscripcionMembresia
from apps.ventas.models import Venta, DetalleVenta
from apps.compras.models import OrdenCompra
from apps.clients.models import Client
from apps.productos.models import Producto, MovimientoInventario
from apps.asistencias.models import AsistenciaClase


@extend_schema(tags=["Dashboard"], responses={200: dict})
class DashboardChartsView(APIView):
    """
    Endpoint para obtener datos de gráficas del dashboard
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Obtener datos para gráficas del dashboard"""

        # Obtener fecha actual y calcular rangos
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # Últimos 6 meses para gráfica de ingresos
        months_data = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if i == 0:
                month_end = now
            else:
                next_month = month_start + timedelta(days=32)
                month_end = next_month.replace(day=1) - timedelta(seconds=1)

            # Ingresos de membresías del mes
            membresias_ingresos = (
                InscripcionMembresia.objects.filter(
                    created_at__gte=month_start, created_at__lte=month_end
                ).aggregate(total=Sum("monto"))["total"]
                or 0
            )

            # Ingresos de ventas del mes
            ventas_ingresos = (
                Venta.objects.filter(
                    estado=Venta.ESTADO_COMPLETADA,
                    fecha_venta__gte=month_start,
                    fecha_venta__lte=month_end,
                ).aggregate(total=Sum("total"))["total"]
                or 0
            )

            total_ingresos = float(membresias_ingresos) + float(ventas_ingresos)

            months_data.append(
                {
                    "mes": month_date.strftime("%b %Y"),
                    "ingresos": total_ingresos,
                    "membresias": float(membresias_ingresos),
                    "ventas": float(ventas_ingresos),
                }
            )

        # Ventas vs Compras (últimos 6 meses)
        ventas_compras_data = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if i == 0:
                month_end = now
            else:
                next_month = month_start + timedelta(days=32)
                month_end = next_month.replace(day=1) - timedelta(seconds=1)

            ventas_total = (
                Venta.objects.filter(
                    estado=Venta.ESTADO_COMPLETADA,
                    fecha_venta__gte=month_start,
                    fecha_venta__lte=month_end,
                ).aggregate(total=Sum("total"))["total"]
                or 0
            )

            compras_total = (
                OrdenCompra.objects.filter(
                    estado=OrdenCompra.ESTADO_RECIBIDA,
                    fecha_orden__gte=month_start,
                    fecha_orden__lte=month_end,
                ).aggregate(total=Sum("total"))["total"]
                or 0
            )

            ventas_compras_data.append(
                {
                    "mes": month_date.strftime("%b"),
                    "ventas": float(ventas_total),
                    "compras": float(compras_total),
                }
            )

        # Membresías por estado
        membresias_activas = Membresia.objects.filter(
            estado="activo", fecha_fin__gte=timezone.now().date()
        ).count()

        membresias_vencidas = Membresia.objects.filter(
            Q(estado="vencido") | Q(fecha_fin__lt=timezone.now().date())
        ).count()

        membresias_suspendidas = Membresia.objects.filter(estado="suspendido").count()

        membresias_estado = [
            {"name": "Activas", "value": membresias_activas, "color": "#10b981"},
            {"name": "Vencidas", "value": membresias_vencidas, "color": "#ef4444"},
            {
                "name": "Suspendidas",
                "value": membresias_suspendidas,
                "color": "#f59e0b",
            },
        ]

        # Tendencias de clientes (últimos 6 meses)
        clientes_tendencia = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if i == 0:
                month_end = now
            else:
                next_month = month_start + timedelta(days=32)
                month_end = next_month.replace(day=1) - timedelta(seconds=1)

            nuevos_clientes = Client.objects.filter(
                created_at__gte=month_start, created_at__lte=month_end
            ).count()

            clientes_tendencia.append(
                {"mes": month_date.strftime("%b"), "clientes": nuevos_clientes}
            )

        # Top productos más vendidos (últimos 30 días)
        desde = now - timedelta(days=30)
        top_productos = (
            DetalleVenta.objects.filter(
                venta__estado=Venta.ESTADO_COMPLETADA, venta__fecha_venta__gte=desde
            )
            .values("producto__nombre")
            .annotate(total_vendido=Sum("cantidad"))
            .order_by("-total_vendido")[:5]
        )

        productos_data = [
            {
                "nombre": item["producto__nombre"] or "Sin nombre",
                "cantidad": item["total_vendido"] or 0,
            }
            for item in top_productos
        ]

        # Comparación mes actual vs mes anterior
        mes_actual_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mes_anterior_end = mes_actual_start - timedelta(seconds=1)
        mes_anterior_start = mes_anterior_end.replace(day=1)

        # Ingresos mes actual
        ingresos_mes_actual = (
            InscripcionMembresia.objects.filter(
                created_at__gte=mes_actual_start
            ).aggregate(total=Sum("monto"))["total"]
            or 0
        )

        ingresos_mes_actual += (
            Venta.objects.filter(
                estado=Venta.ESTADO_COMPLETADA, fecha_venta__gte=mes_actual_start
            ).aggregate(total=Sum("total"))["total"]
            or 0
        )

        # Ingresos mes anterior
        ingresos_mes_anterior = (
            InscripcionMembresia.objects.filter(
                created_at__gte=mes_anterior_start, created_at__lte=mes_anterior_end
            ).aggregate(total=Sum("monto"))["total"]
            or 0
        )

        ingresos_mes_anterior += (
            Venta.objects.filter(
                estado=Venta.ESTADO_COMPLETADA,
                fecha_venta__gte=mes_anterior_start,
                fecha_venta__lte=mes_anterior_end,
            ).aggregate(total=Sum("total"))["total"]
            or 0
        )

        variacion_ingresos = 0
        if ingresos_mes_anterior > 0:
            variacion_ingresos = (
                (float(ingresos_mes_actual) - float(ingresos_mes_anterior))
                / float(ingresos_mes_anterior)
            ) * 100

        # Resumen financiero
        total_ingresos = float(ingresos_mes_actual)
        total_gastos = (
            OrdenCompra.objects.filter(
                estado=OrdenCompra.ESTADO_RECIBIDA, fecha_orden__gte=mes_actual_start
            ).aggregate(total=Sum("total"))["total"]
            or 0
        )
        total_gastos = float(total_gastos)
        ganancia_neta = total_ingresos - total_gastos

        return Response(
            {
                "ingresos_mensuales": months_data,
                "ventas_vs_compras": ventas_compras_data,
                "membresias_estado": membresias_estado,
                "clientes_tendencia": clientes_tendencia,
                "top_productos": productos_data,
                "comparacion_mes": {
                    "mes_actual": float(ingresos_mes_actual),
                    "mes_anterior": float(ingresos_mes_anterior),
                    "variacion_porcentaje": round(variacion_ingresos, 2),
                },
                "resumen_financiero": {
                    "ingresos": total_ingresos,
                    "gastos": total_gastos,
                    "ganancia_neta": ganancia_neta,
                    "margen_ganancia": round(
                        (ganancia_neta / total_ingresos * 100)
                        if total_ingresos > 0
                        else 0,
                        2,
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )
