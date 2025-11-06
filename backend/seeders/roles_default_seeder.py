"""
Seeder para crear los roles predeterminados del sistema con sus permisos.

Crea 3 roles:
- Administrador: Acceso completo (51 permisos)
- Administrativo: Gestión diaria sin eliminaciones críticas (36 permisos)
- Coach: Solo lectura (13 permisos)

Uso:
    python seeders/roles_default_seeder.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.roles.models import Role, Permiso, RolPermiso
from apps.core.permissions import PermissionGroups, PermissionCodes


def create_default_roles():
    """Crea los roles predeterminados con sus permisos."""
    
    print("\n🔐 Creando roles predeterminados...")
    print("=" * 60)
    
    # ========================================
    # ROL: ADMINISTRADOR
    # ========================================
    print("\n📌 Creando rol: Administrador")
    admin_role, created = Role.objects.get_or_create(
        nombre='Administrador',
        defaults={'descripcion': 'Acceso completo al sistema. Puede gestionar todo.'}
    )
    
    if created:
        print("   ✅ Rol 'Administrador' creado")
    else:
        print("   ℹ️  Rol 'Administrador' ya existe, actualizando permisos...")
    
    # Asignar TODOS los permisos
    admin_permissions_added = 0
    for perm_code in PermissionGroups.ADMIN:
        try:
            perm = Permiso.objects.get(codigo=perm_code)
            RolPermiso.objects.get_or_create(rol=admin_role, permiso=perm)
            admin_permissions_added += 1
        except Permiso.DoesNotExist:
            print(f"   ⚠️  Permiso '{perm_code}' no encontrado")
    
    print(f"   ✅ Asignados {admin_permissions_added} permisos al Administrador")
    
    # ========================================
    # ROL: ADMINISTRATIVO
    # ========================================
    print("\n📌 Creando rol: Administrativo")
    admin_staff_role, created = Role.objects.get_or_create(
        nombre='Administrativo',
        defaults={'descripcion': 'Gestión diaria del gimnasio. No puede eliminar usuarios ni roles.'}
    )
    
    if created:
        print("   ✅ Rol 'Administrativo' creado")
    else:
        print("   ℹ️  Rol 'Administrativo' ya existe, actualizando permisos...")
    
    # Asignar permisos de ADMINISTRATIVO
    admin_staff_permissions_added = 0
    for perm_code in PermissionGroups.ADMINISTRATIVO:
        try:
            perm = Permiso.objects.get(codigo=perm_code)
            RolPermiso.objects.get_or_create(rol=admin_staff_role, permiso=perm)
            admin_staff_permissions_added += 1
        except Permiso.DoesNotExist:
            print(f"   ⚠️  Permiso '{perm_code}' no encontrado")
    
    print(f"   ✅ Asignados {admin_staff_permissions_added} permisos al Administrativo")
    
    # ========================================
    # ROL: INSTRUCTOR (CU18)
    # ========================================
    print("\n📌 Creando rol: Instructor")
    instructor_role, created = Role.objects.get_or_create(
        nombre='Instructor',
        defaults={'descripcion': 'Instructor/Coach del gimnasio. Puede consultar clientes inscritos y membresías (solo lectura para pasar lista).'}
    )
    
    if created:
        print("   ✅ Rol 'Instructor' creado")
    else:
        print("   ℹ️  Rol 'Instructor' ya existe, actualizando permisos...")
    
    # Asignar permisos de INSTRUCTOR
    instructor_permissions_added = 0
    for perm_code in PermissionGroups.INSTRUCTOR:
        try:
            perm = Permiso.objects.get(codigo=perm_code)
            RolPermiso.objects.get_or_create(rol=instructor_role, permiso=perm)
            instructor_permissions_added += 1
        except Permiso.DoesNotExist:
            print(f"   ⚠️  Permiso '{perm_code}' no encontrado")
    
    print(f"   ✅ Asignados {instructor_permissions_added} permisos al Instructor")
    
    # ========================================
    # RESUMEN
    # ========================================
    print("\n" + "=" * 60)
    print("✅ Roles predeterminados creados exitosamente")
    print("\n📊 RESUMEN:")
    print(f"   • Administrador: {admin_permissions_added} permisos")
    print(f"   • Administrativo: {admin_staff_permissions_added} permisos")
    print(f"   • Instructor: {instructor_permissions_added} permisos")
    print("\n💡 Ahora puedes asignar estos roles a los usuarios")
    print("=" * 60)


if __name__ == '__main__':
    try:
        create_default_roles()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
