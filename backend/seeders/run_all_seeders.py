"""
Script para ejecutar todos los seeders en orden
"""
from .superuser_seeder import SuperUserSeeder
from .roles_seeder import RolesSeeder
from .users_seeder import UsersSeeder
from .clients_seeder import ClientsSeeder
from .plan_membresia_seeder import PlanMembresiaSeeder
from .promocion_seeder import PromocionSeeder


def run_all_seeders():
    """
    Ejecuta todos los seeders en el orden correcto
    """
    print("\n" + "="*60)
    print("🌱 INICIANDO SEEDERS DEL SISTEMA")
    print("="*60)
    
    seeders = [
        SuperUserSeeder(),
        RolesSeeder(),
        UsersSeeder(),
        ClientsSeeder(),
        PlanMembresiaSeeder(),
        PromocionSeeder(),
    ]
    
    success_count = 0
    error_count = 0
    
    for seeder in seeders:
        if seeder.run():
            success_count += 1
        else:
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
