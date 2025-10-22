from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.users.views import CreateAdminView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetRequestView
from apps.roles.views import RoleAssignView, RoleDetailView, RoleListCreateView, RoleRemoveView

urlpatterns = [
   
    # Schema de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # UI de Swagger
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # UI de Redoc
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # CU1: Registrar Administrador
    path("api/users/admins/", CreateAdminView.as_view(), name="users-create-admin"),
    # CU2: autenticación
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    #CU2: logout
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),   
    #Reset de contraseña
    path("api/auth/password/reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("api/auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    #CU4: Rutas de usuarios (CRUD)
     # Roles
    path("api/roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("api/roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path("api/roles/assign/", RoleAssignView.as_view(), name="role-assign"),
    path("api/roles/remove/", RoleRemoveView.as_view(), name="role-remove"),
]