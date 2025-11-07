"""
Sistema de permisos granular para el gimnasio.
Define todos los permisos posibles en el sistema.
"""

from rest_framework.permissions import BasePermission
from typing import List


# ==========================================
# CONSTANTES DE PERMISOS
# ==========================================

class PermissionCodes:
    """
    Códigos de permisos del sistema.
    Formato: {MODULO}_{ACCION}
    """
    
    # ===== DASHBOARD =====
    DASHBOARD_VIEW = "dashboard.view"
    
    # ===== USUARIOS =====
    USER_VIEW = "user.view"
    USER_CREATE = "user.create"
    USER_EDIT = "user.edit"
    USER_DELETE = "user.delete"
    USER_VIEW_DETAILS = "user.view_details"
    
    # ===== ROLES Y PERMISOS =====
    ROLE_VIEW = "role.view"
    ROLE_CREATE = "role.create"
    ROLE_EDIT = "role.edit"
    ROLE_DELETE = "role.delete"
    ROLE_ASSIGN_PERMISSIONS = "role.assign_permissions"
    ROLE_ASSIGN_TO_USER = "role.assign_to_user"
    
    PERMISSION_VIEW = "permission.view"
    PERMISSION_CREATE = "permission.create"
    PERMISSION_EDIT = "permission.edit"
    PERMISSION_DELETE = "permission.delete"
    
    # ===== CLIENTES =====
    CLIENT_VIEW = "client.view"
    CLIENT_CREATE = "client.create"
    CLIENT_EDIT = "client.edit"
    CLIENT_DELETE = "client.delete"
    CLIENT_VIEW_DETAILS = "client.view_details"
    
    # ===== MEMBRESÍAS =====
    MEMBERSHIP_VIEW = "membership.view"
    MEMBERSHIP_CREATE = "membership.create"
    MEMBERSHIP_EDIT = "membership.edit"
    MEMBERSHIP_DELETE = "membership.delete"
    MEMBERSHIP_VIEW_STATS = "membership.view_stats"
    MEMBERSHIP_VIEW_DETAILS = "membership.view_details"
    
    # ===== PLANES DE MEMBRESÍA =====
    PLAN_VIEW = "plan.view"
    PLAN_CREATE = "plan.create"
    PLAN_EDIT = "plan.edit"
    PLAN_DELETE = "plan.delete"
    
    # ===== PROMOCIONES =====
    PROMOTION_VIEW = "promotion.view"
    PROMOTION_CREATE = "promotion.create"
    PROMOTION_EDIT = "promotion.edit"
    PROMOTION_DELETE = "promotion.delete"
    PROMOTION_VIEW_DETAILS = "promotion.view_details"
    
    # ===== INSCRIPCIONES =====
    ENROLLMENT_VIEW = "enrollment.view"
    ENROLLMENT_CREATE = "enrollment.create"
    ENROLLMENT_EDIT = "enrollment.edit"
    ENROLLMENT_DELETE = "enrollment.delete"
    
    # ===== DISCIPLINAS =====
    DISCIPLINE_VIEW = "discipline.view"
    DISCIPLINE_CREATE = "discipline.create"
    DISCIPLINE_EDIT = "discipline.edit"
    DISCIPLINE_DELETE = "discipline.delete"
    
    # ===== INSTRUCTORES =====
    INSTRUCTOR_VIEW = "instructor.view"
    INSTRUCTOR_CREATE = "instructor.create"
    INSTRUCTOR_EDIT = "instructor.edit"
    INSTRUCTOR_DELETE = "instructor.delete"
    INSTRUCTOR_VIEW_DETAILS = "instructor.view_details"
    
    # ===== SALONES =====
    SALON_VIEW = "salon.view"
    SALON_CREATE = "salon.create"
    SALON_EDIT = "salon.edit"
    SALON_DELETE = "salon.delete"
    
    # ===== CLASES =====
    CLASE_VIEW = "clase.view"
    CLASE_CREATE = "clase.create"
    CLASE_EDIT = "clase.edit"
    CLASE_DELETE = "clase.delete"
    
    # ===== INSCRIPCIONES A CLASES =====
    INSCRIPCION_CLASE_VIEW = "inscripcion_clase.view"
    INSCRIPCION_CLASE_CREATE = "inscripcion_clase.create"
    INSCRIPCION_CLASE_EDIT = "inscripcion_clase.edit"
    INSCRIPCION_CLASE_DELETE = "inscripcion_clase.delete"
    
    # ===== ASISTENCIAS A CLASES =====
    ASISTENCIA_VIEW = "asistencia.view"
    ASISTENCIA_CREATE = "asistencia.create"
    ASISTENCIA_EDIT = "asistencia.edit"
    ASISTENCIA_DELETE = "asistencia.delete"
    ASISTENCIA_VIEW_DETAILS = "asistencia.view_details"
    
    # ===== AUDITORÍA =====
    AUDIT_VIEW = "audit.view"
    AUDIT_VIEW_DETAILS = "audit.view_details"
    AUDIT_EXPORT = "audit.export"
    
    # ===== REPORTES =====
    REPORT_VIEW = "report.view"
    REPORT_GENERATE = "report.generate"
    REPORT_EXPORT = "report.export"


