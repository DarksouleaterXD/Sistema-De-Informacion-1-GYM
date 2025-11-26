"""
Seeder para crear categorías de productos de prueba
"""
from apps.categorias.models import CategoriaProducto
from .base_seeder import BaseSeeder


class CategoriasSeeder(BaseSeeder):
    """
    Crea categorías de productos de prueba para el gimnasio
    """
    
    def seed(self):
        """
        Crea categorías de productos de prueba
        """
        print("\n🏋️  Creando Categorías de Productos...")
        
        categorias_data = [
            {
                "nombre": "Suplementos Proteicos",
                "codigo": "SUP-PROT",
                "descripcion": "Proteínas, aminoácidos y ganadores de masa",
                "activo": True
            },
            {
                "nombre": "Suplementos Energéticos",
                "codigo": "SUP-ENER",
                "descripcion": "Pre-entrenos, energizantes y termogénicos",
                "activo": True
            },
            {
                "nombre": "Vitaminas y Minerales",
                "codigo": "VIT-MIN",
                "descripcion": "Multivitamínicos y suplementos minerales",
                "activo": True
            },
            {
                "nombre": "Equipamiento",
                "codigo": "EQUIP",
                "descripcion": "Equipamiento deportivo y accesorios",
                "activo": True
            },
            {
                "nombre": "Indumentaria",
                "codigo": "INDUM",
                "descripcion": "Ropa deportiva y calzado",
                "activo": True
            },
            {
                "nombre": "Bebidas",
                "codigo": "BEB",
                "descripcion": "Bebidas isotónicas y energéticas",
                "activo": True
            },
            {
                "nombre": "Snacks Saludables",
                "codigo": "SNACK",
                "descripcion": "Barras proteicas y snacks fitness",
                "activo": True
            },
        ]
        
        for data in categorias_data:
            try:
                categoria, is_created = CategoriaProducto.objects.get_or_create(
                    codigo=data["codigo"],
                    defaults={
                        "nombre": data["nombre"],
                        "descripcion": data["descripcion"],
                        "activo": data["activo"]
                    }
                )
                
                if is_created:
                    print(f"   ✅ Categoría creada: {categoria.nombre}")
                    self.created_count += 1
                else:
                    # Actualizar campos si la categoría ya existe
                    categoria.nombre = data["nombre"]
                    categoria.descripcion = data["descripcion"]
                    categoria.activo = data["activo"]
                    categoria.save()
                    print(f"   ⚠️  Categoría ya existe: {categoria.nombre}")
                    self.updated_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error creando categoría {data['nombre']}: {e}")
                self.error_count += 1

