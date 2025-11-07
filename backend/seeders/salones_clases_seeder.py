"""
Seeder para crear salones y clases de prueba.
"""
from django.contrib.auth import get_user_model
from apps.clases.models import Salon, Clase
from apps.disciplinas.models import Disciplina
from apps.core.constants import CLASE_PROGRAMADA
from .base_seeder import BaseSeeder
from datetime import date, time, timedelta

User = get_user_model()


class SalonSeeder(BaseSeeder):
    """
    Crea salones de prueba para el gimnasio
    """
    
    def seed(self):
        """
        Crea salones de prueba
        """
        print("\n🏢 Creando Salones...")
        
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
                print(f"   ✅ Salón creado: {salon.nombre} (Capacidad: {salon.capacidad})")
                self.created_count += 1
            else:
                # Actualizar datos si ya existe
                salon.capacidad = data['capacidad']
                salon.descripcion = data['descripcion']
                salon.activo = data['activo']
                salon.save()
                print(f"   ⚠️  Salón ya existe: {salon.nombre}")
                self.updated_count += 1


class ClaseSeeder(BaseSeeder):
    """
    Crea clases de prueba para el gimnasio
    """
    
    def seed(self):
        """
        Crea clases de prueba
        """
        print("\n📅 Creando Clases de Prueba...")
        
        # Buscar instructor
        try:
            instructor = User.objects.filter(
                userrole__rol__nombre='Instructor'
            ).first()
            
            if not instructor:
                instructor = User.objects.filter(is_active=True).first()
                
            if not instructor:
                print("   ⚠️  No hay usuarios disponibles para asignar como instructores")
                return
        except Exception as e:
            print(f"   ⚠️  Error al buscar instructor: {e}")
            return
        
        # Obtener disciplinas activas
        disciplinas = list(Disciplina.objects.filter(activa=True)[:5])
        
        if not disciplinas:
            print("   ⚠️  No hay disciplinas activas disponibles")
            return
        
        # Obtener salones
        salones = list(Salon.objects.filter(activo=True))
        
        if not salones:
            print("   ⚠️  No hay salones activos disponibles")
            return
        
        # Programar clases para la próxima semana
        clases_data = [
            {
                'disciplina': disciplinas[0],
                'salon': salones[2] if len(salones) > 2 else salones[0],
                'fecha': date.today() + timedelta(days=1),
                'hora_inicio': time(7, 0),
                'hora_fin': time(8, 0),
            },
            {
                'disciplina': disciplinas[1] if len(disciplinas) > 1 else disciplinas[0],
                'salon': salones[1] if len(salones) > 1 else salones[0],
                'fecha': date.today() + timedelta(days=1),
                'hora_inicio': time(18, 0),
                'hora_fin': time(19, 0),
            },
            {
                'disciplina': disciplinas[2] if len(disciplinas) > 2 else disciplinas[0],
                'salon': salones[3] if len(salones) > 3 else salones[0],
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
                    estado=CLASE_PROGRAMADA
                )
                print(f"   ✅ Clase creada: {clase.disciplina.nombre} - {clase.fecha} {clase.hora_inicio} ({clase.salon.nombre})")
                self.created_count += 1
            else:
                print(f"   ⚠️  Ya existe clase en {data['salon'].nombre} el {data['fecha']} a las {data['hora_inicio']}")
                self.updated_count += 1
        
        if self.created_count > 0:
            print(f"   💡 Instructor asignado: {instructor.get_full_name()}")
