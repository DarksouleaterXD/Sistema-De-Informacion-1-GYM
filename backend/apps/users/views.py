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
from .serializers import UserSerializer

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
            self._audit(request, tipo="login", ok=False, detalle=str(s.errors))
            return Response({"detail": "Email y contraseña son obligatorios."}, status=400)

        email = s.validated_data["email"]
        password = s.validated_data["password"]

        # Autenticar usando email (el modelo User usa email como USERNAME_FIELD)
        user = authenticate(request=request, username=email, password=password)
        if not user or not user.is_active:
            self._audit(request, tipo="login", ok=False, email=email, detalle="Credenciales inválidas o usuario inactivo")
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
        Bitacora.log_activity(
            request=request,
            usuario=user if ok else None,
            tipo_accion="login" if ok else "error",
            accion="Inicio de Sesión" if ok else "Fallo de Inicio de Sesión",
            descripcion=detalle,
            nivel="info" if ok else "warning",
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


@extend_schema(
    tags=["Usuarios"],
    responses={200: UserSerializer}
)
class CurrentUserView(APIView):
    """
    Obtiene la información del usuario autenticado actual.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=200)
# --- /Password Reset ---------------------------------------------------------


# --- CRUD Usuarios -----------------------------------------------------------
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .serializers import UserListSerializer, UserCreateSerializer, UserUpdateSerializer


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    tags=["Usuarios - CRUD"],
    responses={200: UserListSerializer(many=True)}
)
class UserListCreateView(APIView):
    """
    GET: Lista todos los usuarios con paginación y búsqueda
    POST: Crea un nuevo usuario
    """
    permission_classes = [permissions.IsAuthenticated, HasRoleSuperUser]
    
    def get(self, request):
        """Listar usuarios con búsqueda y filtros"""
        search = request.query_params.get('search', '').strip()
        is_active_filter = request.query_params.get('is_active', '').strip()
        
        queryset = User.objects.all().order_by('-date_joined')
        
        # Aplicar búsqueda por username, email o nombre
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filtrar por estado activo
        if is_active_filter:
            is_active = is_active_filter.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        # Paginación
        paginator = UserPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=UserCreateSerializer,
        responses={201: UserListSerializer}
    )
    def post(self, request):
        """Crear un nuevo usuario"""
        serializer = UserCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            accion='crear_usuario',
            descripcion=f'Usuario {user.username} creado por {request.user.username}',
            modulo='users',
            nivel='info'
        )
        
        # Retornar con el serializer completo
        response_serializer = UserListSerializer(user)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Usuarios - CRUD"],
    responses={200: UserListSerializer}
)
class UserDetailView(APIView):
    """
    GET: Obtiene los detalles de un usuario
    PUT: Actualiza un usuario
    PATCH: Actualiza parcialmente un usuario
    DELETE: Elimina un usuario
    """
    permission_classes = [permissions.IsAuthenticated, HasRoleSuperUser]
    
    def get_object(self, pk):
        """Helper para obtener el usuario"""
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtener detalle de un usuario"""
        user = self.get_object(pk)
        
        if not user:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserListSerializer(user)
        return Response(serializer.data)
    
    @extend_schema(request=UserUpdateSerializer, responses={200: UserListSerializer})
    def put(self, request, pk):
        """Actualizar completamente un usuario"""
        user = self.get_object(pk)
        
        if not user:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # No permitir que el usuario se modifique a sí mismo
        if user.id == request.user.id:
            return Response(
                {"detail": "No puedes modificarte a ti mismo. Usa tu perfil."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserUpdateSerializer(user, data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_user = serializer.save()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            accion='actualizar_usuario',
            descripcion=f'Usuario {user.username} actualizado por {request.user.username}',
            modulo='users',
            nivel='info'
        )
        
        return Response(UserListSerializer(updated_user).data)
    
    @extend_schema(request=UserUpdateSerializer, responses={200: UserListSerializer})
    def patch(self, request, pk):
        """Actualizar parcialmente un usuario"""
        user = self.get_object(pk)
        
        if not user:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # No permitir que el usuario se modifique a sí mismo
        if user.id == request.user.id:
            return Response(
                {"detail": "No puedes modificarte a ti mismo. Usa tu perfil."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_user = serializer.save()
        
        # Registrar en bitácora
        Bitacora.log_activity(
            request=request,
            accion='actualizar_usuario',
            descripcion=f'Usuario {user.username} actualizado parcialmente por {request.user.username}',
            modulo='users',
            nivel='info'
        )
        
        return Response(UserListSerializer(updated_user).data)
    
    def delete(self, request, pk):
        """Eliminar un usuario"""
        user = self.get_object(pk)
        
        if not user:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # No permitir eliminarse a sí mismo
        if user.id == request.user.id:
            return Response(
                {"detail": "No puedes eliminarte a ti mismo."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # No permitir eliminar superusuarios
        if user.is_superuser:
            return Response(
                {"detail": "No se puede eliminar un superusuario."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar datos antes de eliminar
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip()
        }
        
        # Registrar en bitácora antes de eliminar
        Bitacora.log_activity(
            request=request,
            accion='eliminar_usuario',
            descripcion=f'Usuario {user.username} eliminado por {request.user.username}',
            modulo='users',
            nivel='warning'
        )
        
        user.delete()
        
        return Response(
            {"detail": "Usuario eliminado correctamente.", "data": user_data},
            status=status.HTTP_200_OK
        )