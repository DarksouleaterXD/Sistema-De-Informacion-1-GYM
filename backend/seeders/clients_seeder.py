"""
Seeder para crear clientes de prueba
"""
from apps.clients.models import Client
from .base_seeder import BaseSeeder
import random


class ClientsSeeder(BaseSeeder):
    """
    Crea clientes de prueba con información completa
    """
    
    def seed(self):
        """
        Crea datos de prueba para clientes
        """
        print("\n🏋️ Creando Clientes...")
        
        # Crear clientes de prueba
        clientes_data = [
            {
                'nombre': 'Pedro',
                'apellido': 'Ramírez',
                'ci': '12345678',
                'telefono': '70111111',
                'email': 'pedro.ramirez@gmail.com',
                'peso': 75.5,
                'altura': 1.75,
                'experiencia': 'INTERMEDIO'
            },
            {
                'nombre': 'Ana',
                'apellido': 'Martínez',
                'ci': '87654321',
                'telefono': '70222222',
                'email': 'ana.martinez@gmail.com',
                'peso': 62.0,
                'altura': 1.65,
                'experiencia': 'PRINCIPIANTE'
            },
            {
                'nombre': 'Luis',
                'apellido': 'Flores',
                'ci': '11223344',
                'telefono': '70333333',
                'email': 'luis.flores@gmail.com',
                'peso': 82.3,
                'altura': 1.80,
                'experiencia': 'AVANZADO'
            },
            {
                'nombre': 'Sofia',
                'apellido': 'Vargas',
                'ci': '55667788',
                'telefono': '70444444',
                'email': 'sofia.vargas@gmail.com',
                'peso': 58.5,
                'altura': 1.62,
                'experiencia': 'INTERMEDIO'
            },
            {
                'nombre': 'Brandon',
                'apellido': 'Cusicanqui',
                'ci': '123145',
                'telefono': '78912341',
                'email': 'brason@gmail.com',
                'peso': 70.0,
                'altura': 1.72,
                'experiencia': 'PRINCIPIANTE'
            },
        ]
        
        # Crear clientes
        for cliente_data in clientes_data:
            if Client.objects.filter(ci=cliente_data['ci']).exists():
                print(f"   ⚠️  Cliente ya existe: {cliente_data['ci']}")
                self.updated_count += 1
            else:
                cliente = Client.objects.create(**cliente_data)
                print(f"   ✅ Cliente creado: {cliente_data['nombre']} {cliente_data['apellido']} ({cliente_data['experiencia']})")
                self.created_count += 1
