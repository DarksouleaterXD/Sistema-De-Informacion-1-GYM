"""
Seeder para crear el superusuario del sistema
"""
from django.contrib.auth import get_user_model
from .base_seeder import BaseSeeder

User = get_user_model()


class SuperUserSeeder(BaseSeeder):
    """
    Crea el superusuario principal del sistema
    """
    
    def seed(self):
        """
        Crea el superusuario si no existe
        """
        print("\n🔐 Creando Superusuario...")
        
        # Datos del superusuario
        superuser_data = {
            'email': 'admin@gym-spartan.com',
            'username': 'admin',
            'first_name': 'Super',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
        
        # Verificar si el superusuario ya existe
        if User.objects.filter(email=superuser_data['email']).exists():
            print(f"⚠️  El superusuario ya existe: {superuser_data['email']}")
            self.updated_count += 1
        else:
            # Crear superusuario
            user = User.objects.create_user(
                email=superuser_data['email'],
                username=superuser_data['username'],
                password='admin123',  # Cambiar en producción
                first_name=superuser_data['first_name'],
                last_name=superuser_data['last_name'],
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            print(f"✅ Superusuario creado exitosamente")
            print(f"   Email: {superuser_data['email']}")
            print(f"   Password: admin123")
            print(f"   ⚠️  Cambiar la contraseña en producción")
            
            self.created_count += 1
