"""
Views para Reportes
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone

from .serializers import (
    ReporteFiltroSerializer,
    ReporteVentasSerializer,
    ReporteComprasSerializer,
    ReporteInventarioSerializer,
    ReporteMembresiasSerializer,
    ReporteFinancieroSerializer,
)
from .utils import (
    calcular_periodo,
    generar_reporte_ventas,
    generar_reporte_compras,
    generar_reporte_inventario,
    generar_reporte_membresias,
    generar_reporte_financiero,
)
from .pdf_utils import generar_pdf_reporte
from apps.core.permissions import HasPermission
from apps.audit.helpers import registrar_bitacora


class ReporteViewSet(viewsets.ViewSet):
    """
    ViewSet para generar reportes dinámicos

    Acciones disponibles:
    - ventas: Reporte de ventas
    - compras: Reporte de compras
    - inventario: Reporte de inventario
    - membresias: Reporte de membresías
    - financiero: Reporte financiero consolidado
    """

    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = {
        "ventas": ["report.view"],
        "compras": ["report.view"],
        "inventario": ["report.view"],
        "membresias": ["report.view"],
        "financiero": ["report.view"],
    }

    def _get_permission_key(self, action_name):
        """Obtiene la clave de permiso para una acción"""
        return action_name

    @action(detail=False, methods=["get", "post"])
    def ventas(self, request):
        """
        Generar reporte de ventas

        Query params o Body:
        - tipo_periodo: 'dia', 'semana', 'mes', 'anio', 'personalizado'
        - fecha_inicio: (requerido para personalizado)
        - fecha_fin: (requerido para personalizado)
        - formato: 'json' o 'pdf' (default: 'json')
        """
        serializer = ReporteFiltroSerializer(data=request.data or request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        tipo_periodo = data.get("tipo_periodo", "mes")
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        formato = data.get("formato", "json")

        try:
            fecha_inicio, fecha_fin = calcular_periodo(
                tipo_periodo, fecha_inicio, fecha_fin
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Generar reporte
        reporte_data = generar_reporte_ventas(fecha_inicio, fecha_fin)

        # Registrar en auditoría
        registrar_bitacora(
            request=request,
            accion="Generar Reporte de Ventas",
            descripcion=f"Reporte generado para período {fecha_inicio} - {fecha_fin}",
            modulo="Reportes",
            tipo_accion="read",
            nivel="info",
        )

        # Retornar según formato
        if formato == "pdf":
            pdf_buffer = generar_pdf_reporte(
                reporte_data, "ventas", reporte_data.get("periodo")
            )
            response = HttpResponse(
                pdf_buffer.getvalue(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="reporte_ventas_{fecha_inicio}_{fecha_fin}.pdf"'
            )
            return response

        return Response(reporte_data)

    @action(detail=False, methods=["get", "post"])
    def compras(self, request):
        """
        Generar reporte de compras

        Query params o Body:
        - tipo_periodo: 'dia', 'semana', 'mes', 'anio', 'personalizado'
        - fecha_inicio: (requerido para personalizado)
        - fecha_fin: (requerido para personalizado)
        - formato: 'json' o 'pdf' (default: 'json')
        """
        serializer = ReporteFiltroSerializer(data=request.data or request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        tipo_periodo = data.get("tipo_periodo", "mes")
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        formato = data.get("formato", "json")

        try:
            fecha_inicio, fecha_fin = calcular_periodo(
                tipo_periodo, fecha_inicio, fecha_fin
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Generar reporte
        reporte_data = generar_reporte_compras(fecha_inicio, fecha_fin)

        # Registrar en auditoría
        registrar_bitacora(
            request=request,
            accion="Generar Reporte de Compras",
            descripcion=f"Reporte generado para período {fecha_inicio} - {fecha_fin}",
            modulo="Reportes",
            tipo_accion="read",
            nivel="info",
        )

        # Retornar según formato
        if formato == "pdf":
            pdf_buffer = generar_pdf_reporte(
                reporte_data, "compras", reporte_data.get("periodo")
            )
            response = HttpResponse(
                pdf_buffer.getvalue(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="reporte_compras_{fecha_inicio}_{fecha_fin}.pdf"'
            )
            return response

        return Response(reporte_data)

    @action(detail=False, methods=["get", "post"])
    def inventario(self, request):
        """
        Generar reporte de inventario (no requiere período)

        Query params o Body:
        - formato: 'json' o 'pdf' (default: 'json')
        - search: Término de búsqueda (opcional)
        - estado: Filtro por estado (opcional)
        - stock_bajo: 'true' o 'false' para filtrar solo stock bajo (opcional)
        """
        serializer = ReporteFiltroSerializer(data=request.data or request.query_params)
        if not serializer.is_valid():
            # Inventario no requiere período, solo formato
            formato = request.query_params.get("formato", "json")
        else:
            formato = serializer.validated_data.get("formato", "json")

        # Obtener filtros opcionales
        search = request.query_params.get("search") or request.data.get("search")
        estado = request.query_params.get("estado") or request.data.get("estado")
        stock_bajo_param = request.query_params.get("stock_bajo") or request.data.get("stock_bajo")
        stock_bajo = stock_bajo_param == "true" or stock_bajo_param is True

        # Generar reporte con filtros
        reporte_data = generar_reporte_inventario(
            search=search, estado=estado, stock_bajo=stock_bajo
        )

        # Registrar en auditoría
        registrar_bitacora(
            request=request,
            accion="Generar Reporte de Inventario",
            descripcion="Reporte de inventario generado",
            modulo="Reportes",
            tipo_accion="read",
            nivel="info",
        )

        # Retornar según formato
        if formato == "pdf":
            pdf_buffer = generar_pdf_reporte(reporte_data, "inventario", None)
            response = HttpResponse(
                pdf_buffer.getvalue(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="reporte_inventario_{timezone.now().date()}.pdf"'
            )
            return response

        return Response(reporte_data)

    @action(detail=False, methods=["get", "post"])
    def membresias(self, request):
        """
        Generar reporte de membresías

        Query params o Body:
        - tipo_periodo: 'dia', 'semana', 'mes', 'anio', 'personalizado'
        - fecha_inicio: (requerido para personalizado)
        - fecha_fin: (requerido para personalizado)
        - formato: 'json' o 'pdf' (default: 'json')
        """
        serializer = ReporteFiltroSerializer(data=request.data or request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        tipo_periodo = data.get("tipo_periodo", "mes")
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        formato = data.get("formato", "json")

        try:
            fecha_inicio, fecha_fin = calcular_periodo(
                tipo_periodo, fecha_inicio, fecha_fin
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Generar reporte
        reporte_data = generar_reporte_membresias(fecha_inicio, fecha_fin)

        # Registrar en auditoría
        registrar_bitacora(
            request=request,
            accion="Generar Reporte de Membresías",
            descripcion=f"Reporte generado para período {fecha_inicio} - {fecha_fin}",
            modulo="Reportes",
            tipo_accion="read",
            nivel="info",
        )

        # Retornar según formato
        if formato == "pdf":
            pdf_buffer = generar_pdf_reporte(
                reporte_data, "membresias", reporte_data.get("periodo")
            )
            response = HttpResponse(
                pdf_buffer.getvalue(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="reporte_membresias_{fecha_inicio}_{fecha_fin}.pdf"'
            )
            return response

        return Response(reporte_data)

    @action(detail=False, methods=["get", "post"])
    def financiero(self, request):
        """
        Generar reporte financiero consolidado

        Query params o Body:
        - tipo_periodo: 'dia', 'semana', 'mes', 'anio', 'personalizado'
        - fecha_inicio: (requerido para personalizado)
        - fecha_fin: (requerido para personalizado)
        - formato: 'json' o 'pdf' (default: 'json')
        """
        serializer = ReporteFiltroSerializer(data=request.data or request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        tipo_periodo = data.get("tipo_periodo", "mes")
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        formato = data.get("formato", "json")

        try:
            fecha_inicio, fecha_fin = calcular_periodo(
                tipo_periodo, fecha_inicio, fecha_fin
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Generar reporte
        reporte_data = generar_reporte_financiero(fecha_inicio, fecha_fin)

        # Registrar en auditoría
        registrar_bitacora(
            request=request,
            accion="Generar Reporte Financiero",
            descripcion=f"Reporte generado para período {fecha_inicio} - {fecha_fin}",
            modulo="Reportes",
            tipo_accion="read",
            nivel="info",
        )

        # Retornar según formato
        if formato == "pdf":
            pdf_buffer = generar_pdf_reporte(
                reporte_data, "financiero", reporte_data.get("periodo")
            )
            response = HttpResponse(
                pdf_buffer.getvalue(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="reporte_financiero_{fecha_inicio}_{fecha_fin}.pdf"'
            )
            return response

        return Response(reporte_data)
