"""
Seeder para crear usuarios de prueba
"""
from django.contrib.auth import get_user_model
from apps.roles.models import Role
from .base_seeder import BaseSeeder

User = get_user_model()


class UsersSeeder(BaseSeeder):
    """
    Crea usuarios de prueba para el sistema
    """
    
    def seed(self):
        """
        Crea usuarios de prueba
        """
        print("\n👤 Creando Usuarios de Prueba...")
        
        # Obtener roles
        try:
            rol_administrativo = Role.objects.get(nombre='Administrativo')
            rol_instructor = Role.objects.get(nombre='Instructor')
        except Role.DoesNotExist as e:
            print(f"⚠️  Error: No se encontró el rol - {e}")
            print("   Primero debes ejecutar el seeder de roles")
            return
        
        # Usuarios de prueba
        usuarios_data = [
            {
                'email': 'administrativo@gym-spartan.com',
                'username': 'administrativo1',
                'first_name': 'María',
                'last_name': 'González',
                'password': 'admin123',
                'roles': [rol_administrativo]
            },
            {
                'email': 'instructor@gym-spartan.com',
                'username': 'instructor1',
                'first_name': 'Carlos',
                'last_name': 'López',
                'password': 'instructor123',
                'roles': [rol_instructor]
            },
            {
                'email': 'instructor2@gym-spartan.com',
                'username': 'instructor2',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'password': 'instructor123',
                'roles': [rol_instructor]
            },
        ]
        
        # Crear usuarios
        for user_data in usuarios_data:
            if User.objects.filter(email=user_data['email']).exists():
                print(f"   ⚠️  Usuario ya existe: {user_data['email']}")
                self.updated_count += 1
            else:
                roles = user_data.pop('roles')
                password = user_data.pop('password')
                
                user = User.objects.create_user(
                    password=password,
                    **user_data
                )
                
                # Asignar roles usando UserRole
                from apps.roles.models import UserRole
                for role in roles:
                    UserRole.objects.create(usuario=user, rol=role)
                
                print(f"   ✅ Usuario creado: {user_data['email']}")
                print(f"      Username: {user.username}")
                print(f"      Password: {password}")
                print(f"      Rol(es): {', '.join([r.nombre for r in roles])}")
                self.created_count += 1
