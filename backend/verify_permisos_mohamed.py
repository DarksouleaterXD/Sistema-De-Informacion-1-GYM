"""
Script para verificar permisos de auditoría del usuario mohamed
"""

from apps.users.models import User
from apps.roles.models import Role, Permiso, UserRole
from apps.core.permissions import user_has_permission, PermissionCodes, get_user_permissions

def verificar_permisos_mohamed():
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE PERMISOS - Usuario: mohamed")
    print("="*60 + "\n")
    
    # 1. Obtener usuario mohamed
    try:
        user = User.objects.get(username='mohamed')
        print(f"✅ Usuario encontrado: {user.username} (ID: {user.id})")
        print(f"   Email: {user.email}")
        print(f"   Superuser: {user.is_superuser}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Activo: {user.is_active}")
    except User.DoesNotExist:
        print("❌ Usuario 'mohamed' no existe")
        return
    
    print("\n" + "-"*60)
    
    # 2. Obtener roles asignados
    user_roles = UserRole.objects.filter(usuario=user).select_related('rol')
    print(f"\n📋 ROLES ASIGNADOS ({user_roles.count()}):")
    if user_roles.exists():
        for ur in user_roles:
            permisos_count = ur.rol.permisos.count()
            print(f"   • {ur.rol.nombre} ({permisos_count} permisos)")
    else:
        print("   ❌ Sin roles asignados")
    
    print("\n" + "-"*60)
    
    # 3. Obtener todos los permisos del usuario
    permisos = get_user_permissions(user)
    print(f"\n🔐 PERMISOS DEL USUARIO ({len(permisos)} total):")
    
    # Agrupar por módulo
    permisos_por_modulo = {}
    for permiso in permisos:
        modulo = permiso.split('.')[0]
        if modulo not in permisos_por_modulo:
            permisos_por_modulo[modulo] = []
        permisos_por_modulo[modulo].append(permiso)
    
    for modulo, perms in sorted(permisos_por_modulo.items()):
        print(f"\n   📦 {modulo.upper()}:")
        for perm in sorted(perms):
            print(f"      ✓ {perm}")
    
    print("\n" + "-"*60)
    
    # 4. Verificar permisos específicos de auditoría
    print("\n🎯 VERIFICACIÓN DE PERMISOS DE AUDITORÍA:")
    
    audit_permisos = [
        ('AUDIT_VIEW', PermissionCodes.AUDIT_VIEW),
        ('AUDIT_VIEW_DETAILS', PermissionCodes.AUDIT_VIEW_DETAILS),
        ('AUDIT_EXPORT', PermissionCodes.AUDIT_EXPORT),
    ]
    
    for nombre, codigo in audit_permisos:
        tiene = user_has_permission(user, codigo)
        simbolo = "✅" if tiene else "❌"
        print(f"   {simbolo} {nombre} ({codigo}): {tiene}")
    
    print("\n" + "-"*60)
    
    # 5. Verificar rol 'rol-test'
    print("\n🧪 VERIFICACIÓN DEL ROL 'rol-test':")
    try:
        rol_test = Role.objects.get(nombre='rol-test')
        print(f"   ✅ Rol encontrado: {rol_test.nombre}")
        print(f"   Descripción: {rol_test.descripcion}")
        
        permisos_rol = rol_test.permisos.all()
        print(f"\n   Permisos del rol ({permisos_rol.count()}):")
        for permiso in permisos_rol.order_by('codigo'):
            print(f"      • {permiso.codigo} - {permiso.nombre}")
        
        # Verificar si mohamed tiene este rol
        tiene_rol = UserRole.objects.filter(usuario=user, rol=rol_test).exists()
        print(f"\n   {'✅' if tiene_rol else '❌'} Mohamed tiene asignado este rol: {tiene_rol}")
        
    except Role.DoesNotExist:
        print("   ❌ Rol 'rol-test' no existe")
    
    print("\n" + "="*60)
    print("✅ Verificación completada")
    print("="*60 + "\n")

if __name__ == "__main__":
    verificar_permisos_mohamed()
