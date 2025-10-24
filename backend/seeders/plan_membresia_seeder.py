"""
Seeder para crear planes de membresía iniciales
"""
import sys
import os
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.membresias.models import PlanMembresia
from .base_seeder import BaseSeeder


class PlanMembresiaSeeder(BaseSeeder):
    def seed(self):
        """Crear planes de membresía predefinidos"""
        planes = [
            {
                'nombre': 'Plan Diario',
                'duracion': 1,
                'precio_base': 15.00,
                'descripcion': 'Acceso por un día completo al gimnasio'
            },
            {
                'nombre': 'Plan Semanal',
                'duracion': 7,
                'precio_base': 80.00,
                'descripcion': 'Acceso por una semana completa'
            },
            {
                'nombre': 'Plan Quincenal',
                'duracion': 15,
                'precio_base': 140.00,
                'descripcion': 'Acceso por 15 días'
            },
            {
                'nombre': 'Plan Mensual',
                'duracion': 30,
                'precio_base': 250.00,
                'descripcion': 'Acceso completo por 30 días. El más popular'
            },
            {
                'nombre': 'Plan Trimestral',
                'duracion': 90,
                'precio_base': 650.00,
                'descripcion': 'Acceso por 3 meses con descuento incluido'
            },
            {
                'nombre': 'Plan Semestral',
                'duracion': 180,
                'precio_base': 1200.00,
                'descripcion': 'Acceso por 6 meses con mayor descuento'
            },
            {
                'nombre': 'Plan Anual',
                'duracion': 365,
                'precio_base': 2200.00,
                'descripcion': 'Acceso por todo el año con el mejor precio'
            },
        ]
        
        for plan_data in planes:
            plan, created = PlanMembresia.objects.get_or_create(
                nombre=plan_data['nombre'],
                defaults={
                    'duracion': plan_data['duracion'],
                    'precio_base': plan_data['precio_base'],
                    'descripcion': plan_data['descripcion']
                }
            )
            
            if created:
                self.created_count += 1
                print(f"   ✅ Plan creado: {plan.nombre}")
            else:
                self.updated_count += 1
                print(f"   ℹ️  Plan ya existe: {plan.nombre}")


if __name__ == '__main__':
    seeder = PlanMembresiaSeeder()
    seeder.run()
