"""
Seeder para crear salones y clases de prueba.
"""

import sys
import os
import django
from datetime import date, time, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clases.models import Salon, Clase
from apps.disciplinas.models import Disciplina
from apps.users.models import User


def run():
    """Ejecuta el seeder de salones y clases."""
    print("🏢 Creando salones de prueba...\n")
    
    salones_data = [
        {
            'nombre': 'Sala Principal',
            'capacidad': 30,
            'descripcion': 'Sala amplia para clases grupales grandes',
            'activo': True
        },
        {
            'nombre': 'Sala Spinning',
            'capacidad': 20,
            'descripcion': 'Sala especializada para clases de spinning con bicicletas estáticas',
            'activo': True
        },
        {
            'nombre': 'Sala Yoga',
            'capacidad': 15,
            'descripcion': 'Sala tranquila con piso acolchado para yoga y pilates',
            'activo': True
        },
        {
            'nombre': 'Box CrossFit',
            'capacidad': 25,
            'descripcion': 'Área equipada para entrenamiento funcional y CrossFit',
            'activo': True
        },
        {
            'nombre': 'Sala Multiusos',
            'capacidad': 20,
            'descripcion': 'Sala versátil para diferentes tipos de clases',
            'activo': True
        },
    ]
    
    salones_creados = 0
    salones_actualizados = 0
    
    for data in salones_data:
        salon, is_created = Salon.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'capacidad': data['capacidad'],
                'descripcion': data['descripcion'],
                'activo': data['activo']
            }
        )
        
        if is_created:
            print(f"  ✅ Creado: {salon.nombre} (Cap: {salon.capacidad})")
            salones_creados += 1
        else:
            salon.capacidad = data['capacidad']
            salon.descripcion = data['descripcion']
            salon.activo = data['activo']
            salon.save()
            print(f"  ♻️  Actualizado: {salon.nombre}")
            salones_actualizados += 1
    
    print(f"\n✅ Salones completados:")
    print(f"  - {salones_creados} salones creados")
    print(f"  - {salones_actualizados} salones actualizados\n")
    
    # Crear clases de prueba si hay instructores y disciplinas
    print("📅 Creando clases de prueba...\n")
    
    # Buscar instructores (usuarios con rol de instructor)
    try:
        instructor = User.objects.filter(
            roles__nombre='Instructor'
        ).first()
        
        if not instructor:
            # Buscar cualquier usuario activo como fallback
            instructor = User.objects.filter(is_active=True).first()
            
        if not instructor:
            print("  ⚠️  No hay usuarios disponibles para asignar como instructores")
            return
    except Exception as e:
        print(f"  ⚠️  Error al buscar instructor: {e}")
        return
    
    # Obtener disciplinas activas
    disciplinas = Disciplina.objects.filter(activa=True)[:5]
    
    if not disciplinas.exists():
        print("  ⚠️  No hay disciplinas activas disponibles")
        return
    
    # Obtener salones
    salones = Salon.objects.filter(activo=True)
    
    if not salones.exists():
        print("  ⚠️  No hay salones activos disponibles")
        return
    
    # Programar clases para la próxima semana
    clases_data = [
        {
            'disciplina': disciplinas[0],  # Yoga
            'salon': salones[2] if len(salones) > 2 else salones[0],  # Sala Yoga
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': time(7, 0),
            'hora_fin': time(8, 0),
        },
        {
            'disciplina': disciplinas[1] if len(disciplinas) > 1 else disciplinas[0],  # Spinning
            'salon': salones[1] if len(salones) > 1 else salones[0],  # Sala Spinning
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': time(18, 0),
            'hora_fin': time(19, 0),
        },
        {
            'disciplina': disciplinas[2] if len(disciplinas) > 2 else disciplinas[0],  # CrossFit
            'salon': salones[3] if len(salones) > 3 else salones[0],  # Box CrossFit
            'fecha': date.today() + timedelta(days=2),
            'hora_inicio': time(17, 0),
            'hora_fin': time(18, 30),
        },
        {
            'disciplina': disciplinas[0],
            'salon': salones[0],
            'fecha': date.today() + timedelta(days=3),
            'hora_inicio': time(9, 0),
            'hora_fin': time(10, 0),
        },
        {
            'disciplina': disciplinas[1] if len(disciplinas) > 1 else disciplinas[0],
            'salon': salones[1] if len(salones) > 1 else salones[0],
            'fecha': date.today() + timedelta(days=4),
            'hora_inicio': time(19, 0),
            'hora_fin': time(20, 0),
        },
    ]
    
    clases_creadas = 0
    
    for data in clases_data:
        # Verificar si ya existe una clase en ese horario y salón
        existe = Clase.objects.filter(
            salon=data['salon'],
            fecha=data['fecha'],
            hora_inicio=data['hora_inicio']
        ).exists()
        
        if not existe:
            clase = Clase.objects.create(
                disciplina=data['disciplina'],
                instructor=instructor,
                salon=data['salon'],
                fecha=data['fecha'],
                hora_inicio=data['hora_inicio'],
                hora_fin=data['hora_fin'],
                cupo_maximo=data['salon'].capacidad,
                estado='programada'
            )
            print(f"  ✅ Creada: {clase.disciplina.nombre} - {clase.fecha} {clase.hora_inicio} ({clase.salon.nombre})")
            clases_creadas += 1
        else:
            print(f"  ⚠️  Ya existe clase en {data['salon'].nombre} el {data['fecha']} a las {data['hora_inicio']}")
    
    print(f"\n✅ Clases completadas:")
    print(f"  - {clases_creadas} clases creadas")
    print(f"  - Instructor asignado: {instructor.get_full_name()}\n")


if __name__ == '__main__':
    run()
