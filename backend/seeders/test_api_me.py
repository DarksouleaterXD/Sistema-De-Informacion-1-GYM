"""
Script para probar el endpoint /api/users/me/ y verificar que retorna permisos.

Uso:
    python seeders/test_api_me.py
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.users.views import CurrentUserView
from apps.users.models import User
from rest_framework.test import force_authenticate


def test_current_user_endpoint():
    """Prueba el endpoint CurrentUserView."""
    
    print("\n" + "=" * 70)
    print("🧪 PRUEBA DEL ENDPOINT /api/users/me/")
    print("=" * 70)
    
    try:
        # Obtener usuario admin
        admin = User.objects.get(username='admin')
        print(f"\n✅ Usuario de prueba: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Superuser: {admin.is_superuser}")
        
        # Crear request factory
        factory = RequestFactory()
        
        # Crear request GET simulado
        request = factory.get('/api/users/me/')
        force_authenticate(request, user=admin)
        
        # Crear vista y ejecutar
        view = CurrentUserView.as_view()
        response = view(request)
        
        print(f"\n📊 RESPUESTA DEL ENDPOINT")
        print("-" * 70)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            
            print(f"\n   ✅ Datos del usuario:")
            print(f"      • ID: {data.get('id')}")
            print(f"      • Username: {data.get('username')}")
            print(f"      • Email: {data.get('email')}")
            print(f"      • Nombre: {data.get('nombre')} {data.get('apellido')}")
            print(f"      • Is Superuser: {data.get('is_superuser')}")
            
            # Verificar permisos
            permissions = data.get('permissions', [])
            print(f"\n   ✅ Permisos retornados: {len(permissions)}")
            
            if len(permissions) > 0:
                print(f"\n      Primeros 10 permisos:")
                for perm in permissions[:10]:
                    print(f"         • {perm}")
                if len(permissions) > 10:
                    print(f"         ... y {len(permissions) - 10} más")
            else:
                print(f"      ⚠️  No se retornaron permisos")
            
            # Verificar roles
            roles = data.get('roles', [])
            print(f"\n   ✅ Roles retornados: {len(roles)}")
            
            if len(roles) > 0:
                for role in roles:
                    print(f"      • {role.get('nombre')} (ID: {role.get('id')})")
                    print(f"        Descripción: {role.get('descripcion')}")
            else:
                print(f"      ⚠️  No se retornaron roles")
            
            # Resumen
            print("\n" + "=" * 70)
            print("📋 RESUMEN DE LA PRUEBA")
            print("=" * 70)
            
            checks = [
                (response.status_code == 200, "Endpoint responde correctamente"),
                ('permissions' in data, "Campo 'permissions' presente"),
                ('roles' in data, "Campo 'roles' presente"),
                ('is_superuser' in data, "Campo 'is_superuser' presente"),
                (len(permissions) > 0, f"Permisos retornados ({len(permissions)})"),
                (len(roles) > 0, f"Roles retornados ({len(roles)})"),
            ]
            
            all_passed = True
            for passed, description in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {description}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("\n" + "=" * 70)
                print("✅ TODAS LAS PRUEBAS PASARON")
                print("=" * 70)
                print("\n💡 El endpoint está funcionando correctamente")
                print("   El frontend debería recibir los permisos sin problemas")
            else:
                print("\n" + "=" * 70)
                print("⚠️  ALGUNAS PRUEBAS FALLARON")
                print("=" * 70)
            
        else:
            print(f"\n   ❌ ERROR: Status code {response.status_code}")
            print(f"   Respuesta: {response.data}")
        
        print("\n" + "=" * 70 + "\n")
        
    except User.DoesNotExist:
        print("\n   ❌ ERROR: Usuario 'admin' no encontrado")
    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_current_user_endpoint()
