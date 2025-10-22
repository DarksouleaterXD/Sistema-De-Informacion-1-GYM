# Rest framework
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import permissions, throttling, status
from rest_framework_simplejwt.tokens import RefreshToken

#Swagger docs
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.contrib.auth import get_user_model,authenticate

#Modelos
from apps.roles.models import Role, UserRole
from apps.audit.models import HistorialActividad as Bitacora
#Serializers
from .serializers import AdminCreateSerializer
from .serializers import LoginSerializer, LogoutSerializer

User = get_user_model()

class HasRoleSuperUser(permissions.BasePermission):
    """
    Permite solo al 'Superusuario (Dueño)' o a Django superuser.
    Asume que el nombre del rol es exactamente 'Superusuario' o 'Superusuario (Dueño)'.
    Ajusta la lista según tu semántica real.
    """
    allowed_role_names = {"Superusuario", "Superusuario (Dueño)"}

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True
        # UsuarioRol.related_name="roles" en tu modelo UsuarioRol
        return UserRole.objects.filter(
            usuario=user,
            rol__nombre__in=self.allowed_role_names
        ).exists()


@extend_schema(
    tags=["Usuarios"],
    request=AdminCreateSerializer,
    responses={201: AdminCreateSerializer},
    examples=[
        OpenApiExample(
            "Crear Administrador",
            value={
                "username": "admin2",
                "email": "admin2@demo.com",
                "password": "Admin1234!",
                "first_name": "Ana",
                "last_name": "Pérez"
            },
            request_only=True
        )
    ],
)
class CreateAdminView(APIView):
    permission_classes = [HasRoleSuperUser]

    def post(self, request):
        serializer = AdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1) Crear usuario
        user = serializer.save()

        # 2) Asignar rol 'Administrador' (lo crea si no existe)
        admin_role, _ = Role.objects.get_or_create(nombre="Administrador")
        UserRole.objects.get_or_create(usuario=user, rol=admin_role)

        # 3) Registrar en bitácora
        ip = self._ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")
        Bitacora.log_activity(
            usuario=request.user,
            tipo_accion="create_user",
            accion="Crear Administrador",
            descripcion=f"Se creó el administrador {user.username} ({user.email})",
            nivel="info",
            ip_address=ip,
            user_agent=ua,
            datos_adicionales={"nuevo_usuario_id": user.id, "rol_asignado": "Administrador"},
        )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "rol_asignado": "Administrador",
            },
            status=201,
        )

    def _ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR", "")
# --- /CU1 --------------------------------------------------------------------

class LoginRateThrottle(throttling.AnonRateThrottle):
    rate = "10/min"  # anti fuerza-bruta


@extend_schema(
    tags=["Autenticación"],
    request=LoginSerializer,
    examples=[OpenApiExample(
        "Ejemplo login con username",
        request_only=True,
        value={"username":"admin", "password":"Admin1234!"}
    )]
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        if not s.is_valid():
            self._audit(request, tipo="login", ok=False, detalle=s.errors,username=request.data.get("username",""))
            return Response({"detail": "Username y contraseña son obligatorios."}, status=400)

        username = s.validated_data["username"]
        password = s.validated_data["password"]

        # Importante: si USERNAME_FIELD != 'email', habilita el EmailBackend (ver abajo, opcional)
        user = authenticate(request=request, username=username, password=password)
        if not user or not user.is_active:
            self._audit(request, tipo="login", ok=False, username=username, detalle="Credenciales inválidas o usuario inactivo")
            return Response({"detail": "Credenciales inválidas."}, status=400)

        refresh = RefreshToken.for_user(user)
        self._audit(request, tipo="login", ok=True, user=user, detalle="Inicio de sesión correcto")

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": getattr(user, "email", ""),
                "first_name": getattr(user, "first_name", ""),
                "last_name": getattr(user, "last_name", ""),
            }
        }, status=200)

    def _audit(self, request, tipo, ok, user=None, email="", detalle=""):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = ip.split(",")[0] if ip else request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        Bitacora.log_activity(
            usuario=user if ok else None,
            tipo_accion="login" if ok else "error",
            accion="Inicio de Sesión" if ok else "Fallo de Inicio de Sesión",
            descripcion=detalle,
            nivel="info" if ok else "warning",
            ip_address=ip,
            user_agent=ua,
            datos_adicionales={"email": email or (user.email if user else "")},
        )


@extend_schema(tags=["Autenticación"], request=LogoutSerializer, responses={205: None})
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = LogoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()

        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = ip.split(",")[0] if ip else request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        Bitacora.log_activity(
            usuario=request.user,
            tipo_accion="logout",
            accion="Cierre de Sesión",
            descripcion="Logout con blacklist de refresh",
            nivel="info",
            ip_address=ip,
            user_agent=ua,
        )
        return Response(status=205)
# --- /CU2 --------------------------------------------------------------------