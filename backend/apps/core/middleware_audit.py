"""
Middleware de Auditoría Automática
Registra automáticamente todas las peticiones al sistema
"""
from apps.audit.models import HistorialActividad as Bitacora


class AuditMiddleware:
    """
    Middleware que registra automáticamente todas las peticiones HTTP
    """
    
    # Métodos HTTP que se registrarán
    AUDITABLE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Rutas que se deben ignorar (para evitar spam en bitácora)
    IGNORED_PATHS = [
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',
        '/admin/jsi18n/',
        '/static/',
        '/media/',
    ]
    
    # Mapeo de métodos HTTP a tipos de acción
    METHOD_TO_ACTION = {
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'update',
        'DELETE': 'delete',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Marcar que no se ha registrado manualmente
        request._audit_logged = False
        
        # Procesar la petición
        response = self.get_response(request)
        
        # Registrar en bitácora solo si NO se registró manualmente
        if self._should_audit(request, response) and not getattr(request, '_audit_logged', False):
            self._log_request(request, response)
        
        return response
    
    def _should_audit(self, request, response):
        """
        Determina si la petición debe ser registrada en bitácora
        """
        # Solo métodos modificadores
        if request.method not in self.AUDITABLE_METHODS:
            return False
        
        # Ignorar rutas específicas
        if any(request.path.startswith(path) for path in self.IGNORED_PATHS):
            return False
        
        # Solo respuestas exitosas (2xx)
        if not (200 <= response.status_code < 300):
            return False
        
        # Usuario debe estar autenticado (opcional, puedes quitarlo)
        if not request.user.is_authenticated:
            return False
        
        return True
    
    def _log_request(self, request, response):
        """
        Registra la petición en la bitácora
        """
        try:
            # Determinar tipo de acción basado en el método
            tipo_accion = self.METHOD_TO_ACTION.get(request.method, 'other')
            
            # Determinar acción basada en la ruta
            accion = self._get_action_from_path(request.path, request.method)
            
            # Descripción
            descripcion = f"{request.method} {request.path}"
            
            # Nivel
            nivel = 'warning' if request.method == 'DELETE' else 'info'
            
            # Datos adicionales
            datos_adicionales = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
            }
            
            # Si hay datos en el body (POST/PUT/PATCH)
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
                # No incluir contraseñas ni datos sensibles
                safe_data = {k: v for k, v in request.data.items() 
                            if k not in ['password', 'token', 'refresh']}
                datos_adicionales['request_data'] = safe_data
            
            # Registrar en bitácora
            Bitacora.log_activity(
                request=request,
                tipo_accion=tipo_accion,
                accion=accion,
                descripcion=descripcion,
                nivel=nivel,
                datos_adicionales=datos_adicionales
            )
        
        except Exception as e:
            # No queremos que un error en la bitácora rompa la aplicación
            print(f"Error al registrar en bitácora: {e}")
    
    def _get_action_from_path(self, path, method):
        """
        Genera una descripción legible de la acción basada en la ruta
        """
        # Remover /api/ del inicio
        clean_path = path.replace('/api/', '')
        
        # Mapeo de rutas a acciones
        actions = {
            'POST': {
                'auth/login': 'Inicio de Sesión',
                'auth/logout': 'Cierre de Sesión',
                'clients': 'Crear Cliente',
                'users/admins': 'Crear Administrador',
                'roles': 'Crear Rol',
                'permissions': 'Crear Permiso',
            },
            'PUT': {
                'clients': 'Actualizar Cliente',
                'roles': 'Actualizar Rol',
                'permissions': 'Actualizar Permiso',
            },
            'PATCH': {
                'clients': 'Actualizar Cliente (Parcial)',
                'roles': 'Actualizar Rol (Parcial)',
                'permissions': 'Actualizar Permiso (Parcial)',
            },
            'DELETE': {
                'clients': 'Eliminar Cliente',
                'roles': 'Eliminar Rol',
                'permissions': 'Eliminar Permiso',
            }
        }
        
        # Buscar coincidencia
        method_actions = actions.get(method, {})
        for key, value in method_actions.items():
            if key in clean_path:
                return value
        
        # Por defecto
        return f"{method} {clean_path}"
