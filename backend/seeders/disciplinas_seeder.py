"""
Seeder para crear disciplinas de prueba en el gimnasio.
"""

import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.disciplinas.models import Disciplina


def run():
    """Ejecuta el seeder de disciplinas."""
    print("🏋️  Creando disciplinas de prueba...\n")
    
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
            'activa': False  # Inactiva - piscina en mantenimiento
        },
    ]
    
    created = 0
    updated = 0
    
    for data in disciplinas_data:
        disciplina, is_created = Disciplina.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'descripcion': data['descripcion'],
                'activa': data['activa']
            }
        )
        
        if is_created:
            print(f"  ✅ Creada: {disciplina.nombre}")
            created += 1
        else:
            # Actualizar si ya existe
            disciplina.descripcion = data['descripcion']
            disciplina.activa = data['activa']
            disciplina.save()
            print(f"  ♻️  Actualizada: {disciplina.nombre}")
            updated += 1
    
    print(f"\n✅ Seeder completado:")
    print(f"  - {created} disciplinas creadas")
    print(f"  - {updated} disciplinas actualizadas")
    print(f"  - {created + updated} disciplinas totales\n")


if __name__ == '__main__':
    run()
