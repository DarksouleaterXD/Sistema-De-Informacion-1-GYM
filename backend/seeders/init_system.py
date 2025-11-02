"""
Script Maestro de Inicialización del Sistema
Ejecuta TODOS los seeders y configuraciones necesarias en orden correcto
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.roles.models import Role, UserRole, Permiso, RolPermiso
from apps.clients.models import Client
from apps.membresias.models import PlanMembresia
from apps.promociones.models import Promocion


def print_header(title):
    """Imprime un header bonito"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_step(step, description):
    """Imprime un paso"""
    print(f"\n{'─'*70}")
    print(f"PASO {step}: {description}")
    print('─'*70)


def check_database():
    """Verifica la conexión a la base de datos"""
    print_step(0, "Verificando Conexión a Base de Datos")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False


def run_migrations():
    """Ejecuta las migraciones"""
    print_step(1, "Ejecutando Migraciones")
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput')
        print("✅ Migraciones ejecutadas correctamente")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {e}")
        return False


def create_superuser():
    """Crea el superusuario admin"""
    print_step(2, "Creando Superusuario Admin")
    try:
        if User.objects.filter(username='admin').exists():
            print("ℹ️  Usuario admin ya existe")
            admin = User.objects.get(username='admin')
        else:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@gym-spartan.com',
                password='admin123',
                nombre='Super',
                apellido='Admin'
            )
            print("✅ Superusuario admin creado")
        
        print(f"   Username: admin")
        print(f"   Email: admin@gym-spartan.com")
        print(f"   Password: admin123")
        print(f"   Superuser: {admin.is_superuser}")
        return True
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False


def setup_rbac():
    """Configura todo el sistema RBAC"""
    print_step(3, "Configurando Sistema RBAC (Permisos y Roles)")
    
    try:
        # Importar el setup_rbac
        from seeders.setup_rbac import setup_complete_rbac
        
        setup_complete_rbac()
        
        # Verificar resultados
        permisos_count = Permiso.objects.count()
        roles_count = Role.objects.count()
        
        print(f"✅ Sistema RBAC configurado:")
        print(f"   • {permisos_count} permisos creados")
        print(f"   • {roles_count} roles configurados")
        
        return True
    except Exception as e:
        print(f"❌ Error configurando RBAC: {e}")
        import traceback
        traceback.print_exc()
        return False


def assign_admin_role():
    """Asigna el rol Administrador al usuario admin"""
    print_step(4, "Asignando Rol Administrador a Admin")
    
    try:
        admin = User.objects.get(username='admin')
        role = Role.objects.get(nombre='Administrador')
        
        # Verificar si ya tiene el rol
        if UserRole.objects.filter(usuario=admin, rol=role).exists():
            print("ℹ️  Admin ya tiene el rol Administrador")
        else:
            UserRole.objects.create(usuario=admin, rol=role)
            print("✅ Rol Administrador asignado a admin")
        
        # Mostrar permisos
        permisos = admin.get_all_permissions()
        print(f"   • Permisos: {len(permisos)}")
        print(f"   • Superuser: {admin.is_superuser}")
        
        return True
    except Exception as e:
        print(f"❌ Error asignando rol: {e}")
        return False


def seed_data():
    """Ejecuta los seeders de datos"""
    print_step(5, "Cargando Datos de Prueba")
    
    try:
        # Plan de Membresías
        from seeders.plan_membresia_seeder import PlanMembresiaSeeder
        PlanMembresiaSeeder().run()
        
        # Promociones
        from seeders.promocion_seeder import PromocionSeeder
        PromocionSeeder().run()
        
        # Usuarios
        from seeders.users_seeder import UsersSeeder
        UsersSeeder().run()
        
        # Clientes
        from seeders.clients_seeder import ClientsSeeder
        ClientsSeeder().run()
        
        # Verificar datos
        print(f"\n📊 Datos Cargados:")
        print(f"   • Usuarios: {User.objects.count()}")
        print(f"   • Clientes: {Client.objects.count()}")
        print(f"   • Planes: {PlanMembresia.objects.count()}")
        print(f"   • Promociones: {Promocion.objects.count()}")
        
        return True
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_system():
    """Verifica que todo esté correcto"""
    print_step(6, "Verificando Sistema")
    
    try:
        # Verificar admin
        admin = User.objects.get(username='admin')
        permisos = list(admin.get_all_permissions())
        roles = UserRole.objects.filter(usuario=admin).count()
        
        print("\n✅ Usuario Admin:")
        print(f"   • Username: {admin.username}")
        print(f"   • Email: {admin.email}")
        print(f"   • Superuser: {admin.is_superuser}")
        print(f"   • Roles: {roles}")
        print(f"   • Permisos: {len(permisos)}")
        
        # Mostrar primeros 10 permisos
        print(f"\n   Primeros 10 permisos:")
        for i, perm in enumerate(permisos[:10], 1):
            print(f"      {i}. {perm}")
        
        # Verificar RBAC
        permisos_total = Permiso.objects.count()
        roles_total = Role.objects.count()
        
        print(f"\n✅ Sistema RBAC:")
        print(f"   • Permisos en BD: {permisos_total}")
        print(f"   • Roles en BD: {roles_total}")
        
        # Listar roles
        print(f"\n   Roles configurados:")
        for role in Role.objects.all():
            permisos_rol = RolPermiso.objects.filter(rol=role).count()
            print(f"      • {role.nombre}: {permisos_rol} permisos")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando sistema: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print_header("🚀 INICIALIZACIÓN COMPLETA DEL SISTEMA GYM SPARTAN")
    
    steps = [
        ("Verificar Base de Datos", check_database),
        ("Ejecutar Migraciones", run_migrations),
        ("Crear Superusuario", create_superuser),
        ("Configurar RBAC", setup_rbac),
        ("Asignar Rol Admin", assign_admin_role),
        ("Cargar Datos", seed_data),
        ("Verificar Sistema", verify_system),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
            
            if not result:
                print(f"\n⚠️  Error en: {step_name}")
                print("   Continuando con el siguiente paso...")
        except Exception as e:
            print(f"\n❌ Error inesperado en {step_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((step_name, False))
    
    # Resumen final
    print_header("📊 RESUMEN DE INICIALIZACIÓN")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for step_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {step_name}")
    
    print("\n" + "="*70)
    print(f"Exitosos: {success_count}/{total_count}")
    print("="*70)
    
    if success_count == total_count:
        print("\n🎉 ¡SISTEMA INICIALIZADO COMPLETAMENTE!")
        print("\n📝 Credenciales de acceso:")
        print("   URL: http://localhost:3000")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🔐 Otros usuarios de prueba:")
        print("   • gerente / gerente123")
        print("   • recepcionista / recep123")
    else:
        print("\n⚠️  Algunos pasos fallaron. Revisa los errores arriba.")


if __name__ == '__main__':
    main()
