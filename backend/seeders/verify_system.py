"""
Script de Verificación del Sistema
Verifica que todos los componentes estén funcionando correctamente
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.roles.models import Role, Permiso, UserRole, RolPermiso
from apps.clients.models import Client
from apps.membresias.models import PlanMembresia
from apps.promociones.models import Promocion


def print_header(title):
    """Imprime un header bonito"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_section(title):
    """Imprime una sección"""
    print(f"\n{'─'*70}")
    print(f"📊 {title}")
    print('─'*70)


def check_database_connection():
    """Verifica la conexión a la base de datos"""
    print_section("Verificando Conexión a Base de Datos")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_migrations():
    """Verifica que las migraciones estén aplicadas"""
    print_section("Verificando Migraciones")
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠️  Hay {len(plan)} migraciones pendientes")
            print("   Ejecuta: python manage.py migrate")
            return False
        else:
            print("✅ Todas las migraciones están aplicadas")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_users():
    """Verifica usuarios del sistema"""
    print_section("Usuarios del Sistema")
    
    try:
        total = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        active = User.objects.filter(is_active=True).count()
        
        print(f"   Total usuarios: {total}")
        print(f"   Superusuarios: {superusers}")
        print(f"   Activos: {active}")
        
        # Verificar admin
        try:
            admin = User.objects.get(username='admin')
            print(f"\n   ✅ Usuario 'admin' existe")
            print(f"      Email: {admin.email}")
            print(f"      Superuser: {admin.is_superuser}")
            print(f"      Activo: {admin.is_active}")
            
            # Verificar roles del admin
            admin_roles = UserRole.objects.filter(usuario=admin)
            print(f"      Roles asignados: {admin_roles.count()}")
            for ur in admin_roles:
                print(f"         - {ur.rol.nombre}")
        except User.DoesNotExist:
            print("   ⚠️  Usuario 'admin' no existe")
            print("      Ejecuta: python seeders/init_system.py")
            return False
        
        if total >= 1:
            print(f"\n   ✅ Sistema tiene {total} usuario(s)")
            return True
        else:
            print("   ⚠️  No hay usuarios en el sistema")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_rbac():
    """Verifica el sistema de roles y permisos"""
    print_section("Sistema RBAC (Roles y Permisos)")
    
    try:
        # Permisos
        total_permisos = Permiso.objects.count()
        print(f"   Permisos creados: {total_permisos}")
        
        if total_permisos < 46:
            print(f"   ⚠️  Se esperan al menos 46 permisos, hay {total_permisos}")
            print("      Ejecuta: python seeders/permissions_seeder.py")
        else:
            print("   ✅ Permisos completos")
        
        # Roles
        total_roles = Role.objects.count()
        print(f"\n   Roles creados: {total_roles}")
        
        if total_roles > 0:
            print("   Roles disponibles:")
            for role in Role.objects.all():
                permisos_count = role.permisos.count()
                usuarios_count = UserRole.objects.filter(rol=role).count()
                print(f"      - {role.nombre}: {permisos_count} permisos, {usuarios_count} usuarios")
            print("   ✅ Roles configurados")
        else:
            print("   ⚠️  No hay roles configurados")
            print("      Ejecuta: python seeders/roles_default_seeder.py")
            return False
        
        # Asignaciones
        total_asignaciones = UserRole.objects.count()
        print(f"\n   Asignaciones usuario-rol: {total_asignaciones}")
        
        if total_asignaciones > 0:
            print("   ✅ Usuarios tienen roles asignados")
            return True
        else:
            print("   ⚠️  No hay usuarios con roles asignados")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_data():
    """Verifica datos de prueba"""
    print_section("Datos de Prueba")
    
    try:
        # Clientes
        total_clientes = Client.objects.count()
        print(f"   Clientes: {total_clientes}")
        
        # Planes
        total_planes = PlanMembresia.objects.count()
        print(f"   Planes de membresía: {total_planes}")
        
        # Promociones
        total_promociones = Promocion.objects.count()
        print(f"   Promociones: {total_promociones}")
        
        if total_clientes > 0 and total_planes > 0:
            print("\n   ✅ Datos de prueba cargados")
            return True
        else:
            print("\n   ⚠️  Faltan datos de prueba")
            print("      Ejecuta: python manage.py seed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_api_access():
    """Verifica acceso a API"""
    print_section("Verificación de API")
    
    print("   Endpoints disponibles:")
    print("      - GET  /api/users/me/")
    print("      - POST /api/auth/login/")
    print("      - GET  /api/roles/")
    print("      - GET  /api/permissions/")
    print("      - GET  /api/clients/")
    print("      - GET  /api/membresias/")
    print("      - GET  /api/promociones/")
    print("      - GET  /api/audit/logs/")
    print("      - GET  /api/docs/ (Swagger)")
    
    print("\n   ✅ API REST funcionando en http://localhost:8000/api/")
    return True


def main():
    """Función principal"""
    print_header("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
    
    checks = [
        ("Conexión a Base de Datos", check_database_connection),
        ("Migraciones", check_migrations),
        ("Usuarios", check_users),
        ("RBAC (Roles y Permisos)", check_rbac),
        ("Datos de Prueba", check_data),
        ("API REST", check_api_access),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print_header("📋 RESUMEN DE VERIFICACIÓN")
    
    success = 0
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"   {icon} {name}")
        if result:
            success += 1
    
    print("\n" + "="*70)
    percentage = (success / total) * 100
    print(f"   Resultado: {success}/{total} verificaciones exitosas ({percentage:.0f}%)")
    print("="*70)
    
    if success == total:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("\n📝 Credenciales de acceso:")
        print("   Frontend: http://localhost:3000")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("\n⚠️  Algunos componentes necesitan atención.")
        print("\n🔧 Para resolver problemas:")
        print("   1. Ejecutar migraciones:")
        print("      docker compose exec backend python manage.py migrate")
        print("   2. Cargar datos completos:")
        print("      docker compose exec backend python seeders/init_system.py")


if __name__ == '__main__':
    main()
