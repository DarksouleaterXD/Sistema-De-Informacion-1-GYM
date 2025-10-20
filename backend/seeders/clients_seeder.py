"""
Seeder para crear clientes de prueba
"""
from apps.clients.models import Client, InscripcionMembresia
from .base_seeder import BaseSeeder


class ClientsSeeder(BaseSeeder):
    """
    Crea clientes de prueba
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
                'telefono': '70111111',
                'peso': 75.5,
                'altura': 1.75,
                'experiencia': 'Principiante',
                'monto_inscripcion': 250.00
            },
            {
                'nombre': 'Ana',
                'apellido': 'Martínez',
                'telefono': '70222222',
                'peso': 60.0,
                'altura': 1.65,
                'experiencia': 'Avanzado',
                'monto_inscripcion': 1500.00
            },
            {
                'nombre': 'Luis',
                'apellido': 'Flores',
                'telefono': '70333333',
                'peso': 80.0,
                'altura': 1.80,
                'experiencia': 'Intermedio',
                'monto_inscripcion': 150.00
            },
            {
                'nombre': 'Sofia',
                'apellido': 'Vargas',
                'telefono': '70444444',
                'peso': 55.0,
                'altura': 1.60,
                'experiencia': 'Principiante',
                'monto_inscripcion': 400.00
            },
        ]
        
        # Crear clientes e inscripciones
        for cliente_data in clientes_data:
            monto_inscripcion = cliente_data.pop('monto_inscripcion')
            
            if Client.objects.filter(telefono=cliente_data['telefono']).exists():
                print(f"   ⚠️  Cliente ya existe: {cliente_data['telefono']}")
                self.updated_count += 1
            else:
                cliente = Client.objects.create(**cliente_data)
                
                # Crear inscripción a membresía
                InscripcionMembresia.objects.create(
                    cliente=cliente,
                    monto=monto_inscripcion,
                    metodo_de_pago='Efectivo'
                )
                
                print(f"   ✅ Cliente creado: {cliente_data['nombre']} {cliente_data['apellido']}")
                self.created_count += 1
