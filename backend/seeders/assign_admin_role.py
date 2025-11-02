"""
Script para asignar rol Administrador al superuser.

Uso:
    python seeders/assign_admin_role.py [username]
    
Ejemplo:
    python seeders/assign_admin_role.py admin
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.roles.models import Role, UserRole


def assign_admin_role(username='admin'):
    """Asigna el rol Administrador a un usuario."""
    
    print("\n" + "=" * 60)
    print("🔐 ASIGNACIÓN DE ROL ADMINISTRADOR")
    print("=" * 60)
    
    try:
        # Buscar usuario
        print(f"\n📌 Buscando usuario: {username}")
        user = User.objects.get(username=username)
        print(f"   ✅ Usuario encontrado: {user.get_full_name()} ({user.email})")
        
        # Buscar rol
        print(f"\n📌 Buscando rol: Administrador")
        role = Role.objects.get(nombre='Administrador')
        print(f"   ✅ Rol encontrado: {role.nombre}")
        print(f"   ℹ️  Permisos del rol: {role.permisos.count()}")
        
        # Verificar si ya tiene el rol
        existing = UserRole.objects.filter(usuario=user, rol=role).first()
        if existing:
            print(f"\n   ℹ️  El usuario ya tiene el rol Administrador asignado")
            print(f"   Fecha de asignación: {existing.created_at}")
        else:
            # Asignar rol
            print(f"\n📌 Asignando rol...")
            user_role = UserRole.objects.create(usuario=user, rol=role)
            print(f"   ✅ Rol asignado exitosamente")
            print(f"   Fecha: {user_role.created_at}")
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN:")
        print(f"   Usuario: {user.username}")
        print(f"   Roles asignados: {user.roles.count()}")
        for ur in UserRole.objects.filter(usuario=user):
            print(f"      - {ur.rol.nombre} ({ur.rol.permisos.count()} permisos)")
        print("=" * 60)
        print("\n✅ Operación completada exitosamente")
        print("\n💡 Ahora el usuario puede hacer login y tendrá acceso completo")
        print("=" * 60 + "\n")
        
        return True
        
    except User.DoesNotExist:
        print(f"\n❌ ERROR: Usuario '{username}' no encontrado")
        print("\n💡 Usuarios disponibles:")
        for u in User.objects.all()[:5]:
            print(f"   - {u.username} ({u.get_full_name()})")
        return False
        
    except Role.DoesNotExist:
        print(f"\n❌ ERROR: Rol 'Administrador' no encontrado")
        print("\n💡 Ejecuta primero: python seeders/setup_rbac.py")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Obtener username de argumentos o usar 'admin' por defecto
    username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    
    success = assign_admin_role(username)
    sys.exit(0 if success else 1)
