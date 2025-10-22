from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from apps.roles.models import Role, Permiso, UserRole, RolPermiso
from apps.roles.serializers import RolSerializer, PermisoSerializer, RolePermissionSerializer, RolePermissionSetSerializer
from apps.audit.models import HistorialActividad as Bitacora

User = get_user_model()
# ----- Permiso: solo Superusuario (Dueño) o superuser de Django -----

class HasRoleSuperUser(permissions.BasePermission):
    allowed_role_names = {"Superusuario", "Superusuario (Dueño)"}

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if getattr(u, "is_superuser", False):
            return True
        # UserRole.related_name="roles" en tu modelo; filtra por nombre del rol
        return UserRole.objects.filter(usuario=u, rol__nombre__in=self.allowed_role_names).exists()


# ----- Utils para auditoría -----
def _ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR", "")

def _ua(request):
    return request.META.get("HTTP_USER_AGENT", "")


# ================== CRUD Roles ==================

@extend_schema(
    tags=["Roles"],
    responses={200: RolSerializer(many=True)},
)
class RoleListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/roles/        -> Lista roles
    POST /api/roles/        -> Crea rol
    """
    queryset = Role.objects.all().order_by("-created_at")
    serializer_class = RolSerializer
    permission_classes = [HasRoleSuperUser]

    @extend_schema(
        tags=["Roles"],
        request=RolSerializer,
        responses={201: RolSerializer},
        examples=[OpenApiExample("Crear rol", request_only=True, value={
            "nombre": "Administrador",
            "descripcion": "Puede gestionar usuarios y membresías",
            "activo": True
        })],
    )
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if resp.status_code == 201:
            Bitacora.log_activity(
                usuario=request.user,
                tipo_accion="create_role",
                accion="Crear Rol",
                descripcion=f"Rol creado: {resp.data.get('nombre')}",
                nivel="info",
                ip_address=_ip(request),
                user_agent=_ua(request),
                datos_adicionales={"rol_id": resp.data.get("id")},
            )
        return resp


@extend_schema(tags=["Roles"], responses={200: RolSerializer})
class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/roles/{id}/   -> Detalle rol
    PUT    /api/roles/{id}/   -> Actualiza rol (reemplaza)
    PATCH  /api/roles/{id}/   -> Actualiza parcial
    DELETE /api/roles/{id}/   -> Elimina rol
    """
    queryset = Role.objects.all()
    serializer_class = RolSerializer
    permission_classes = [HasRoleSuperUser]

    @extend_schema(
        tags=["Roles"],
        request=RolSerializer,
        responses={200: RolSerializer},
        examples=[OpenApiExample("Actualizar rol", request_only=True, value={
            "nombre": "Administrador",
            "descripcion": "Admin del sistema (actualizado)",
            "activo": True
        })],
    )
    def put(self, request, *args, **kwargs):
        resp = super().put(request, *args, **kwargs)
        if resp.status_code == 200:
            Bitacora.log_activity(
                usuario=request.user,
                tipo_accion="update_role",
                accion="Actualizar Rol",
                descripcion=f"Rol actualizado: {resp.data.get('nombre')}",
                nivel="info",
                ip_address=_ip(request),
                user_agent=_ua(request),
                datos_adicionales={"rol_id": resp.data.get("id")},
            )
        return resp

    def patch(self, request, *args, **kwargs):
        resp = super().patch(request, *args, **kwargs)
        if resp.status_code == 200:
            Bitacora.log_activity(
                usuario=request.user,
                tipo_accion="update_role",
                accion="Actualizar Rol (parcial)",
                descripcion=f"Rol actualizado: {resp.data.get('nombre')}",
                nivel="info",
                ip_address=_ip(request),
                user_agent=_ua(request),
                datos_adicionales={"rol_id": resp.data.get("id")},
            )
        return resp

    @extend_schema(tags=["Roles"], responses={204: OpenApiResponse(description="Eliminado")})
    def delete(self, request, *args, **kwargs):
        rol = self.get_object()
        rol_id, rol_nombre = rol.id, rol.nombre
        resp = super().delete(request, *args, **kwargs)
        if resp.status_code == 204:
            Bitacora.log_activity(
                usuario=request.user,
                tipo_accion="delete_role",
                accion="Eliminar Rol",
                descripcion=f"Rol eliminado: {rol_nombre}",
                nivel="info",
                ip_address=_ip(request),
                user_agent=_ua(request),
                datos_adicionales={"rol_id": rol_id},
            )
        return resp


# ================== Asignar / Remover Rol a Usuario ==================

class RoleAssignSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

class RoleRemoveSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()


