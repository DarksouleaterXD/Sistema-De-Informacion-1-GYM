"""
Seeder para crear instructores de prueba
"""
from django.contrib.auth import get_user_model
from apps.instructores.models import Instructor
from apps.roles.models import Role, UserRole
from datetime import date
from .base_seeder import BaseSeeder

User = get_user_model()


class InstructorSeeder(BaseSeeder):
    """Crea instructores de prueba en el sistema"""
    
    def seed(self):
        """Ejecuta el seeder"""
        print("\n👨‍🏫 Creando instructores de prueba...")
        
        # Obtener o crear el rol de Instructor
        instructor_role, _ = Role.objects.get_or_create(
            nombre="Instructor",
            defaults={
                "descripcion": "Instructor de clases del gimnasio",
                "activo": True
            }
        )
        
        # Datos de instructores de prueba
        instructores_data = [
            {
                "username": "jperez_instructor",
                "email": "jperez@gym-spartan.com",
                "password": "instructor123",
                "first_name": "Juan",
                "last_name": "Pérez",
                "perfil": {
                    "especialidades": "CrossFit, Functional Training, HIIT",
                    "certificaciones": "Certified CrossFit Trainer (L1), Functional Movement Screen",
                    "experiencia_anos": 5,
                    "telefono": "71234567",
                    "biografia": "Entrenador certificado con 5 años de experiencia en CrossFit y entrenamiento funcional.",
                    "foto_url": "https://i.pravatar.cc/300?img=12",
                    "fecha_ingreso": date(2020, 1, 15)
                }
            },
            {
                "username": "mgarcia_instructor",
                "email": "mgarcia@gym-spartan.com",
                "password": "instructor123",
                "first_name": "María",
                "last_name": "García",
                "perfil": {
                    "especialidades": "Yoga, Pilates, Stretching",
                    "certificaciones": "200hr Yoga Alliance RYT, Pilates Mat Certification",
                    "experiencia_anos": 8,
                    "telefono": "72345678",
                    "biografia": "Instructora de Yoga y Pilates con más de 8 años enseñando bienestar integral.",
                    "foto_url": "https://i.pravatar.cc/300?img=47",
                    "fecha_ingreso": date(2018, 6, 10)
                }
            },
            {
                "username": "clopez_instructor",
                "email": "clopez@gym-spartan.com",
                "password": "instructor123",
                "first_name": "Carlos",
                "last_name": "López",
                "perfil": {
                    "especialidades": "Spinning, Cardio, HIIT",
                    "certificaciones": "Spinning Instructor Certification, CPR/AED",
                    "experiencia_anos": 3,
                    "telefono": "73456789",
                    "biografia": "Especialista en clases de alta intensidad y ciclismo indoor.",
                    "foto_url": "https://i.pravatar.cc/300?img=33",
                    "fecha_ingreso": date(2022, 3, 20)
                }
            },
            {
                "username": "amartinez_instructor",
                "email": "amartinez@gym-spartan.com",
                "password": "instructor123",
                "first_name": "Ana",
                "last_name": "Martínez",
                "perfil": {
                    "especialidades": "Zumba, Dance Fitness, Aerobics",
                    "certificaciones": "Zumba Basic 1 & 2, Dance Fitness Instructor",
                    "experiencia_anos": 4,
                    "telefono": "74567890",
                    "biografia": "Instructora energética especializada en clases de baile y fitness cardiovascular.",
                    "foto_url": "https://i.pravatar.cc/300?img=45",
                    "fecha_ingreso": date(2021, 9, 5)
                }
            },
            {
                "username": "rsanchez_instructor",
                "email": "rsanchez@gym-spartan.com",
                "password": "instructor123",
                "first_name": "Roberto",
                "last_name": "Sánchez",
                "perfil": {
                    "especialidades": "Musculación, Powerlifting, Strength Training",
                    "certificaciones": "NSCA-CPT, USA Powerlifting Coach",
                    "experiencia_anos": 10,
                    "telefono": "75678901",
                    "biografia": "Entrenador de fuerza con 10 años de experiencia en powerlifting y musculación avanzada.",
                    "foto_url": "https://i.pravatar.cc/300?img=51",
                    "fecha_ingreso": date(2015, 11, 1)
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for data in instructores_data:
            try:
                # Verificar si el usuario ya existe
                user = User.objects.filter(email=data['email']).first()
                
                if not user:
                    # Crear usuario
                    user = User.objects.create_user(
                        username=data['username'],
                        email=data['email'],
                        password=data['password'],
                        first_name=data['first_name'],
                        last_name=data['last_name']
                    )
                    print(f"   ✅ Usuario creado: {user.email}")
                else:
                    print(f"   ⚠️  Usuario ya existe: {user.email}")
                
                # Asignar rol de Instructor si no lo tiene
                user_role, created = UserRole.objects.get_or_create(
                    usuario=user,
                    rol=instructor_role
                )
                
                if created:
                    print(f"   ✅ Rol 'Instructor' asignado a {user.email}")
                
                # Verificar si ya tiene perfil de instructor
                instructor = Instructor.objects.filter(usuario=user).first()
                
                if not instructor:
                    # Crear perfil de instructor
                    instructor = Instructor.objects.create(
                        usuario=user,
                        especialidades=data['perfil']['especialidades'],
                        certificaciones=data['perfil']['certificaciones'],
                        experiencia_anos=data['perfil']['experiencia_anos'],
                        telefono=data['perfil']['telefono'],
                        biografia=data['perfil']['biografia'],
                        foto_url=data['perfil']['foto_url'],
                        fecha_ingreso=data['perfil']['fecha_ingreso'],
                        activo=True
                    )
                    created_count += 1
                    self.created_count += 1
                    print(f"   ✅ Instructor creado: {user.get_full_name()}")
                else:
                    # Actualizar perfil existente
                    instructor.especialidades = data['perfil']['especialidades']
                    instructor.certificaciones = data['perfil']['certificaciones']
                    instructor.experiencia_anos = data['perfil']['experiencia_anos']
                    instructor.telefono = data['perfil']['telefono']
                    instructor.biografia = data['perfil']['biografia']
                    instructor.foto_url = data['perfil']['foto_url']
                    instructor.fecha_ingreso = data['perfil']['fecha_ingreso']
                    instructor.save()
                    updated_count += 1
                    self.updated_count += 1
                    print(f"   📝 Instructor actualizado: {user.get_full_name()}")
                    
            except Exception as e:
                self.error_count += 1
                print(f"   ❌ Error al crear instructor {data['email']}: {str(e)}")
        
        # Resumen
        print(f"\n📊 Resumen:")
        print(f"   ✅ Instructores creados: {created_count}")
        print(f"   📝 Instructores actualizados: {updated_count}")
        print(f"   📈 Total en base de datos: {Instructor.objects.count()}")


def run():
    """Función para ejecutar el seeder"""
    seeder = InstructorSeeder()
    seeder.run()


if __name__ == "__main__":
    run()
