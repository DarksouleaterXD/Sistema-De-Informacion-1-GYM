"""
Script para ejecutar todos los seeders en orden
"""
from .superuser_seeder import SuperUserSeeder
from .permissions_seeder import PermissionSeeder
from .roles_default_seeder import create_default_roles  # 🔥 Usar el nuevo seeder de roles
from .users_seeder import UsersSeeder
from .clients_seeder import ClientsSeeder
from .plan_membresia_seeder import PlanMembresiaSeeder
from .promocion_seeder import PromocionSeeder
from .disciplinas_seeder import DisciplinasSeeder
from .salones_clases_seeder import SalonSeeder, ClaseSeeder
from .instructores_seeder import InstructorSeeder
from .categorias_seeder import CategoriasSeeder
from .productos_seeder import ProductosSeeder


class RolesDefaultSeederWrapper:
    """Wrapper para el seeder de roles que usa la función create_default_roles"""
    def run(self):
        try:
            create_default_roles()
            return True
        except Exception as e:
            print(f"❌ Error al ejecutar seeder: {e}")
            return False


def run_all_seeders():
    """
    Ejecuta todos los seeders en el orden correcto
    """
    print("\n" + "="*60)
    print("🌱 INICIANDO SEEDERS DEL SISTEMA")
    print("="*60)
    
    seeders = [
        SuperUserSeeder(),
        PermissionSeeder(),  # 🔥 PRIMERO: Crear permisos
        RolesDefaultSeederWrapper(),  # LUEGO: Crear roles y asignar permisos
        UsersSeeder(),
        InstructorSeeder(),  # 🔥 NUEVO: Crear instructores
        ClientsSeeder(),
        PlanMembresiaSeeder(),
        PromocionSeeder(),
        DisciplinasSeeder(),  # 🔥 NUEVO: Crear disciplinas
        SalonSeeder(),  # 🔥 NUEVO: Crear salones
        ClaseSeeder(),  # 🔥 NUEVO: Crear clases de prueba
        CategoriasSeeder(),  # 🔥 CU24: Crear categorías de productos
        ProductosSeeder(),  # 🔥 CU24: Crear productos (requiere categorías)
    ]
    
    success_count = 0
    error_count = 0
    
    for i, seeder in enumerate(seeders, 1):
        seeder_name = seeder.__class__.__name__
        try:
            if seeder.run():
                success_count += 1
            else:
                print(f"\n⚠️  Seeder #{i} ({seeder_name}) retornó False")
                error_count += 1
        except Exception as e:
            print(f"\n❌ Error en Seeder #{i} ({seeder_name}): {e}")
            error_count += 1
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"✅ Seeders exitosos: {success_count}")
    print(f"❌ Seeders fallidos: {error_count}")
    print("="*60 + "\n")
    
    if error_count == 0:
        print("🎉 ¡Todos los seeders se ejecutaron exitosamente!")
    else:
        print("⚠️  Algunos seeders fallaron. Revisa los errores arriba.")
