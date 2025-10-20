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
            rol_gerente = Role.objects.get(nombre='Gerente')
            rol_recepcionista = Role.objects.get(nombre='Recepcionista')
            rol_entrenador = Role.objects.get(nombre='Entrenador')
        except Role.DoesNotExist:
            print("⚠️  Primero debes ejecutar el seeder de roles")
            return
        
        # Usuarios de prueba
        usuarios_data = [
            {
                'email': 'gerente@gym-spartan.com',
                'username': 'gerente1',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'password': 'gerente123',
                'roles': [rol_gerente]
            },
            {
                'email': 'recepcion@gym-spartan.com',
                'username': 'recepcion1',
                'first_name': 'María',
                'last_name': 'González',
                'password': 'recepcion123',
                'roles': [rol_recepcionista]
            },
            {
                'email': 'entrenador@gym-spartan.com',
                'username': 'entrenador1',
                'first_name': 'Carlos',
                'last_name': 'López',
                'password': 'entrenador123',
                'roles': [rol_entrenador]
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
                user.is_staff = True
                user.roles.set(roles)
                user.save()
                
                print(f"   ✅ Usuario creado: {user_data['email']}")
                print(f"      Password: {password}")
                self.created_count += 1
