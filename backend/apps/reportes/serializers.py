"""
Serializers para Reportes
"""

from rest_framework import serializers
from datetime import datetime, date
from django.utils import timezone


class ReporteFiltroSerializer(serializers.Serializer):
    """Serializer para validar filtros de reportes"""

    tipo_periodo = serializers.ChoiceField(
        choices=[
            ("dia", "Día"),
            ("semana", "Semana"),
            ("mes", "Mes"),
            ("anio", "Año"),
            ("personalizado", "Rango Personalizado"),
        ],
        default="mes",
        help_text="Tipo de período para el reporte",
    )

    fecha_inicio = serializers.DateField(
        required=False,
        help_text="Fecha de inicio (requerida para rango personalizado)",
    )

    fecha_fin = serializers.DateField(
        required=False,
        help_text="Fecha de fin (requerida para rango personalizado)",
    )

    formato = serializers.ChoiceField(
        choices=[("json", "JSON"), ("pdf", "PDF")],
        default="json",
        help_text="Formato de salida del reporte",
    )

    def validate(self, data):
        """Validar que las fechas sean consistentes"""
        tipo_periodo = data.get("tipo_periodo")
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")

        if tipo_periodo == "personalizado":
            if not fecha_inicio or not fecha_fin:
                raise serializers.ValidationError(
                    "Las fechas de inicio y fin son requeridas para rango personalizado"
                )
            if fecha_inicio > fecha_fin:
                raise serializers.ValidationError(
                    "La fecha de inicio debe ser anterior a la fecha de fin"
                )

        return data


class ReporteVentasSerializer(serializers.Serializer):
    """Serializer para reporte de ventas"""

    total_ventas = serializers.DecimalField(max_digits=10, decimal_places=2)
    cantidad_ventas = serializers.IntegerField()
    ventas_por_metodo_pago = serializers.DictField()
    ventas_por_dia = serializers.ListField()
    productos_mas_vendidos = serializers.ListField()
    clientes_mas_frecuentes = serializers.ListField()
    periodo = serializers.DictField()


class ReporteComprasSerializer(serializers.Serializer):
    """Serializer para reporte de compras"""

    total_compras = serializers.DecimalField(max_digits=10, decimal_places=2)
    cantidad_ordenes = serializers.IntegerField()
    compras_por_proveedor = serializers.ListField()
    compras_por_dia = serializers.ListField()
    productos_mas_comprados = serializers.ListField()
    periodo = serializers.DictField()


class ReporteInventarioSerializer(serializers.Serializer):
    """Serializer para reporte de inventario"""

    total_productos = serializers.IntegerField()
    productos_activos = serializers.IntegerField()
    productos_agotados = serializers.IntegerField()
    productos_bajo_stock = serializers.IntegerField()
    productos_vencidos = serializers.IntegerField()
    productos_proximos_vencer = serializers.IntegerField()
    valor_total_inventario = serializers.DecimalField(max_digits=10, decimal_places=2)
    movimientos_recientes = serializers.ListField()


class ReporteMembresiasSerializer(serializers.Serializer):
    """Serializer para reporte de membresías"""

    total_membresias = serializers.IntegerField()
    membresias_activas = serializers.IntegerField()
    membresias_vencidas = serializers.IntegerField()
    nuevas_membresias = serializers.IntegerField()
    renovaciones = serializers.IntegerField()
    ingresos_membresias = serializers.DecimalField(max_digits=10, decimal_places=2)
    membresias_por_plan = serializers.ListField()
    periodo = serializers.DictField()


class ReporteFinancieroSerializer(serializers.Serializer):
    """Serializer para reporte financiero"""

    ingresos_totales = serializers.DecimalField(max_digits=10, decimal_places=2)
    egresos_totales = serializers.DecimalField(max_digits=10, decimal_places=2)
    ganancia_neta = serializers.DecimalField(max_digits=10, decimal_places=2)
    ingresos_por_fuente = serializers.DictField()
    egresos_por_categoria = serializers.DictField()
    periodo = serializers.DictField()
