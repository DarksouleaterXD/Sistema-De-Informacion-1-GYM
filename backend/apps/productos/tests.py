"""
Tests para Productos
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from .models import Producto
from apps.categorias.models import CategoriaProducto
from apps.proveedores.models import Proveedor

User = get_user_model()


class ProductoModelTest(TestCase):
    """Tests para el modelo Producto"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.categoria = CategoriaProducto.objects.create(
            nombre='Suplementos',
            codigo='SUP'
        )
        
        self.proveedor = Proveedor.objects.create(
            razon_social='Proveedor Test',
            nit='123456789'
        )
        
        self.producto = Producto.objects.create(
            nombre='Proteína Whey',
            codigo='PROT001',
            categoria=self.categoria,
            proveedor=self.proveedor,
            precio=Decimal('150.00'),
            costo=Decimal('100.00'),
            stock=50,
            stock_minimo=10,
            creado_por=self.user
        )
    
    def test_producto_creacion(self):
        """Test de creación de producto"""
        self.assertEqual(self.producto.nombre, 'Proteína Whey')
        self.assertEqual(self.producto.codigo, 'PROT001')
        self.assertEqual(self.producto.estado, Producto.ESTADO_ACTIVO)
    
    def test_precio_con_descuento_sin_promocion(self):
        """Test precio sin promoción"""
        self.assertEqual(self.producto.precio_con_descuento, self.producto.precio)
    
    def test_necesita_reposicion(self):
        """Test de alerta de stock bajo"""
        self.producto.stock = 5
        self.assertTrue(self.producto.necesita_reposicion)
        
        self.producto.stock = 20
        self.assertFalse(self.producto.necesita_reposicion)
    
    def test_margen_ganancia(self):
        """Test cálculo de margen de ganancia"""
        margen = self.producto.margen_ganancia
        self.assertEqual(margen, 50.0)  # (150-100)/100 * 100 = 50%
    
    def test_actualizar_stock_sumar(self):
        """Test sumar stock"""
        stock_inicial = self.producto.stock
        self.producto.actualizar_stock(10, 'sumar')
        self.assertEqual(self.producto.stock, stock_inicial + 10)
    
    def test_actualizar_stock_restar(self):
        """Test restar stock"""
        stock_inicial = self.producto.stock
        self.producto.actualizar_stock(5, 'restar')
        self.assertEqual(self.producto.stock, stock_inicial - 5)
    
    def test_codigo_unico(self):
        """Test que el código sea único"""
        with self.assertRaises(Exception):
            Producto.objects.create(
                nombre='Otro Producto',
                codigo='PROT001',  # Código duplicado
                categoria=self.categoria,
                proveedor=self.proveedor,
                precio=Decimal('100.00')
            )


class ProductoAPITest(APITestCase):
    """Tests para la API de productos"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.categoria = CategoriaProducto.objects.create(
            nombre='Suplementos',
            codigo='SUP'
        )
        
        self.proveedor = Proveedor.objects.create(
            razon_social='Proveedor Test',
            nit='123456789'
        )
        
        self.producto_data = {
            'nombre': 'Creatina',
            'codigo': 'CREA001',
            'categoria': self.categoria.id,
            'proveedor': self.proveedor.id,
            'precio': '80.00',
            'costo': '50.00',
            'stock': 100,
            'stock_minimo': 20,
            'unidad_medida': 'KG',
            'estado': 'ACTIVO'
        }
    
    def test_crear_producto(self):
        """Test crear producto vía API"""
        response = self.client.post('/api/productos/', self.producto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(Producto.objects.first().nombre, 'Creatina')
    
    def test_listar_productos(self):
        """Test listar productos"""
        Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            categoria=self.categoria,
            proveedor=self.proveedor,
            precio=Decimal('100.00')
        )
        
        response = self.client.get('/api/productos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_obtener_producto(self):
        """Test obtener detalle de producto"""
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            categoria=self.categoria,
            proveedor=self.proveedor,
            precio=Decimal('100.00')
        )
        
        response = self.client.get(f'/api/productos/{producto.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Producto Test')
    
    def test_actualizar_producto(self):
        """Test actualizar producto"""
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            categoria=self.categoria,
            proveedor=self.proveedor,
            precio=Decimal('100.00')
        )
        
        data = {
            'nombre': 'Producto Actualizado',
            'codigo': 'TEST001',
            'categoria': self.categoria.id,
            'proveedor': self.proveedor.id,
            'precio': '120.00'
        }
        
        response = self.client.put(f'/api/productos/{producto.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, 'Producto Actualizado')
    
    def test_eliminar_producto(self):
        """Test eliminar producto"""
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            categoria=self.categoria,
            proveedor=self.proveedor,
            precio=Decimal('100.00')
        )
        
        response = self.client.delete(f'/api/productos/{producto.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), 0)