@extend_schema(
    tags=["Roles"],
    request=RoleAssignSerializer,
    responses={204: OpenApiResponse(description="Asignado")},
    examples=[OpenApiExample("Asignar rol", request_only=True, value={"user_id": 12, "role_id": 3})],
)
class RoleAssignView(APIView):
    """
    POST /api/roles/assign/  {user_id, role_id}
    """
    permission_classes = [HasRoleSuperUser]

    def post(self, request):
        s = RoleAssignSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        user = User.objects.filter(id=s.validated_data["user_id"]).first()
        if not user:
            return Response({"detail": "Usuario no encontrado."}, status=404)

        rol = Role.objects.filter(id=s.validated_data["role_id"]).first()
        if not rol:
            return Response({"detail": "Rol no encontrado."}, status=404)

        UserRole.objects.get_or_create(usuario=user, rol=rol)

        Bitacora.log_activity(
            usuario=request.user,
            tipo_accion="assign_role",
            accion="Asignar Rol",
            descripcion=f"Asignado {rol.nombre} a {user.username}",
            nivel="info",
            ip_address=_ip(request),
            user_agent=_ua(request),
            datos_adicionales={"user_id": user.id, "role_id": rol.id},
        )
        return Response(status=204)


@extend_schema(
    tags=["Roles"],
    request=RoleRemoveSerializer,
    responses={204: OpenApiResponse(description="Removido")},
    examples=[OpenApiExample("Remover rol", request_only=True, value={"user_id": 12, "role_id": 3})],
)
class RoleRemoveView(APIView):
    """
    POST /api/roles/remove/  {user_id, role_id}
    """
    permission_classes = [HasRoleSuperUser]

    def post(self, request):
        s = RoleRemoveSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        qs = UserRole.objects.filter(
            usuario_id=s.validated_data["user_id"],
            rol_id=s.validated_data["role_id"]
        )
        if not qs.exists():
            return Response({"detail": "La asignación usuario-rol no existe."}, status=404)

        # para bitácora, guarda datos antes de borrar
        ur = qs.select_related("usuario", "rol").first()
        user, rol = ur.usuario, ur.rol

        qs.delete()

        Bitacora.log_activity(
            usuario=request.user,
            tipo_accion="remove_role",
            accion="Remover Rol",
            descripcion=f"Removido {rol.nombre} de {user.username}",
            nivel="info",
            ip_address=_ip(request),
            user_agent=_ua(request),
            datos_adicionales={"user_id": user.id, "role_id": rol.id},
        )
        return Response(status=204)
# ---------- Permiso reutilizable SOLO-SUPERUSUARIO ----------
class HasRoleSuperUser(permissions.BasePermission):
    """
    Permite solo al 'Superusuario (Dueño)' o a Django superuser.
    Ajusta allowed_role_names si usas otro label.
    """
    allowed_role_names = {"Superusuario", "Superusuario (Dueño)"}

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if getattr(u, "is_superuser", False):
            return True
        # Verifica si el usuario tiene uno de los roles permitidos
        return UserRole.objects.filter(
            usuario=u, rol__nombre__in=self.allowed_role_names
        ).exists()

# ---------- helpers ----------
def _ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR", "")
def _ua(request): return request.META.get("HTTP_USER_AGENT", "")

# ================== CRUD Permisos ==================
@extend_schema(tags=["Permisos"], responses={200: PermisoSerializer(many=True)})
class PermissionListCreateView(generics.ListCreateAPIView):
    queryset = Permiso.objects.all().order_by("nombre")
    serializer_class = PermisoSerializer
    permission_classes = [HasRoleSuperUser]

    @extend_schema(
        tags=["Permisos"], request=PermisoSerializer, responses={201: PermisoSerializer},
        examples=[OpenApiExample("Crear permiso", request_only=True,
                                 value={"nombre": "clients.view", "descripcion": "Ver clientes"})],
    )
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if resp.status_code == 201:
            Bitacora.log_activity(
                usuario=request.user, tipo_accion="create_permission", accion="Crear Permiso",
                descripcion=f"Permiso creado: {resp.data.get('nombre')}",
                nivel="info", ip_address=_ip(request), user_agent=_ua(request),
                datos_adicionales={"permiso_id": resp.data.get("id")},
            )
        return resp

