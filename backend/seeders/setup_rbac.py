"""
Script maestro para configurar el sistema RBAC completo.

Este script ejecuta en orden:
1. Seeder de permisos (51 permisos)
2. Seeder de roles predeterminados (3 roles)

Uso:
    python seeders/setup_rbac.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from seeders.permissions_seeder import PermissionSeeder
from seeders.roles_default_seeder import create_default_roles


def setup_rbac():
    """Configura el sistema RBAC completo."""
    
    print("\n" + "=" * 70)
    print("🚀 CONFIGURACIÓN COMPLETA DEL SISTEMA RBAC")
    print("=" * 70)
    
    # PASO 1: Crear permisos
    print("\n📝 PASO 1: Creando permisos...")
    print("-" * 70)
    try:
        seeder = PermissionSeeder()
        seeder.run()
    except Exception as e:
        print(f"\n❌ ERROR al crear permisos: {e}")
        return False
    
    # PASO 2: Crear roles
    print("\n\n📝 PASO 2: Creando roles predeterminados...")
    print("-" * 70)
    try:
        create_default_roles()
    except Exception as e:
        print(f"\n❌ ERROR al crear roles: {e}")
        return False
    
    # ÉXITO
    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN RBAC COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\n📋 Próximos pasos:")
    print("   1. Asignar roles a usuarios existentes:")
    print("      python manage.py shell")
    print("      >>> from apps.users.models import User")
    print("      >>> from apps.roles.models import Role, UserRole")
    print("      >>> user = User.objects.get(username='admin')")
    print("      >>> role = Role.objects.get(nombre='Administrador')")
    print("      >>> UserRole.objects.create(usuario=user, rol=role)")
    print("\n   2. Reiniciar el servidor si está corriendo")
    print("\n   3. Verificar en el frontend que los permisos funcionan")
    print("\n" + "=" * 70 + "\n")
    
    return True


if __name__ == '__main__':
    try:
        success = setup_rbac()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
