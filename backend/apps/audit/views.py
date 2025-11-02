from django.db.models import Q
from django.utils.dateparse import parse_datetime, parse_date
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.audit.models import HistorialActividad as Bitacora
from apps.audit.serializers import BitacoraSerializer
from apps.roles.models import UserRole
from apps.core.permissions import HasPermission, PermissionCodes


# --- Paginación por defecto (20 por página) ---
class AuditPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    tags=["Bitácora"],
    parameters=[
        OpenApiParameter("user_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filtra por ID de usuario"),
        OpenApiParameter("username", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filtra por username de usuario"),
        OpenApiParameter("email", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filtra por email de usuario"),
        OpenApiParameter("tipo_accion", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Exacto. Ej: login, logout, create_role..."),
        OpenApiParameter("nivel", OpenApiTypes.STR, OpenApiParameter.QUERY, description="info | warning | error | critical"),
        OpenApiParameter("ip", OpenApiTypes.STR, OpenApiParameter.QUERY, description="IP exacta o parte"),
        OpenApiParameter("date_from", OpenApiTypes.STR, OpenApiParameter.QUERY, description="ISO date/datetime (incluye)"),
        OpenApiParameter("date_to", OpenApiTypes.STR, OpenApiParameter.QUERY, description="ISO date/datetime (incluye)"),
        OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Búsqueda en acción/descripcion/user_agent/datos_adicionales"),
        OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY, description="campo para ordenar (p.ej. -fecha_hora)"),
    ],
)
class AuditLogListView(ListAPIView):
    """
    GET /api/audit/logs/?q=&tipo_accion=&nivel=&user_id=&username=&email=&ip=&date_from=&date_to=&ordering=
    """
    serializer_class = BitacoraSerializer
    pagination_class = AuditPagination
    permission_classes = [HasPermission]
    required_permission = PermissionCodes.AUDIT_VIEW

    def get_queryset(self):
        qs = Bitacora.objects.select_related("usuario").all()

        user_id = self.request.query_params.get("user_id")
        username = self.request.query_params.get("username")
        email = self.request.query_params.get("email")
        tipo = self.request.query_params.get("tipo_accion")
        nivel = self.request.query_params.get("nivel")
        ip = self.request.query_params.get("ip")
        q = self.request.query_params.get("q")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        ordering = self.request.query_params.get("ordering") or "-fecha_hora"

        if user_id:
            qs = qs.filter(usuario_id=user_id)
        if username:
            qs = qs.filter(usuario__username__icontains=username)
        if email:
            qs = qs.filter(usuario__email__icontains=email)
        if tipo:
            qs = qs.filter(tipo_accion=tipo)
        if nivel:
            qs = qs.filter(nivel=nivel)
        if ip:
            qs = qs.filter(ip_address__icontains=ip)
        if q:
            qs = qs.filter(
                Q(accion__icontains=q)
                | Q(descripcion__icontains=q)
                | Q(user_agent__icontains=q)
                | Q(datos_adicionales__icontains=q)
            )

        # fechas (acepta date o datetime)
        if date_from:
            dt = parse_datetime(date_from) or parse_date(date_from)
            if dt:
                qs = qs.filter(fecha_hora__gte=dt)
        if date_to:
            dt = parse_datetime(date_to) or parse_date(date_to)
            if dt:
                # <= date_to 23:59:59 si es solo fecha
                if hasattr(dt, "year") and not hasattr(dt, "hour"):
                    from datetime import datetime, time
                    dt = datetime.combine(dt, time.max)
                qs = qs.filter(fecha_hora__lte=dt)

        # orden
        allowed_order = {"fecha_hora", "-fecha_hora", "nivel", "-nivel", "tipo_accion", "-tipo_accion", "id", "-id"}
        if ordering in allowed_order:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-fecha_hora")

        return qs


@extend_schema(tags=["Bitácora"])
class AuditLogDetailView(RetrieveAPIView):
    """
    GET /api/audit/logs/<id>/
    """
    queryset = Bitacora.objects.select_related("usuario").all()
    serializer_class = BitacoraSerializer
    permission_classes = [HasPermission]
    required_permission = PermissionCodes.AUDIT_VIEW_DETAILS