# ==========================================
# GRUPOS DE PERMISOS PREDEFINIDOS
# ==========================================

class PermissionGroups:
    """Grupos de permisos para facilitar la asignación."""
    
    # Admin tiene TODOS los permisos
    ADMIN = [
        getattr(PermissionCodes, attr) 
        for attr in dir(PermissionCodes) 
        if not attr.startswith('_')
    ]
    
    # Administrativo/Encargado - Permisos de gestión sin eliminar usuarios/roles
    ADMINISTRATIVO = [
        PermissionCodes.DASHBOARD_VIEW,
        
        # Usuarios (sin crear/eliminar)
        PermissionCodes.USER_VIEW,
        PermissionCodes.USER_EDIT,
        PermissionCodes.USER_VIEW_DETAILS,
        
        # Clientes completo
        PermissionCodes.CLIENT_VIEW,
        PermissionCodes.CLIENT_CREATE,
        PermissionCodes.CLIENT_EDIT,
        PermissionCodes.CLIENT_DELETE,
        PermissionCodes.CLIENT_VIEW_DETAILS,
        
        # Membresías completo
        PermissionCodes.MEMBERSHIP_VIEW,
        PermissionCodes.MEMBERSHIP_CREATE,
        PermissionCodes.MEMBERSHIP_EDIT,
        PermissionCodes.MEMBERSHIP_DELETE,
        PermissionCodes.MEMBERSHIP_VIEW_STATS,
        PermissionCodes.MEMBERSHIP_VIEW_DETAILS,
        
        # Planes solo ver
        PermissionCodes.PLAN_VIEW,
        
        # Promociones completo
        PermissionCodes.PROMOTION_VIEW,
        PermissionCodes.PROMOTION_CREATE,
        PermissionCodes.PROMOTION_EDIT,
        PermissionCodes.PROMOTION_DELETE,
        PermissionCodes.PROMOTION_VIEW_DETAILS,
        
        # Asistencias - Control completo
        PermissionCodes.ASISTENCIA_VIEW,
        PermissionCodes.ASISTENCIA_CREATE,
        PermissionCodes.ASISTENCIA_EDIT,
        PermissionCodes.ASISTENCIA_DELETE,
        PermissionCodes.ASISTENCIA_VIEW_DETAILS,
        
        # Auditoría solo ver
        PermissionCodes.AUDIT_VIEW,
        PermissionCodes.AUDIT_VIEW_DETAILS,
        
        # Reportes
        PermissionCodes.REPORT_VIEW,
        PermissionCodes.REPORT_GENERATE,
    ]
    
    # Instructor - Permisos según CU18
    # Puede: Ver clientes inscritos, Consultar vigencia membresías (solo lectura),
    # Programar sus clases, Inscribir clientes, Controlar asistencia
    INSTRUCTOR = [
        PermissionCodes.DASHBOARD_VIEW,
        
        # Clientes - Solo ver (CU8: solo inscritos en sus clases)
        PermissionCodes.CLIENT_VIEW,
        PermissionCodes.CLIENT_VIEW_DETAILS,
        
        # Membresías - Solo consultar estado/vigencia (CU17: para pasar lista)
        PermissionCodes.MEMBERSHIP_VIEW,
        PermissionCodes.MEMBERSHIP_VIEW_DETAILS,
        
        # Disciplinas - Ver disciplinas disponibles
        PermissionCodes.DISCIPLINE_VIEW,
        
        # Salones - Ver salones disponibles para programar clases
        PermissionCodes.SALON_VIEW,
        
        # Clases - Gestión completa de sus clases (CU20: Programar clase)
        PermissionCodes.CLASE_VIEW,
        PermissionCodes.CLASE_CREATE,
        PermissionCodes.CLASE_EDIT,
        PermissionCodes.CLASE_DELETE,
        
        # Inscripciones a Clases - Gestión de inscripciones (CU21: Inscribir cliente, CU22: Asistencia)
        PermissionCodes.INSCRIPCION_CLASE_VIEW,
        PermissionCodes.INSCRIPCION_CLASE_CREATE,
        PermissionCodes.INSCRIPCION_CLASE_EDIT,
        PermissionCodes.INSCRIPCION_CLASE_DELETE,
        
        # Asistencias - Control completo (CU22: Controlar asistencia a clase)
        PermissionCodes.ASISTENCIA_VIEW,
        PermissionCodes.ASISTENCIA_CREATE,
        PermissionCodes.ASISTENCIA_EDIT,
        PermissionCodes.ASISTENCIA_DELETE,
        PermissionCodes.ASISTENCIA_VIEW_DETAILS,
    ]
    
    # Alias para compatibilidad
    COACH = INSTRUCTOR


