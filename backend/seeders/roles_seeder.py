"""
Seeder para crear roles y permisos del sistema
"""
from apps.roles.models import Role, Permiso, RolPermiso
from .base_seeder import BaseSeeder


class RolesSeeder(BaseSeeder):
    """
    Crea los roles y permisos básicos del sistema
    """
    
    def seed(self):
        """
        Crea los roles predefinidos
        """
        print("\n👥 Creando Roles y Permisos...")
        
        # Permisos básicos
        permisos_data = [
            {
                'nombre': 'Gestión de Usuarios',
                'descripcion': 'Puede crear, editar y eliminar usuarios del sistema'
            },
            {
                'nombre': 'Gestión de Clientes',
                'descripcion': 'Puede crear, editar y eliminar clientes'
            },
            {
                'nombre': 'Gestión de Membresías',
                'descripcion': 'Puede crear, editar y asignar membresías'
            },
            {
                'nombre': 'Ver Reportes',
                'descripcion': 'Puede visualizar reportes del sistema'
            },
            {
                'nombre': 'Gestión de Roles',
                'descripcion': 'Puede crear, editar y eliminar roles'
            },
        ]
        
        # Crear permisos
        permisos = {}
        for permiso_data in permisos_data:
            permiso, created = Permiso.objects.get_or_create(
                nombre=permiso_data['nombre'],
                defaults={'descripcion': permiso_data['descripcion']}
            )
            permisos[permiso_data['nombre']] = permiso
            
            if created:
                print(f"   ✅ Permiso creado: {permiso_data['nombre']}")
                self.created_count += 1
            else:
                self.updated_count += 1
        
        # Roles básicos
        roles_data = [
            {
                'nombre': 'Administrador',
                'descripcion': 'Acceso total al sistema',
                'permisos': ['Gestión de Usuarios', 'Gestión de Clientes', 'Gestión de Membresías', 
                           'Ver Reportes', 'Gestión de Roles']
            },
            {
                'nombre': 'Gerente',
                'descripcion': 'Gestión de clientes y membresías',
                'permisos': ['Gestión de Clientes', 'Gestión de Membresías', 'Ver Reportes']
            },
            {
                'nombre': 'Recepcionista',
                'descripcion': 'Gestión básica de clientes',
                'permisos': ['Gestión de Clientes', 'Gestión de Membresías']
            },
            {
                'nombre': 'Entrenador',
                'descripcion': 'Visualización de información de clientes',
                'permisos': []
            },
        ]
        
        # Crear roles
        for rol_data in roles_data:
            rol, created = Role.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            
            # Asignar permisos al rol usando la tabla intermedia
            for permiso_nombre in rol_data['permisos']:
                if permiso_nombre in permisos:
                    RolPermiso.objects.get_or_create(
                        rol=rol,
                        permiso=permisos[permiso_nombre]
                    )
            
            if created:
                print(f"   ✅ Rol creado: {rol_data['nombre']}")
                self.created_count += 1
            else:
                self.updated_count += 1
