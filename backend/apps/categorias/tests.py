"""
Tests para Categorías de Productos
"""
from django.test import TestCase
from .models import CategoriaProducto


class CategoriaProductoTestCase(TestCase):
    """Tests básicos para el modelo CategoriaProducto"""
    
    def setUp(self):
        self.categoria = CategoriaProducto.objects.create(
            nombre="Suplementos",
            codigo="SUP-001",
            descripcion="Categoría de suplementos deportivos"
        )
    
    def test_categoria_creacion(self):
        """Test de creación de categoría"""
        self.assertEqual(self.categoria.nombre, "Suplementos")
        self.assertEqual(self.categoria.codigo, "SUP-001")
        self.assertTrue(self.categoria.activo)
    
    def test_categoria_str(self):
        """Test del método __str__"""
        expected = "SUP-001 - Suplementos"
        self.assertEqual(str(self.categoria), expected)

