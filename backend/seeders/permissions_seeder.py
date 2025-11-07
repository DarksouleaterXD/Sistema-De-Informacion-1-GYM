"""
Seeder para permisos del sistema.
Crea todos los permisos definidos en el sistema de RBAC.
"""

import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.roles.models import Permiso
from apps.core.permissions import PermissionCodes


class PermissionSeeder:
    """Seeder para crear todos los permisos del sistema."""
    
    # Definición de permisos con sus descripciones
    PERMISSIONS = [
        # DASHBOARD
        {
            'codigo': PermissionCodes.DASHBOARD_VIEW,
            'nombre': 'Ver Dashboard',
            'descripcion': 'Ver el dashboard principal y estadísticas'
        },
        
        # USUARIOS
        {
            'codigo': PermissionCodes.USER_VIEW,
            'nombre': 'Ver Usuarios',
            'descripcion': 'Ver lista de usuarios del sistema'
        },
        {
            'codigo': PermissionCodes.USER_CREATE,
            'nombre': 'Crear Usuario',
            'descripcion': 'Crear nuevos usuarios en el sistema'
        },
        {
            'codigo': PermissionCodes.USER_EDIT,
            'nombre': 'Editar Usuario',
            'descripcion': 'Editar información de usuarios existentes'
        },
        {
            'codigo': PermissionCodes.USER_DELETE,
            'nombre': 'Eliminar Usuario',
            'descripcion': 'Eliminar usuarios del sistema'
        },
        {
            'codigo': PermissionCodes.USER_VIEW_DETAILS,
            'nombre': 'Ver Detalles de Usuario',
            'descripcion': 'Ver detalles completos de un usuario'
        },
        
        # ROLES Y PERMISOS
        {
            'codigo': PermissionCodes.ROLE_VIEW,
            'nombre': 'Ver Roles',
            'descripcion': 'Ver lista de roles del sistema'
        },
        {
            'codigo': PermissionCodes.ROLE_CREATE,
            'nombre': 'Crear Rol',
            'descripcion': 'Crear nuevos roles'
        },
        {
            'codigo': PermissionCodes.ROLE_EDIT,
            'nombre': 'Editar Rol',
            'descripcion': 'Editar roles existentes'
        },
        {
            'codigo': PermissionCodes.ROLE_DELETE,
            'nombre': 'Eliminar Rol',
            'descripcion': 'Eliminar roles del sistema'
        },
        {
            'codigo': PermissionCodes.ROLE_ASSIGN_PERMISSIONS,
            'nombre': 'Asignar Permisos a Rol',
            'descripcion': 'Asignar o quitar permisos a roles'
        },
        {
            'codigo': PermissionCodes.ROLE_ASSIGN_TO_USER,
            'nombre': 'Asignar Rol a Usuario',
            'descripcion': 'Asignar roles a usuarios'
        },
        {
            'codigo': PermissionCodes.PERMISSION_VIEW,
            'nombre': 'Ver Permisos',
            'descripcion': 'Ver lista de permisos disponibles'
        },
        {
            'codigo': PermissionCodes.PERMISSION_CREATE,
            'nombre': 'Crear Permiso',
            'descripcion': 'Crear nuevos permisos'
        },
        {
            'codigo': PermissionCodes.PERMISSION_EDIT,
            'nombre': 'Editar Permiso',
            'descripcion': 'Editar permisos existentes'
        },
        {
            'codigo': PermissionCodes.PERMISSION_DELETE,
            'nombre': 'Eliminar Permiso',
            'descripcion': 'Eliminar permisos del sistema'
        },
        
        # CLIENTES
        {
            'codigo': PermissionCodes.CLIENT_VIEW,
            'nombre': 'Ver Clientes',
            'descripcion': 'Ver lista de clientes del gimnasio'
        },
        {
            'codigo': PermissionCodes.CLIENT_CREATE,
            'nombre': 'Crear Cliente',
            'descripcion': 'Registrar nuevos clientes'
        },
        {
            'codigo': PermissionCodes.CLIENT_EDIT,
            'nombre': 'Editar Cliente',
            'descripcion': 'Editar información de clientes'
        },
        {
            'codigo': PermissionCodes.CLIENT_DELETE,
            'nombre': 'Eliminar Cliente',
            'descripcion': 'Eliminar clientes del sistema'
        },
        {
            'codigo': PermissionCodes.CLIENT_VIEW_DETAILS,
            'nombre': 'Ver Detalles de Cliente',
            'descripcion': 'Ver detalles completos de un cliente'
        },
        
        # MEMBRESÍAS
        {
            'codigo': PermissionCodes.MEMBERSHIP_VIEW,
            'nombre': 'Ver Membresías',
            'descripcion': 'Ver lista de membresías activas'
        },
        {
            'codigo': PermissionCodes.MEMBERSHIP_CREATE,
            'nombre': 'Crear Membresía',
            'descripcion': 'Crear nuevas membresías para clientes'
        },
        {
            'codigo': PermissionCodes.MEMBERSHIP_EDIT,
            'nombre': 'Editar Membresía',
            'descripcion': 'Editar membresías existentes'
        },
        {
            'codigo': PermissionCodes.MEMBERSHIP_DELETE,
            'nombre': 'Eliminar Membresía',
            'descripcion': 'Eliminar o cancelar membresías'
        },
        {
            'codigo': PermissionCodes.MEMBERSHIP_VIEW_STATS,
            'nombre': 'Ver Estadísticas de Membresías',
            'descripcion': 'Ver estadísticas de membresías'
        },
        {
            'codigo': PermissionCodes.MEMBERSHIP_VIEW_DETAILS,
            'nombre': 'Ver Detalles de Membresía',
            'descripcion': 'Ver detalles completos de una membresía'
        },
        
        # PLANES DE MEMBRESÍA
        {
            'codigo': PermissionCodes.PLAN_VIEW,
            'nombre': 'Ver Planes',
            'descripcion': 'Ver planes de membresía disponibles'
        },
        {
            'codigo': PermissionCodes.PLAN_CREATE,
            'nombre': 'Crear Plan',
            'descripcion': 'Crear nuevos planes de membresía'
        },
        {
            'codigo': PermissionCodes.PLAN_EDIT,
            'nombre': 'Editar Plan',
            'descripcion': 'Editar planes de membresía existentes'
        },
        {
            'codigo': PermissionCodes.PLAN_DELETE,
            'nombre': 'Eliminar Plan',
            'descripcion': 'Eliminar planes de membresía'
        },
        
        # PROMOCIONES
        {
            'codigo': PermissionCodes.PROMOTION_VIEW,
            'nombre': 'Ver Promociones',
            'descripcion': 'Ver promociones y descuentos'
        },
        {
            'codigo': PermissionCodes.PROMOTION_CREATE,
            'nombre': 'Crear Promoción',
            'descripcion': 'Crear nuevas promociones'
        },
        {
            'codigo': PermissionCodes.PROMOTION_EDIT,
            'nombre': 'Editar Promoción',
            'descripcion': 'Editar promociones existentes'
        },
        {
            'codigo': PermissionCodes.PROMOTION_DELETE,
            'nombre': 'Eliminar Promoción',
            'descripcion': 'Eliminar promociones'
        },
        {
            'codigo': PermissionCodes.PROMOTION_VIEW_DETAILS,
            'nombre': 'Ver Detalles de Promoción',
            'descripcion': 'Ver detalles completos de una promoción'
        },
        
        # INSCRIPCIONES
        {
            'codigo': PermissionCodes.ENROLLMENT_VIEW,
            'nombre': 'Ver Inscripciones',
            'descripcion': 'Ver lista de inscripciones'
        },
        {
            'codigo': PermissionCodes.ENROLLMENT_CREATE,
            'nombre': 'Crear Inscripción',
            'descripcion': 'Crear nuevas inscripciones'
        },
        {
            'codigo': PermissionCodes.ENROLLMENT_EDIT,
            'nombre': 'Editar Inscripción',
            'descripcion': 'Editar inscripciones existentes'
        },
        {
            'codigo': PermissionCodes.ENROLLMENT_DELETE,
            'nombre': 'Eliminar Inscripción',
            'descripcion': 'Eliminar inscripciones'
        },
        
        # DISCIPLINAS
        {
            'codigo': PermissionCodes.DISCIPLINE_VIEW,
            'nombre': 'Ver Disciplinas',
            'descripcion': 'Ver lista de disciplinas del gimnasio'
        },
        {
            'codigo': PermissionCodes.DISCIPLINE_CREATE,
            'nombre': 'Crear Disciplina',
            'descripcion': 'Crear nuevas disciplinas'
        },
        {
            'codigo': PermissionCodes.DISCIPLINE_EDIT,
            'nombre': 'Editar Disciplina',
            'descripcion': 'Editar disciplinas existentes'
        },
        {
            'codigo': PermissionCodes.DISCIPLINE_DELETE,
            'nombre': 'Eliminar Disciplina',
            'descripcion': 'Eliminar disciplinas'
        },
        
        # SALONES
        {
            'codigo': PermissionCodes.SALON_VIEW,
            'nombre': 'Ver Salones',
            'descripcion': 'Ver lista de salones del gimnasio'
        },
        {
            'codigo': PermissionCodes.SALON_CREATE,
            'nombre': 'Crear Salón',
            'descripcion': 'Crear nuevos salones'
        },
        {
            'codigo': PermissionCodes.SALON_EDIT,
            'nombre': 'Editar Salón',
            'descripcion': 'Editar salones existentes'
        },
        {
            'codigo': PermissionCodes.SALON_DELETE,
            'nombre': 'Eliminar Salón',
            'descripcion': 'Eliminar salones'
        },
        
        # CLASES
        {
            'codigo': PermissionCodes.CLASE_VIEW,
            'nombre': 'Ver Clases',
            'descripcion': 'Ver lista de clases programadas'
        },
        {
            'codigo': PermissionCodes.CLASE_CREATE,
            'nombre': 'Programar Clase',
            'descripcion': 'Programar nuevas clases'
        },
        {
            'codigo': PermissionCodes.CLASE_EDIT,
            'nombre': 'Editar Clase',
            'descripcion': 'Editar clases programadas'
        },
        {
            'codigo': PermissionCodes.CLASE_DELETE,
            'nombre': 'Cancelar Clase',
            'descripcion': 'Cancelar clases programadas'
        },
        
        # INSCRIPCIONES A CLASES
        {
            'codigo': PermissionCodes.INSCRIPCION_CLASE_VIEW,
            'nombre': 'Ver Inscripciones a Clases',
            'descripcion': 'Ver inscripciones de clientes a clases'
        },
        {
            'codigo': PermissionCodes.INSCRIPCION_CLASE_CREATE,
            'nombre': 'Inscribir a Clase',
            'descripcion': 'Inscribir clientes a clases'
        },
        {
            'codigo': PermissionCodes.INSCRIPCION_CLASE_EDIT,
            'nombre': 'Editar Inscripción a Clase',
            'descripcion': 'Editar inscripciones a clases'
        },
        {
            'codigo': PermissionCodes.INSCRIPCION_CLASE_DELETE,
            'nombre': 'Cancelar Inscripción a Clase',
            'descripcion': 'Cancelar inscripciones a clases'
        },
        
        # AUDITORÍA
        {
            'codigo': PermissionCodes.AUDIT_VIEW,
            'nombre': 'Ver Auditoría',
            'descripcion': 'Ver registros de auditoría del sistema'
        },
        {
            'codigo': PermissionCodes.AUDIT_VIEW_DETAILS,
            'nombre': 'Ver Detalles de Auditoría',
            'descripcion': 'Ver detalles completos de registros de auditoría'
        },
        {
            'codigo': PermissionCodes.AUDIT_EXPORT,
            'nombre': 'Exportar Auditoría',
            'descripcion': 'Exportar registros de auditoría'
        },
        
        # REPORTES
        {
            'codigo': PermissionCodes.REPORT_VIEW,
            'nombre': 'Ver Reportes',
            'descripcion': 'Ver reportes y estadísticas'
        },
        {
            'codigo': PermissionCodes.REPORT_GENERATE,
            'nombre': 'Generar Reporte',
            'descripcion': 'Generar nuevos reportes'
        },
        {
            'codigo': PermissionCodes.REPORT_EXPORT,
            'nombre': 'Exportar Reporte',
            'descripcion': 'Exportar reportes en diferentes formatos'
        },
    ]
    
    def run(self):
        """Ejecuta el seeder."""
        print("🔐 Iniciando seeder de permisos...")
        
        created_count = 0
        updated_count = 0
        
        for perm_data in self.PERMISSIONS:
            permiso, created = Permiso.objects.update_or_create(
                codigo=perm_data['codigo'],
                defaults={
                    'nombre': perm_data['nombre'],
                    'descripcion': perm_data['descripcion']
                }
            )
            
            if created:
                created_count += 1
                print(f"  ✅ Creado: {permiso.codigo} - {permiso.nombre}")
            else:
                updated_count += 1
                print(f"  ♻️  Actualizado: {permiso.codigo} - {permiso.nombre}")
        
        print(f"\n✅ Seeder completado:")
        print(f"  - {created_count} permisos creados")
        print(f"  - {updated_count} permisos actualizados")
        print(f"  - {created_count + updated_count} permisos totales")
        
        return True  # 🔥 RETORNAR True para indicar éxito


if __name__ == '__main__':
    seeder = PermissionSeeder()
    seeder.run()
