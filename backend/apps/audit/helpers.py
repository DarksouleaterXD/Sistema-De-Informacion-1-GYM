"""
Helper functions para la bitácora del sistema
Simplifica el registro de actividades
"""
from apps.audit.models import HistorialActividad


def registrar_bitacora(request, usuario=None, accion="", descripcion="", modulo="", 
                       tipo_accion="other", nivel="info", datos_adicionales=None):
    """
    Función helper simplificada para registrar en la bitácora
    
    Args:
        request: HttpRequest object
        usuario: Usuario que realizó la acción (opcional, usa request.user si es None)
        accion: Descripción corta de la acción
        descripcion: Descripción detallada
        modulo: Módulo del sistema (PERFIL, CLIENTES, ROLES, etc.)
        tipo_accion: Tipo de acción (create, update, delete, etc.)
        nivel: Nivel de severidad (info, warning, error, critical)
        datos_adicionales: Dict con datos extra (opcional)
    
    Example:
        registrar_bitacora(
            request=request,
            usuario=request.user,
            accion="Actualización Perfil",
            descripcion=f"Perfil actualizado por {request.user.username}",
            modulo="PERFIL"
        )
    """
    # Si no se especifica usuario, usar el del request
    if usuario is None and hasattr(request, 'user') and request.user.is_authenticated:
        usuario = request.user
    
    # Agregar módulo a los datos adicionales
    if datos_adicionales is None:
        datos_adicionales = {}
    
    if modulo:
        datos_adicionales['modulo'] = modulo
    
    # Marcar que se registró manualmente (evita duplicados con middleware)
    if hasattr(request, '_audit_logged'):
        request._audit_logged = True
    
    # Registrar usando el método del modelo
    return HistorialActividad.log_activity(
        request=request,
        tipo_accion=tipo_accion,
        accion=accion,
        descripcion=descripcion,
        nivel=nivel,
        usuario=usuario,
        datos_adicionales=datos_adicionales
    )


def registrar_creacion(request, objeto, modulo=""):
    """
    Helper específico para registrar creaciones
    
    Example:
        cliente = serializer.save()
        registrar_creacion(request, cliente, modulo="CLIENTES")
    """
    nombre_clase = objeto.__class__.__name__
    
    return registrar_bitacora(
        request=request,
        accion=f"Crear {nombre_clase}",
        descripcion=f"Se creó {nombre_clase}: {str(objeto)}",
        modulo=modulo,
        tipo_accion="create",
        nivel="info",
        datos_adicionales={
            "objeto_id": objeto.pk,
            "objeto_tipo": nombre_clase
        }
    )


def registrar_actualizacion(request, objeto, modulo="", datos_anteriores=None):
    """
    Helper específico para registrar actualizaciones
    
    Example:
        datos_anteriores = {"nombre": cliente.nombre, "email": cliente.email}
        cliente = serializer.save()
        registrar_actualizacion(request, cliente, modulo="CLIENTES", datos_anteriores=datos_anteriores)
    """
    nombre_clase = objeto.__class__.__name__
    
    datos_extra = {
        "objeto_id": objeto.pk,
        "objeto_tipo": nombre_clase
    }
    
    if datos_anteriores:
        datos_extra["datos_anteriores"] = datos_anteriores
    
    return registrar_bitacora(
        request=request,
        accion=f"Actualizar {nombre_clase}",
        descripcion=f"Se actualizó {nombre_clase}: {str(objeto)}",
        modulo=modulo,
        tipo_accion="update",
        nivel="info",
        datos_adicionales=datos_extra
    )


def registrar_eliminacion(request, objeto, modulo=""):
    """
    Helper específico para registrar eliminaciones
    
    Example:
        datos_cliente = {"nombre": cliente.nombre_completo, "ci": cliente.ci}
        cliente.delete()
        registrar_eliminacion(request, datos_cliente, modulo="CLIENTES")
    """
    if isinstance(objeto, dict):
        # Si es un dict, ya se eliminó el objeto
        nombre_clase = objeto.get('tipo', 'Objeto')
        objeto_str = str(objeto)
        objeto_id = objeto.get('id', None)
    else:
        # Si es un objeto, aún no se eliminó
        nombre_clase = objeto.__class__.__name__
        objeto_str = str(objeto)
        objeto_id = objeto.pk
    
    return registrar_bitacora(
        request=request,
        accion=f"Eliminar {nombre_clase}",
        descripcion=f"Se eliminó {nombre_clase}: {objeto_str}",
        modulo=modulo,
        tipo_accion="delete",
        nivel="warning",  # Eliminaciones siempre son warning
        datos_adicionales={
            "objeto_id": objeto_id,
            "objeto_tipo": nombre_clase,
            "datos_eliminados": objeto if isinstance(objeto, dict) else None
        }
    )


def registrar_login(request, usuario, exitoso=True):
    """
    Helper para registrar login
    
    Example:
        registrar_login(request, user, exitoso=True)
    """
    if exitoso:
        return registrar_bitacora(
            request=request,
            usuario=usuario,
            accion="Inicio de Sesión",
            descripcion=f"Usuario {usuario.username} inició sesión correctamente",
            modulo="AUTENTICACIÓN",
            tipo_accion="login",
            nivel="info"
        )
    else:
        return registrar_bitacora(
            request=request,
            usuario=None,
            accion="Fallo de Inicio de Sesión",
            descripcion=f"Intento fallido de inicio de sesión",
            modulo="AUTENTICACIÓN",
            tipo_accion="login_failed",
            nivel="warning"
        )


def registrar_logout(request, usuario):
    """
    Helper para registrar logout
    
    Example:
        registrar_logout(request, request.user)
    """
    return registrar_bitacora(
        request=request,
        usuario=usuario,
        accion="Cierre de Sesión",
        descripcion=f"Usuario {usuario.username} cerró sesión",
        modulo="AUTENTICACIÓN",
        tipo_accion="logout",
        nivel="info"
    )


def registrar_error(request, error, modulo=""):
    """
    Helper para registrar errores
    
    Example:
        try:
            risky_operation()
        except Exception as e:
            registrar_error(request, e, modulo="CLIENTES")
    """
    return registrar_bitacora(
        request=request,
        accion="Error del Sistema",
        descripcion=f"Error: {str(error)}",
        modulo=modulo,
        tipo_accion="error",
        nivel="error",
        datos_adicionales={
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
    )
