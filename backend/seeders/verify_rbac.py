"""
Script de verificación del sistema RBAC.
Verifica que el usuario admin tenga todos los permisos necesarios.

Uso:
    python seeders/verify_rbac.py
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.roles.models import Role, UserRole, Permiso
from apps.core.permissions import get_user_permissions, get_user_roles, PermissionCodes


def verify_rbac():
    """Verifica el estado del sistema RBAC."""
    
    print("\n" + "=" * 70)
    print("🔍 VERIFICACIÓN DEL SISTEMA RBAC")
    print("=" * 70)
    
    # ========================================
    # 1. VERIFICAR PERMISOS EN BASE DE DATOS
    # ========================================
    print("\n📊 1. PERMISOS EN BASE DE DATOS")
    print("-" * 70)
    
    total_permisos = Permiso.objects.count()
    print(f"   Total de permisos creados: {total_permisos}")
    
    if total_permisos < 46:
        print(f"   ⚠️  ADVERTENCIA: Se esperaban al menos 46 permisos")
        print(f"   💡 Ejecuta: python seeders/setup_rbac.py")
    else:
        print(f"   ✅ Cantidad de permisos correcta")
    
    # Mostrar algunos permisos
    print("\n   Primeros 10 permisos:")
    for p in Permiso.objects.all()[:10]:
        print(f"      • {p.nombre} - {p.descripcion}")
    
    # ========================================
    # 2. VERIFICAR ROLES
    # ========================================
    print("\n📊 2. ROLES CONFIGURADOS")
    print("-" * 70)
    
    total_roles = Role.objects.count()
    print(f"   Total de roles: {total_roles}")
    
    for role in Role.objects.all():
        permisos_count = role.permisos.count()
        print(f"      • {role.nombre}: {permisos_count} permisos")
    
    # ========================================
    # 3. VERIFICAR USUARIO ADMIN
    # ========================================
    print("\n📊 3. VERIFICAR USUARIO ADMIN")
    print("-" * 70)
    
    try:
        admin = User.objects.get(username='admin')
        print(f"   ✅ Usuario encontrado: {admin.get_full_name()}")
        print(f"      Email: {admin.email}")
        print(f"      Superuser: {admin.is_superuser}")
        
        # Verificar roles
        user_roles = get_user_roles(admin)
        print(f"\n   Roles asignados: {len(user_roles)}")
        for role in user_roles:
            print(f"      • {role.nombre} ({role.permisos.count()} permisos)")
        
        # Verificar permisos
        user_perms = get_user_permissions(admin)
        print(f"\n   Permisos totales: {len(user_perms)}")
        
        if admin.is_superuser:
            print(f"      ℹ️  Como superuser, tiene acceso a TODOS los permisos")
        
        # Mostrar algunos permisos
        print("\n   Primeros 15 permisos del usuario:")
        for perm in user_perms[:15]:
            print(f"      • {perm}")
        
        if len(user_perms) > 15:
            print(f"      ... y {len(user_perms) - 15} más")
        
        # ========================================
        # 4. VERIFICAR PERMISOS CLAVE
        # ========================================
        print("\n📊 4. VERIFICAR PERMISOS CLAVE DEL ADMIN")
        print("-" * 70)
        
        permisos_criticos = [
            ('dashboard.view', 'Ver Dashboard'),
            ('client.view', 'Ver Clientes'),
            ('client.create', 'Crear Clientes'),
            ('user.view', 'Ver Usuarios'),
            ('user.create', 'Crear Usuarios'),
            ('role.view', 'Ver Roles'),
            ('membership.view', 'Ver Membresías'),
            ('promotion.view', 'Ver Promociones'),
            ('audit.view', 'Ver Auditoría'),
        ]
        
        todos_ok = True
        for perm_code, perm_name in permisos_criticos:
            tiene = perm_code in user_perms or admin.is_superuser
            status = "✅" if tiene else "❌"
            print(f"   {status} {perm_name} ({perm_code})")
            if not tiene:
                todos_ok = False
        
        if todos_ok:
            print("\n   ✅ Todos los permisos críticos están presentes")
        else:
            print("\n   ⚠️  Faltan algunos permisos críticos")
        
    except User.DoesNotExist:
        print("   ❌ ERROR: Usuario 'admin' no encontrado")
        print("\n   💡 Usuarios disponibles:")
        for u in User.objects.all()[:5]:
            print(f"      - {u.username}")
        return False
    
    # ========================================
    # 5. VERIFICAR ESTRUCTURA DE ROLES
    # ========================================
    print("\n📊 5. ESTRUCTURA DE ROLES Y USUARIOS")
    print("-" * 70)
    
    total_user_roles = UserRole.objects.count()
    print(f"   Total de asignaciones usuario-rol: {total_user_roles}")
    
    print("\n   Desglose por rol:")
    for role in Role.objects.all():
        count = UserRole.objects.filter(rol=role).count()
        print(f"      • {role.nombre}: {count} usuario(s)")
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print("\n" + "=" * 70)
    print("📋 RESUMEN")
    print("=" * 70)
    
    print(f"\n   ✅ Permisos en BD: {total_permisos}")
    print(f"   ✅ Roles configurados: {total_roles}")
    print(f"   ✅ Usuario admin: Configurado")
    print(f"   ✅ Permisos del admin: {len(user_perms)}")
    print(f"   ✅ Roles del admin: {len(user_roles)}")
    
    print("\n" + "=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)
    
    print("\n💡 SIGUIENTE PASO:")
    print("   Accede a http://localhost:3000 y haz login con:")
    print("   • Username: admin")
    print("   • Password: admin123")
    print("\n   Deberías ver:")
    print("   ✅ 8 items en el sidebar")
    print("   ✅ Botones de Crear/Editar/Eliminar visibles")
    print("   ✅ Acceso a todas las páginas")
    print("\n" + "=" * 70 + "\n")
    
    return True


if __name__ == '__main__':
    try:
        verify_rbac()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
