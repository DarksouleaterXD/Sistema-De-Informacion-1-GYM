from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.users.views import CreateAdminView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetRequestView
from apps.roles.views import PermissionDetailView, PermissionListCreateView, RoleAssignView, RoleDetailView, RoleListCreateView, RolePermissionAssignView, RolePermissionRemoveView, RolePermissionSetView, RoleRemoveView
from apps.audit.views import AuditLogDetailView, AuditLogListView

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
    # Permisos y Roles-Permisos
    path("api/permissions/", PermissionListCreateView.as_view(), name="permission-list-create"),
    path("api/permissions/<int:pk>/", PermissionDetailView.as_view(), name="permission-detail"),
    path("api/roles/<int:role_id>/permissions/assign/", RolePermissionAssignView.as_view(), name="role-permission-assign"),
    path("api/roles/<int:role_id>/permissions/remove/", RolePermissionRemoveView.as_view(), name="role-permission-remove"),
    path("api/roles/<int:role_id>/permissions/", RolePermissionSetView.as_view(), name="role-permission-set"),
    #Bitacora
     # ...
    path("api/audit/logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("api/audit/logs/<int:pk>/", AuditLogDetailView.as_view(), name="audit-log-detail"),
    
]