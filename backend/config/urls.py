from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.users.views import CreateAdminView, CurrentUserView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetRequestView, UserListCreateView, UserDetailView
from apps.roles.views import PermissionDetailView, PermissionListCreateView, RoleAssignView, RoleDetailView, RoleListCreateView, RolePermissionAssignView, RolePermissionRemoveView, RolePermissionSetView, RoleRemoveView
from apps.audit.views import AuditLogDetailView, AuditLogListView
from apps.clients.views import ClientListCreateView, ClientDetailView
from apps.membresias.views import (
    MembresiaListCreateView, 
    MembresiaDetailView, 
    MembresiaStatsView, 
    ConsultarEstadoVigenciaView,
    PlanMembresiaListCreateView,
    PlanMembresiaDetailView
)
from apps.promociones.views import PromocionListCreateView, PromocionDetailView
from apps.disciplinas.views import DisciplinaListCreateView, DisciplinaDetailView
from apps.clases.views import (
    SalonListCreateView, SalonDetailView,
    ClaseListCreateView, ClaseDetailView,
    InscripcionClaseListCreateView, InscripcionClaseDetailView
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
   
    # Schema de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # UI de Swagger
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # UI de Redoc
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # CU1: Registrar Administrador
    path("api/users/admins/", CreateAdminView.as_view(), name="users-create-admin"),
    # Usuario actual
    path("api/users/me/", CurrentUserView.as_view(), name="current-user"),
    # CU2: autenticación
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    #CU2: logout
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),   
    #Reset de contraseña
    path("api/auth/password/reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("api/auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    
    # Usuarios CRUD
    path("api/users/", UserListCreateView.as_view(), name="user-list-create"),
    path("api/users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    
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
    
    # Clientes CRUD
    path("api/clients/", ClientListCreateView.as_view(), name="client-list-create"),
    path("api/clients/<int:pk>/", ClientDetailView.as_view(), name="client-detail"),
    
    # Membresías CRUD
    path("api/membresias/", MembresiaListCreateView.as_view(), name="membresia-list-create"),
    path("api/membresias/<int:pk>/", MembresiaDetailView.as_view(), name="membresia-detail"),
    path("api/membresias/stats/", MembresiaStatsView.as_view(), name="membresia-stats"),
    # CU17: Consultar Estado/Vigencia de Membresía
    path("api/membresias/consultar-estado/", ConsultarEstadoVigenciaView.as_view(), name="membresia-consultar-estado"),
    
    # Planes de Membresía CRUD
    path("api/planes-membresia/", PlanMembresiaListCreateView.as_view(), name="plan-membresia-list-create"),
    path("api/planes-membresia/<int:pk>/", PlanMembresiaDetailView.as_view(), name="plan-membresia-detail"),
    
    # Promociones CRUD
    path("api/promociones/", PromocionListCreateView.as_view(), name="promocion-list-create"),
    path("api/promociones/<int:pk>/", PromocionDetailView.as_view(), name="promocion-detail"),
    
    # CU19: Gestionar Disciplinas CRUD
    path("api/disciplinas/", DisciplinaListCreateView.as_view(), name="disciplina-list-create"),
    path("api/disciplinas/<int:pk>/", DisciplinaDetailView.as_view(), name="disciplina-detail"),
    
    # Gestionar Instructores CRUD
    path("api/instructores/", include('apps.instructores.urls')),
    
    # CU20: Programar Clase - Salones
    path("api/salones/", SalonListCreateView.as_view(), name="salon-list-create"),
    path("api/salones/<int:pk>/", SalonDetailView.as_view(), name="salon-detail"),
    
    # CU20: Programar Clase - Clases
    path("api/clases/", ClaseListCreateView.as_view(), name="clase-list-create"),
    path("api/clases/<int:pk>/", ClaseDetailView.as_view(), name="clase-detail"),
    
    # Inscripciones a Clases
    path("api/inscripciones-clase/", InscripcionClaseListCreateView.as_view(), name="inscripcion-clase-list-create"),
    path("api/inscripciones-clase/<int:pk>/", InscripcionClaseDetailView.as_view(), name="inscripcion-clase-detail"),
    
]