"""
Script de prueba manual para CU29 - Registrar Proveedor
Ejecutar con: python test_cu29.py
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
PROVEEDORES_URL = f"{BASE_URL}/proveedores/"

# Credenciales (ajustar según tu setup)
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """Obtener token de autenticación"""
    response = requests.post(LOGIN_URL, json={
        "username": USERNAME,
        "password": PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"Error al autenticar: {response.status_code}")
        print(response.text)
        return None

def test_crear_proveedor(token):
    """Test: Crear proveedor con datos válidos"""
    print("\n=== Test 1: Crear proveedor exitoso ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "razon_social": "Distribuidora Test S.A.",
        "nit": "TEST123456",
        "telefono": "71234567",
        "email": "test@distribuidora.com",
        "direccion": "Av. Test #123",
        "contacto_nombre": "Juan Test"
    }
    
    response = requests.post(PROVEEDORES_URL, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ ÉXITO: Proveedor creado correctamente")
        return response.json()['id']
    else:
        print("❌ FALLO: No se pudo crear el proveedor")
        return None

def test_nit_duplicado(token):
    """Test: Intentar crear proveedor con NIT duplicado"""
    print("\n=== Test 2: NIT duplicado (debe fallar) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "razon_social": "Otra Empresa S.R.L.",
        "nit": "TEST123456"  # NIT duplicado
    }
    
    response = requests.post(PROVEEDORES_URL, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 422:
        print("✅ ÉXITO: Error detectado correctamente (422)")
    else:
        print("❌ FALLO: Se esperaba error 422")

def test_email_invalido(token):
    """Test: Email con formato inválido"""
    print("\n=== Test 3: Email inválido (debe fallar) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "razon_social": "Empresa Email Inválido",
        "nit": "EMAIL999",
        "email": "email-sin-arroba.com"
    }
    
    response = requests.post(PROVEEDORES_URL, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 422:
        print("✅ ÉXITO: Error de validación detectado correctamente (422)")
    else:
        print("❌ FALLO: Se esperaba error 422")

def test_telefono_invalido(token):
    """Test: Teléfono con menos de 7 dígitos"""
    print("\n=== Test 4: Teléfono inválido (debe fallar) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "razon_social": "Empresa Teléfono Inválido",
        "nit": "TEL999",
        "telefono": "12345"  # Solo 5 dígitos
    }
    
    response = requests.post(PROVEEDORES_URL, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 422:
        print("✅ ÉXITO: Error de validación detectado correctamente (422)")
    else:
        print("❌ FALLO: Se esperaba error 422")

def test_listar_proveedores(token):
    """Test: Listar proveedores"""
    print("\n=== Test 5: Listar proveedores ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(PROVEEDORES_URL, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total proveedores: {data.get('count', 0)}")
    
    if response.status_code == 200:
        print("✅ ÉXITO: Lista obtenida correctamente")
    else:
        print("❌ FALLO: No se pudo obtener la lista")

def test_obtener_detalle(token, proveedor_id):
    """Test: Obtener detalle de un proveedor"""
    print(f"\n=== Test 6: Obtener detalle del proveedor ID={proveedor_id} ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{PROVEEDORES_URL}{proveedor_id}/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ ÉXITO: Detalle obtenido correctamente")
    else:
        print("❌ FALLO: No se pudo obtener el detalle")

def main():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("CU29 - Registrar Proveedor - Tests Manuales")
    print("=" * 60)
    
    # Obtener token
    print("\n🔐 Obteniendo token de autenticación...")
    token = get_auth_token()
    
    if not token:
        print("❌ No se pudo autenticar. Verifica las credenciales.")
        return
    
    print(f"✅ Token obtenido: {token[:20]}...")
    
    # Ejecutar tests
    proveedor_id = test_crear_proveedor(token)
    test_nit_duplicado(token)
    test_email_invalido(token)
    test_telefono_invalido(token)
    test_listar_proveedores(token)
    
    if proveedor_id:
        test_obtener_detalle(token, proveedor_id)
    
    print("\n" + "=" * 60)
    print("Tests completados")
    print("=" * 60)

if __name__ == "__main__":
    main()
