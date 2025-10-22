from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.users.views import CreateAdminView, LoginView, LogoutView

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
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),   
]