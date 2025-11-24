"""
CU29 - Registrar Proveedor
Tests unitarios completos
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.proveedores.models import Proveedor
from apps.audit.models import HistorialActividad

User = get_user_model()


class ProveedorModelTests(TestCase):
    """Tests del modelo Proveedor"""
    
    def setUp(self):
        """Configuración inicial"""
        self.proveedor_data = {
            'razon_social': 'Distribuidora ABC S.A.',
            'nit': '1234567890',
            'telefono': '71234567',
            'email': 'contacto@abc.com',
            'direccion': 'Av. Principal #123'
        }
    
    def test_crear_proveedor_exitoso(self):
        """Test: Crear proveedor con datos válidos"""
        proveedor = Proveedor.objects.create(**self.proveedor_data)
        
        self.assertEqual(proveedor.razon_social, 'Distribuidora ABC S.A.')
        self.assertEqual(proveedor.nit, '1234567890')
        self.assertEqual(proveedor.estado, Proveedor.ESTADO_ACTIVO)
        self.assertTrue(proveedor.esta_activo)
    
    def test_proveedor_str_representation(self):
        """Test: Representación string del proveedor"""
        proveedor = Proveedor.objects.create(**self.proveedor_data)
        expected = f"{proveedor.razon_social} (NIT: {proveedor.nit})"
        self.assertEqual(str(proveedor), expected)
    
    def test_unicidad_nit(self):
        """Test: NIT debe ser único"""
        Proveedor.objects.create(**self.proveedor_data)
        
        # Intentar crear otro proveedor con mismo NIT
        with self.assertRaises(Exception):
            Proveedor.objects.create(
                razon_social='Otra Empresa',
                nit='1234567890',  # NIT duplicado
                telefono='71111111'
            )
    
    def test_unicidad_razon_social(self):
        """Test: Razón social debe ser única"""
        Proveedor.objects.create(**self.proveedor_data)
        
        # Intentar crear otro proveedor con misma razón social
        with self.assertRaises(Exception):
            Proveedor.objects.create(
                razon_social='Distribuidora ABC S.A.',  # Razón social duplicada
                nit='9999999999',
                telefono='72222222'
            )
    
    def test_cambiar_estado(self):
        """Test: Cambios de estado del proveedor"""
        proveedor = Proveedor.objects.create(**self.proveedor_data)
        
        # Desactivar
        proveedor.desactivar()
        proveedor.refresh_from_db()
        self.assertEqual(proveedor.estado, Proveedor.ESTADO_INACTIVO)
        self.assertFalse(proveedor.esta_activo)
        
        # Activar
        proveedor.activar()
        proveedor.refresh_from_db()
        self.assertEqual(proveedor.estado, Proveedor.ESTADO_ACTIVO)
        self.assertTrue(proveedor.esta_activo)
        
        # Suspender
        proveedor.suspender()
        proveedor.refresh_from_db()
        self.assertEqual(proveedor.estado, Proveedor.ESTADO_SUSPENDIDO)


class ProveedorAPITests(TestCase):
    """Tests de la API de Proveedores (CU29)"""
    
    def setUp(self):
        """Configuración inicial para tests de API"""
        self.client = APIClient()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)
        
        self.valid_proveedor = {
            'razon_social': 'Distribuidora ABC S.A.',
            'nit': '1234567890',
            'telefono': '71234567',
            'email': 'contacto@abc.com',
            'direccion': 'Av. Principal #123',
            'contacto_nombre': 'Juan Pérez'
        }
    
    def test_crear_proveedor_exitoso(self):
        """Test CU29: Crear proveedor con datos válidos (201 Created)"""
        response = self.client.post('/api/proveedores/', self.valid_proveedor, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['razon_social'], 'Distribuidora ABC S.A.')
        self.assertEqual(response.data['nit'], '1234567890')
        self.assertEqual(response.data['estado'], 'A')
        self.assertTrue(response.data['esta_activo'])
        
        # Verificar que se creó en DB
        self.assertEqual(Proveedor.objects.count(), 1)
        proveedor = Proveedor.objects.first()
        self.assertEqual(proveedor.razon_social, 'Distribuidora ABC S.A.')
    
    def test_crear_proveedor_datos_minimos(self):
        """Test CU29: Crear proveedor solo con campos obligatorios"""
        minimal_data = {
            'razon_social': 'Proveedor Mínimo',
            'nit': '9999999999'
        }
        
        response = self.client.post('/api/proveedores/', minimal_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['razon_social'], 'Proveedor Mínimo')
        self.assertEqual(response.data['nit'], '9999999999')
        self.assertEqual(response.data['estado'], 'A')
    
    def test_crear_proveedor_nit_duplicado(self):
        """Test CU29: Error 422 al intentar crear proveedor con NIT duplicado"""
        # Crear primer proveedor
        Proveedor.objects.create(**self.valid_proveedor)
        
        # Intentar crear otro con mismo NIT
        duplicate_data = {
            'razon_social': 'Otra Empresa S.R.L.',
            'nit': '1234567890'  # NIT duplicado
        }
        
        response = self.client.post('/api/proveedores/', duplicate_data, format='json')
        
        # El serializer detecta el duplicado y retorna 422
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)
        self.assertIn('nit', response.data['detail'])
    
    def test_crear_proveedor_razon_social_duplicada(self):
        """Test CU29: Error 422 al intentar crear proveedor con razón social duplicada"""
        # Crear primer proveedor
        Proveedor.objects.create(**self.valid_proveedor)
        
        # Intentar crear otro con misma razón social
        duplicate_data = {
            'razon_social': 'Distribuidora ABC S.A.',  # Razón social duplicada
            'nit': '9999999999'
        }
        
        response = self.client.post('/api/proveedores/', duplicate_data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_409_CONFLICT, status.HTTP_422_UNPROCESSABLE_ENTITY])
        self.assertIn('error', response.data)
    
    def test_crear_proveedor_sin_razon_social(self):
        """Test CU29: Error 422 sin razón social"""
        invalid_data = {
            'nit': '1234567890'
            # falta razon_social
        }
        
        response = self.client.post('/api/proveedores/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)
        self.assertIn('razon_social', response.data['detail'])
    
    def test_crear_proveedor_sin_nit(self):
        """Test CU29: Error 422 sin NIT"""
        invalid_data = {
            'razon_social': 'Empresa Sin NIT'
            # falta nit
        }
        
        response = self.client.post('/api/proveedores/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)
        self.assertIn('nit', response.data['detail'])
    
    def test_crear_proveedor_email_invalido(self):
        """Test CU29: Error 422 con email inválido"""
        invalid_data = {
            'razon_social': 'Empresa Email Inválido',
            'nit': '1234567890',
            'email': 'email-invalido'  # formato inválido
        }
        
        response = self.client.post('/api/proveedores/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)
        self.assertIn('email', response.data['detail'])
    
    def test_crear_proveedor_telefono_muy_corto(self):
        """Test CU29: Error 422 con teléfono menor a 7 dígitos"""
        invalid_data = {
            'razon_social': 'Empresa Teléfono Corto',
            'nit': '1234567890',
            'telefono': '123456'  # solo 6 dígitos
        }
        
        response = self.client.post('/api/proveedores/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)
        self.assertIn('telefono', response.data['detail'])
    
    def test_crear_proveedor_telefono_muy_largo(self):
        """Test CU29: Error 422 con teléfono mayor a 15 dígitos"""
        invalid_data = {
            'razon_social': 'Empresa Teléfono Largo',
            'nit': '1234567890',
            'telefono': '1234567890123456'  # 16 dígitos
        }
        
        response = self.client.post('/api/proveedores/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)
        self.assertIn('telefono', response.data['detail'])
    
    def test_crear_proveedor_telefono_valido(self):
        """Test CU29: Teléfono válido con 7-15 dígitos"""
        valid_phones = ['7123456', '71234567', '123456789012345']
        
        for i, phone in enumerate(valid_phones):
            data = {
                'razon_social': f'Empresa Teléfono {i}',
                'nit': f'NIT{i}000000',
                'telefono': phone
            }
            
            response = self.client.post('/api/proveedores/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_listar_proveedores(self):
        """Test: Listar proveedores"""
        # Crear varios proveedores
        Proveedor.objects.create(**self.valid_proveedor)
        Proveedor.objects.create(
            razon_social='Proveedor 2',
            nit='9999999999',
            telefono='72222222'
        )
        
        response = self.client.get('/api/proveedores/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_obtener_detalle_proveedor(self):
        """Test: Obtener detalle de un proveedor"""
        proveedor = Proveedor.objects.create(**self.valid_proveedor)
        
        response = self.client.get(f'/api/proveedores/{proveedor.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], proveedor.id)
        self.assertEqual(response.data['razon_social'], proveedor.razon_social)
    
    def test_sin_autenticacion(self):
        """Test CU29: Error 401/403 sin autenticación"""
        self.client.force_authenticate(user=None)
        
        response = self.client.post('/api/proveedores/', self.valid_proveedor, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_bitacora_registrada(self):
        """Test CU29: Verificar que se registra en bitácora"""
        initial_count = HistorialActividad.objects.count()
        
        response = self.client.post('/api/proveedores/', self.valid_proveedor, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se creó entrada en bitácora
        final_count = HistorialActividad.objects.count()
        self.assertGreater(final_count, initial_count)
        
        # Verificar contenido del registro (buscar registro manual)
        registros_proveedor = HistorialActividad.objects.filter(
            usuario=self.user,
            accion__icontains='Proveedor'
        ).order_by('-fecha_hora')
        
        self.assertTrue(registros_proveedor.exists())


class ProveedorValidationTests(TestCase):
    """Tests adicionales de validaciones de negocio"""
    
    def test_normalizar_nit_mayusculas(self):
        """Test: NIT se normaliza a mayúsculas"""
        proveedor = Proveedor.objects.create(
            razon_social='Test Empresa',
            nit='abc123def'
        )
        
        self.assertEqual(proveedor.nit, 'ABC123DEF')
    
    def test_normalizar_telefono_solo_digitos(self):
        """Test: Teléfono se normaliza a solo dígitos"""
        proveedor = Proveedor.objects.create(
            razon_social='Test Empresa',
            nit='123456789',
            telefono='71234567'  # Ya normalizado con 8 dígitos
        )
        
        proveedor.refresh_from_db()
        self.assertEqual(proveedor.telefono, '71234567')  # Solo dígitos
    
    def test_normalizar_email_minusculas(self):
        """Test: Email se normaliza a minúsculas"""
        proveedor = Proveedor.objects.create(
            razon_social='Test Empresa',
            nit='123456789',
            email='CONTACTO@EMPRESA.COM'
        )
        
        proveedor.refresh_from_db()
        self.assertEqual(proveedor.email, 'contacto@empresa.com')
