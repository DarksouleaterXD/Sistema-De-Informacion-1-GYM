"""
Seeder para crear disciplinas de prueba en el gimnasio.
"""
from apps.disciplinas.models import Disciplina
from .base_seeder import BaseSeeder


class DisciplinasSeeder(BaseSeeder):
    """
    Crea disciplinas de prueba para el gimnasio
    """
    
    def seed(self):
        """
        Crea disciplinas de prueba
        """
        print("\n🏋️  Creando Disciplinas...")
        
        disciplinas_data = [
            {
                'nombre': 'Yoga',
                'descripcion': 'Clase de yoga para mejorar flexibilidad, equilibrio y reducir estrés. Apto para todos los niveles.',
                'activa': True
            },
            {
                'nombre': 'Spinning',
                'descripcion': 'Entrenamiento cardiovascular de alta intensidad en bicicleta estática. Quema calorías y mejora resistencia.',
                'activa': True
            },
            {
                'nombre': 'CrossFit',
                'descripcion': 'Entrenamiento funcional de alta intensidad que combina levantamiento de pesas, gimnasia y cardio.',
                'activa': True
            },
            {
                'nombre': 'Pilates',
                'descripcion': 'Método de entrenamiento físico que fortalece el core, mejora postura y flexibilidad.',
                'activa': True
            },
            {
                'nombre': 'Zumba',
                'descripcion': 'Ejercicio aeróbico que combina baile con música latina. Divertido y energético.',
                'activa': True
            },
            {
                'nombre': 'Boxeo',
                'descripcion': 'Entrenamiento de boxeo que incluye técnicas de golpeo, movimientos y acondicionamiento físico.',
                'activa': True
            },
            {
                'nombre': 'Funcional',
                'descripcion': 'Entrenamiento que utiliza movimientos naturales del cuerpo para mejorar fuerza y resistencia.',
                'activa': True
            },
            {
                'nombre': 'GAP',
                'descripcion': 'Entrenamiento enfocado en Glúteos, Abdomen y Piernas. Tonifica y fortalece el tren inferior.',
                'activa': True
            },
            {
                'nombre': 'TRX',
                'descripcion': 'Entrenamiento en suspensión que utiliza el peso corporal para desarrollar fuerza y estabilidad.',
                'activa': True
            },
            {
                'nombre': 'Natación',
                'descripcion': 'Clases de natación para todos los niveles. Ejercicio de bajo impacto y alto rendimiento.',
                'activa': False
            },
        ]
        
        for data in disciplinas_data:
            disciplina, is_created = Disciplina.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    'descripcion': data['descripcion'],
                    'activa': data['activa']
                }
            )
            
            if is_created:
                print(f"   ✅ Disciplina creada: {disciplina.nombre}")
                self.created_count += 1
            else:
                disciplina.descripcion = data['descripcion']
                disciplina.activa = data['activa']
                disciplina.save()
                print(f"   ⚠️  Disciplina ya existe: {disciplina.nombre}")
                self.updated_count += 1
