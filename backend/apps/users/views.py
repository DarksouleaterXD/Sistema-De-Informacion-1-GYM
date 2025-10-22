# Rest framework
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import permissions, throttling, status
from rest_framework_simplejwt.tokens import RefreshToken

# Swagger docs
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.contrib.auth import get_user_model, authenticate

# Modelos
from apps.roles.models import Role, UserRole
from apps.audit.models import HistorialActividad as Bitacora
from .models import PasswordResetToken

# Serializers
from .serializers import AdminCreateSerializer
from .serializers import LoginSerializer, LogoutSerializer
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

# Utilidades
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

# Permisos personalizados
from apps.roles.views import HasRoleSuperUser

User = get_user_model()

   


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


@extend_schema(
    tags=["Autenticación"],
    request=LogoutSerializer,
    responses={205: OpenApiResponse(description="Logout OK (refresh invalidado)")},
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = LogoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        self._audit(request, ok=True, accion="Cierre de sesión (refresh invalidado)")
        return Response(status=205)
    def _audit(self, request, ok: bool, accion: str, detalle: str = ""):
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
        
# --- /CU2 --------------------------------------------------------------------
# --- Contraseña Reset: request & confirm --------------------------------------
class ResetRateThrottle(throttling.AnonRateThrottle):
    # Ajusta el rate según tus políticas (evita enumeración/abuso)
    rate = "20/min"


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR", "")


def _user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")


def _build_reset_link(request, token):
    """
    Construye el link de reseteo que recibirá el usuario.
    Preferencia: FRONTEND_URL (Next.js) -> /reset-password?token=...
    Fallback: endpoint backend (confirm).
    """
    frontend = getattr(settings, "FRONTEND_URL", None)
    if frontend:
        sep = "&" if "?" in frontend else "?"
        return f"{frontend.rstrip('/')}/reset-password{sep}token={token}"
    # backend fallback
    base = request.build_absolute_uri("/api/auth/password/reset/confirm/")
    return f"{base}?token={token}"


class PasswordResetRequestView(APIView):
    """
    Recibe un email y, si existe un usuario, crea un token y envía correo.
    Respuesta siempre 200 (para no revelar si el email existe).
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ResetRateThrottle]

    @extend_schema(tags=["Autenticación"], request=PasswordResetRequestSerializer, responses={200: None})
    def post(self, request):
        s = PasswordResetRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"].strip().lower()

        user = User.objects.filter(email__iexact=email).first()
        ip, ua = _client_ip(request), _user_agent(request)

        if user:
            # invalidar tokens vigentes no usados (opcional)
            PasswordResetToken.objects.filter(user=user, used=False, expires_at__gt=timezone.now()).update(used=True)

            # crear token
            prt = PasswordResetToken.objects.create(
                user=user, ip_address=ip, user_agent=ua
            )
            reset_link = _build_reset_link(request, prt.token)

            # enviar correo
            subject = "Recuperación de contraseña"
            body = (
                f"Hola {user.username},\n\n"
                "Recibimos un pedido para restablecer tu contraseña.\n"
                f"Usa el siguiente enlace (válido por 1 hora):\n{reset_link}\n\n"
                "Si no realizaste este pedido, ignora este correo."
            )
            try:
                send_mail(subject, body, getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"), [email], fail_silently=True)
            except Exception:
                pass

            # bitácora
            Bitacora.log_activity(
                usuario=user,
                tipo_accion="other",
                accion="Password Reset Request",
                descripcion="Solicitud de recuperación de contraseña",
                nivel="info",
                ip_address=ip,
                user_agent=ua,
                datos_adicionales={"token": str(prt.token)},
            )

        # Respuesta genérica
        return Response({"detail": "Si el email está registrado, enviaremos instrucciones."}, status=200)


class PasswordResetConfirmView(APIView):
    """
    Recibe token + new_password, valida y cambia la contraseña.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ResetRateThrottle]

    @extend_schema(tags=["Autenticación"], request=PasswordResetConfirmSerializer, responses={200: None, 400: None})
    def post(self, request):
        s = PasswordResetConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        token = s.validated_data["token"]
        new_password = s.validated_data["new_password"]
        ip, ua = _client_ip(request), _user_agent(request)

        # buscar token válido
        try:
            prt = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Token inválido."}, status=400)

        if not prt.is_valid():
            return Response({"detail": "Token expirado o ya utilizado."}, status=400)

        user = prt.user
        user.set_password(new_password)
        user.save()

        # marcar token como usado
        prt.mark_as_used()

        # bitácora
        Bitacora.log_activity(
            usuario=user,
            tipo_accion="other",
            accion="Password Reset Confirm",
            descripcion="Contraseña restablecida correctamente",
            nivel="info",
            ip_address=ip,
            user_agent=ua,
        )

        # (opcional) notificar por email que se cambió la contraseña
        try:
            send_mail(
                "Tu contraseña fue cambiada",
                f"Hola {user.username}, tu contraseña se cambió en {timezone.now().strftime('%d/%m/%Y %H:%M')}.",
                getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({"detail": "Contraseña actualizada."}, status=200)
# --- /Password Reset ---------------------------------------------------------