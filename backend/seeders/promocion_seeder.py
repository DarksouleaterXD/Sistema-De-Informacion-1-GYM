"""
Seeder para crear promociones iniciales
"""
import sys
import os
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.promociones.models import Promocion
from .base_seeder import BaseSeeder


class PromocionSeeder(BaseSeeder):
    def seed(self):
        """Crear promociones predefinidas"""
        hoy = date.today()
        
        promociones = [
            {
                'nombre': 'Promoción Año Nuevo',
                'meses': 1,
                'descuento': 15.00,
                'fecha_inicio': date(2025, 1, 1),
                'fecha_fin': date(2025, 1, 31),
                'estado': 'ACTIVA'
            },
            {
                'nombre': 'Promoción Verano',
                'meses': 3,
                'descuento': 20.00,
                'fecha_inicio': date(2025, 1, 1),
                'fecha_fin': date(2025, 3, 31),
                'estado': 'ACTIVA'
            },
            {
                'nombre': 'Black Friday Gym',
                'meses': 6,
                'descuento': 30.00,
                'fecha_inicio': hoy,
                'fecha_fin': hoy + timedelta(days=60),
                'estado': 'ACTIVA'
            },
            {
                'nombre': 'Estudiantes',
                'meses': 1,
                'descuento': 10.00,
                'fecha_inicio': hoy,
                'fecha_fin': hoy + timedelta(days=365),
                'estado': 'ACTIVA'
            },
            {
                'nombre': 'Referido',
                'meses': 1,
                'descuento': 25.00,
                'fecha_inicio': hoy,
                'fecha_fin': hoy + timedelta(days=365),
                'estado': 'ACTIVA'
            },
        ]
        
        for promo_data in promociones:
            promo, created = Promocion.objects.get_or_create(
                nombre=promo_data['nombre'],
                defaults=promo_data
            )
            
            if created:
                self.created_count += 1
                print(f"   ✅ Promoción creada: {promo.nombre} ({promo.descuento}% descuento)")
            else:
                self.updated_count += 1
                print(f"   ℹ️  Promoción ya existe: {promo.nombre}")


if __name__ == '__main__':
    seeder = PromocionSeeder()
    seeder.run()