@extend_schema(tags=["Permisos"], responses={200: PermisoSerializer})
class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [HasRoleSuperUser]

    @extend_schema(tags=["Permisos"], request=PermisoSerializer, responses={200: PermisoSerializer})
    def put(self, request, *args, **kwargs):
        resp = super().put(request, *args, **kwargs)
        if resp.status_code == 200:
            Bitacora.log_activity(
                usuario=request.user, tipo_accion="update_permission", accion="Actualizar Permiso",
                descripcion=f"Permiso actualizado: {resp.data.get('nombre')}",
                nivel="info", ip_address=_ip(request), user_agent=_ua(request),
                datos_adicionales={"permiso_id": resp.data.get("id")},
            )
        return resp

    def patch(self, request, *args, **kwargs):
        resp = super().patch(request, *args, **kwargs)
        if resp.status_code == 200:
            Bitacora.log_activity(
                usuario=request.user, tipo_accion="update_permission", accion="Actualizar Permiso (parcial)",
                descripcion=f"Permiso actualizado: {resp.data.get('nombre')}",
                nivel="info", ip_address=_ip(request), user_agent=_ua(request),
                datos_adicionales={"permiso_id": resp.data.get("id")},
            )
        return resp

    @extend_schema(tags=["Permisos"], responses={204: OpenApiResponse(description="Eliminado")})
    def delete(self, request, *args, **kwargs):
        permiso = self.get_object()
        pid, pname = permiso.id, permiso.nombre
        resp = super().delete(request, *args, **kwargs)
        if resp.status_code == 204:
            Bitacora.log_activity(
                usuario=request.user, tipo_accion="delete_permission", accion="Eliminar Permiso",
                descripcion=f"Permiso eliminado: {pname}",
                nivel="info", ip_address=_ip(request), user_agent=_ua(request),
                datos_adicionales={"permiso_id": pid},
            )
        return resp

# ================== Rol ↔ Permisos ==================
@extend_schema(
    tags=["Permisos"], request=RolePermissionSerializer,
    responses={204: OpenApiResponse(description="Asignado")},
    examples=[OpenApiExample("Asignar permiso a rol", request_only=True, value={"permiso_id": 2})],
)
class RolePermissionAssignView(APIView):
    permission_classes = [HasRoleSuperUser]

    def post(self, request, role_id: int):
        s = RolePermissionSerializer(data=request.data); s.is_valid(raise_exception=True)
        rol = Role.objects.filter(id=role_id).first()
        if not rol: return Response({"detail": "Rol no encontrado."}, status=404)
        perm = Permiso.objects.filter(id=s.validated_data["permiso_id"]).first()
        if not perm: return Response({"detail": "Permiso no encontrado."}, status=404)

        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        Bitacora.log_activity(
            usuario=request.user, tipo_accion="assign_role", accion="Asignar Permiso a Rol",
            descripcion=f"{perm.nombre} -> {rol.nombre}",
            nivel="info", ip_address=_ip(request), user_agent=_ua(request),
            datos_adicionales={"role_id": rol.id, "permiso_id": perm.id},
        )
        return Response(status=204)

@extend_schema(
    tags=["Permisos"], request=RolePermissionSerializer,
    responses={204: OpenApiResponse(description="Removido")},
    examples=[OpenApiExample("Remover permiso de rol", request_only=True, value={"permiso_id": 2})],
)
class RolePermissionRemoveView(APIView):
    permission_classes = [HasRoleSuperUser]

    def post(self, request, role_id: int):
        s = RolePermissionSerializer(data=request.data); s.is_valid(raise_exception=True)
        deleted, _ = RolPermiso.objects.filter(
            rol_id=role_id, permiso_id=s.validated_data["permiso_id"]
        ).delete()
        if not deleted:
            return Response({"detail": "Relación rol-permiso no existe."}, status=404)

        Bitacora.log_activity(
            usuario=request.user, tipo_accion="remove_role", accion="Remover Permiso de Rol",
            descripcion=f"permiso_id={s.validated_data['permiso_id']} de rol_id={role_id}",
            nivel="info", ip_address=_ip(request), user_agent=_ua(request),
            datos_adicionales={"role_id": role_id, "permiso_id": s.validated_data["permiso_id"]},
        )
        return Response(status=204)

@extend_schema(
    tags=["Permisos"], request=RolePermissionSetSerializer,
    responses={204: OpenApiResponse(description="Set actualizado")},
    examples=[OpenApiExample("Reemplazar set", request_only=True, value={"permisos": [1, 2, 5]})],
)
class RolePermissionSetView(APIView):
    permission_classes = [HasRoleSuperUser]

    def put(self, request, role_id: int):
        s = RolePermissionSetSerializer(data=request.data); s.is_valid(raise_exception=True)
        rol = Role.objects.filter(id=role_id).first()
        if not rol: return Response({"detail":"Rol no encontrado."}, status=404)

        nuevos = set(s.validated_data["permisos"])
        actuales = set(RolPermiso.objects.filter(rol=rol).values_list("permiso_id", flat=True))

        # eliminar los que sobran
        RolPermiso.objects.filter(rol=rol, permiso_id__in=(actuales - nuevos)).delete()
        # agregar los nuevos
        for pid in (nuevos - actuales):
            perm = Permiso.objects.filter(id=pid).first()
            if perm:
                RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        Bitacora.log_activity(
            usuario=request.user, tipo_accion="update_role", accion="Actualizar Set de Permisos de Rol",
            descripcion=f"rol={rol.nombre} -> {sorted(list(nuevos))}",
            nivel="info", ip_address=_ip(request), user_agent=_ua(request),
            datos_adicionales={"role_id": rol.id, "permisos": sorted(list(nuevos))},
        )
        return Response(status=204)