# ==========================================
# CLASES DE PERMISOS DRF
# ==========================================

class HasPermission(BasePermission):
    """
    Permiso genérico que verifica si el usuario tiene un permiso específico.
    Uso: permission_classes = [HasPermission]
    Se debe especificar 'required_permission' en la vista.
    """
    
    def has_permission(self, request, view):
        # El admin siempre tiene permiso
        if request.user and request.user.is_superuser:
            return True
        
        # Obtener el permiso requerido de la vista
        required_permission = getattr(view, 'required_permission', None)
        
        if not required_permission:
            # Si no se especifica permiso, denegar por defecto
            return False
        
        # Verificar si el usuario tiene el permiso
        return user_has_permission(request.user, required_permission)


class HasAnyPermission(BasePermission):
    """
    Verifica si el usuario tiene AL MENOS UNO de los permisos especificados.
    Uso: permission_classes = [HasAnyPermission]
    Se debe especificar 'required_permissions' (lista) en la vista.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        required_permissions = getattr(view, 'required_permissions', [])
        
        if not required_permissions:
            return False
        
        # Retorna True si tiene al menos uno de los permisos
        return any(
            user_has_permission(request.user, perm) 
            for perm in required_permissions
        )


class HasAllPermissions(BasePermission):
    """
    Verifica si el usuario tiene TODOS los permisos especificados.
    Uso: permission_classes = [HasAllPermissions]
    Se debe especificar 'required_permissions' (lista) en la vista.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        required_permissions = getattr(view, 'required_permissions', [])
        
        if not required_permissions:
            return False
        
        # Retorna True solo si tiene TODOS los permisos
        return all(
            user_has_permission(request.user, perm) 
            for perm in required_permissions
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin puede hacer todo, otros solo lectura (GET, HEAD, OPTIONS).
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        # Métodos seguros (solo lectura)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return False


# ==========================================
# FUNCIONES HELPER
# ==========================================

def user_has_permission(user, permission_code: str) -> bool:
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        user: Usuario de Django
        permission_code: Código del permiso (ej: "client.view")
    
    Returns:
        bool: True si tiene el permiso, False si no
    """
    if not user or not user.is_authenticated:
        return False
    
    # El superuser siempre tiene todos los permisos
    if user.is_superuser:
        return True
    
    # Obtener todos los permisos del usuario a través de sus roles
    from apps.roles.models import Permiso
    
    user_permissions = Permiso.objects.filter(
        roles__userrole__usuario=user
    ).values_list('codigo', flat=True)  # ✅ CORREGIDO: usar 'codigo' en lugar de 'nombre'
    
    return permission_code in user_permissions


def user_has_any_permission(user, permission_codes: List[str]) -> bool:
    """Verifica si el usuario tiene AL MENOS UNO de los permisos."""
    return any(user_has_permission(user, code) for code in permission_codes)


def user_has_all_permissions(user, permission_codes: List[str]) -> bool:
    """Verifica si el usuario tiene TODOS los permisos."""
    return all(user_has_permission(user, code) for code in permission_codes)


def get_user_permissions(user) -> List[str]:
    """
    Obtiene todos los códigos de permisos que tiene un usuario.
    
    Returns:
        List[str]: Lista de códigos de permisos (ej: ["client.view", "user.create"])
    """
    if not user or not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return PermissionGroups.ADMIN
    
    from apps.roles.models import Permiso
    
    return list(
        Permiso.objects.filter(
            roles__userrole__usuario=user
        ).values_list('codigo', flat=True).distinct()  # ✅ CORREGIDO: usar 'codigo'
    )


def get_user_roles(user):
    """Obtiene todos los roles asignados a un usuario."""
    if not user or not user.is_authenticated:
        return []
    
    from apps.roles.models import Role
    
    return list(
        Role.objects.filter(
            userrole__usuario=user
        ).distinct()
    )
