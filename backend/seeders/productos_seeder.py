"""
Seeder para Productos - Datos de Prueba
Carga categorías y productos iniciales para el gimnasio
"""
import sys
import os
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from apps.productos.models import CategoriaProducto, Producto
from apps.proveedores.models import Proveedor
from apps.users.models import User


class ProductosSeeder:
    """Seeder para productos y categorías"""
    
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.error_count = 0
    
    def run(self):
        """Ejecutar seeder"""
        print("\n🏋️  Creando Categorías de Productos...")
        self.create_categorias()
        
        print("\n📦 Creando Productos...")
        self.create_productos()
        
        self.print_summary()
    
    def create_categorias(self):
        """Crear categorías de productos"""
        categorias = [
            {"nombre": "Suplementos Proteicos", "codigo": "SUP-PROT", "descripcion": "Proteínas, aminoácidos y ganadores de masa"},
            {"nombre": "Suplementos Energéticos", "codigo": "SUP-ENER", "descripcion": "Pre-entrenos, energizantes y termogénicos"},
            {"nombre": "Vitaminas y Minerales", "codigo": "VIT-MIN", "descripcion": "Multivitamínicos y suplementos minerales"},
            {"nombre": "Equipamiento", "codigo": "EQUIP", "descripcion": "Equipamiento deportivo y accesorios"},
            {"nombre": "Indumentaria", "codigo": "INDUM", "descripcion": "Ropa deportiva y calzado"},
            {"nombre": "Bebidas", "codigo": "BEB", "descripcion": "Bebidas isotónicas y energéticas"},
            {"nombre": "Snacks Saludables", "codigo": "SNACK", "descripcion": "Barras proteicas y snacks fitness"},
        ]
        
        for cat_data in categorias:
            try:
                categoria, created = CategoriaProducto.objects.get_or_create(
                    codigo=cat_data["codigo"],
                    defaults={
                        "nombre": cat_data["nombre"],
                        "descripcion": cat_data["descripcion"]
                    }
                )
                
                if created:
                    print(f"   ✅ Categoría creada: {categoria.nombre}")
                    self.created_count += 1
                else:
                    print(f"   ⚠️  Categoría ya existe: {categoria.nombre}")
                    self.updated_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error creando categoría {cat_data['nombre']}: {e}")
                self.error_count += 1
    
    def create_productos(self):
        """Crear productos de ejemplo"""
        # Obtener proveedor (debe existir)
        try:
            proveedor = Proveedor.objects.filter(estado=Proveedor.ESTADO_ACTIVO).first()
            if not proveedor:
                print("   ⚠️  No hay proveedores activos. Creando proveedor de ejemplo...")
                proveedor = Proveedor.objects.create(
                    razon_social="Distribuidora Fitness Bolivia",
                    nit="1234567890",
                    telefono="77777777",
                    email="ventas@fitnessbolivia.com",
                    direccion="Av. Principal 123, La Paz",
                    estado=Proveedor.ESTADO_ACTIVO
                )
        except Exception as e:
            print(f"   ❌ Error obteniendo proveedor: {e}")
            return
        
        # Obtener usuario admin
        try:
            admin = User.objects.filter(is_superuser=True).first()
        except:
            admin = None
        
        # Obtener categorías
        categorias = {cat.codigo: cat for cat in CategoriaProducto.objects.all()}
        
        productos = [
            # Suplementos Proteicos
            {
                "nombre": "Proteína Whey Gold Standard",
                "codigo": "PROT-WGS-001",
                "categoria": categorias.get("SUP-PROT"),
                "descripcion": "Proteína de suero de leche de alta calidad, ideal para recuperación muscular",
                "precio": Decimal("280.00"),
                "costo": Decimal("200.00"),
                "stock": 50,
                "stock_minimo": 10,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Proteína Isolate Premium",
                "codigo": "PROT-ISO-001",
                "categoria": categorias.get("SUP-PROT"),
                "descripcion": "Proteína aislada 95% pureza, baja en lactosa",
                "precio": Decimal("350.00"),
                "costo": Decimal("250.00"),
                "stock": 30,
                "stock_minimo": 5,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Creatina Monohidrato 300g",
                "codigo": "CREA-MONO-300",
                "categoria": categorias.get("SUP-PROT"),
                "descripcion": "Creatina pura para aumento de fuerza y masa muscular",
                "precio": Decimal("120.00"),
                "costo": Decimal("80.00"),
                "stock": 80,
                "stock_minimo": 15,
                "unidad_medida": "UNIDAD"
            },
            # Suplementos Energéticos
            {
                "nombre": "Pre-Entreno Explosive",
                "codigo": "PRE-EXP-001",
                "categoria": categorias.get("SUP-ENER"),
                "descripcion": "Pre-entreno con cafeína, beta-alanina y citrulina",
                "precio": Decimal("150.00"),
                "costo": Decimal("100.00"),
                "stock": 40,
                "stock_minimo": 10,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Quemador de Grasa Thermo",
                "codigo": "THER-001",
                "categoria": categorias.get("SUP-ENER"),
                "descripcion": "Termogénico para definición muscular",
                "precio": Decimal("180.00"),
                "costo": Decimal("120.00"),
                "stock": 25,
                "stock_minimo": 5,
                "unidad_medida": "UNIDAD"
            },
            # Vitaminas y Minerales
            {
                "nombre": "Multivitamínico Daily",
                "codigo": "MULTI-DAILY-001",
                "categoria": categorias.get("VIT-MIN"),
                "descripcion": "Complejo vitamínico diario para deportistas",
                "precio": Decimal("90.00"),
                "costo": Decimal("60.00"),
                "stock": 60,
                "stock_minimo": 15,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Omega 3 1000mg",
                "codigo": "OMEGA3-1000",
                "categoria": categorias.get("VIT-MIN"),
                "descripcion": "Ácidos grasos esenciales para salud cardiovascular",
                "precio": Decimal("110.00"),
                "costo": Decimal("75.00"),
                "stock": 45,
                "stock_minimo": 10,
                "unidad_medida": "UNIDAD"
            },
            # Equipamiento
            {
                "nombre": "Guantes de Entrenamiento Pro",
                "codigo": "EQUIP-GUANT-PRO",
                "categoria": categorias.get("EQUIP"),
                "descripcion": "Guantes acolchados para levantamiento de pesas",
                "precio": Decimal("65.00"),
                "costo": Decimal("40.00"),
                "stock": 35,
                "stock_minimo": 10,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Shaker Mezclador 700ml",
                "codigo": "EQUIP-SHAK-700",
                "categoria": categorias.get("EQUIP"),
                "descripcion": "Vaso mezclador con compartimento para suplementos",
                "precio": Decimal("35.00"),
                "costo": Decimal("20.00"),
                "stock": 100,
                "stock_minimo": 20,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Cinta para Muñecas",
                "codigo": "EQUIP-CINTA-MUN",
                "categoria": categorias.get("EQUIP"),
                "descripcion": "Soporte para muñecas en ejercicios pesados",
                "precio": Decimal("45.00"),
                "costo": Decimal("25.00"),
                "stock": 50,
                "stock_minimo": 15,
                "unidad_medida": "UNIDAD"
            },
            # Indumentaria
            {
                "nombre": "Camiseta Deportiva Dry-Fit",
                "codigo": "INDUM-CAM-DRY",
                "categoria": categorias.get("INDUM"),
                "descripcion": "Camiseta transpirable para entrenamiento",
                "precio": Decimal("85.00"),
                "costo": Decimal("50.00"),
                "stock": 40,
                "stock_minimo": 10,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Short de Entrenamiento",
                "codigo": "INDUM-SHORT-001",
                "categoria": categorias.get("INDUM"),
                "descripcion": "Short cómodo para gym y running",
                "precio": Decimal("75.00"),
                "costo": Decimal("45.00"),
                "stock": 30,
                "stock_minimo": 8,
                "unidad_medida": "UNIDAD"
            },
            # Bebidas
            {
                "nombre": "Bebida Isotónica 500ml",
                "codigo": "BEB-ISO-500",
                "categoria": categorias.get("BEB"),
                "descripcion": "Bebida para hidratación durante el ejercicio",
                "precio": Decimal("12.00"),
                "costo": Decimal("7.00"),
                "stock": 200,
                "stock_minimo": 50,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Energético Sport 250ml",
                "codigo": "BEB-ENER-250",
                "categoria": categorias.get("BEB"),
                "descripcion": "Bebida energética para antes del entreno",
                "precio": Decimal("15.00"),
                "costo": Decimal("9.00"),
                "stock": 150,
                "stock_minimo": 40,
                "unidad_medida": "UNIDAD"
            },
            # Snacks Saludables
            {
                "nombre": "Barra Proteica Chocolate",
                "codigo": "SNACK-BAR-CHOC",
                "categoria": categorias.get("SNACK"),
                "descripcion": "Barra con 20g de proteína sabor chocolate",
                "precio": Decimal("18.00"),
                "costo": Decimal("11.00"),
                "stock": 120,
                "stock_minimo": 30,
                "unidad_medida": "UNIDAD"
            },
            {
                "nombre": "Mix de Frutos Secos 200g",
                "codigo": "SNACK-NUTS-200",
                "categoria": categorias.get("SNACK"),
                "descripcion": "Mezcla de almendras, nueces y pasas",
                "precio": Decimal("35.00"),
                "costo": Decimal("22.00"),
                "stock": 70,
                "stock_minimo": 20,
                "unidad_medida": "PAQUETE"
            },
        ]
        
        for prod_data in productos:
            if not prod_data.get("categoria"):
                print(f"   ⚠️  Categoría no encontrada para {prod_data['nombre']}")
                continue
            
            try:
                producto, created = Producto.objects.get_or_create(
                    codigo=prod_data["codigo"],
                    defaults={
                        "nombre": prod_data["nombre"],
                        "descripcion": prod_data["descripcion"],
                        "categoria": prod_data["categoria"],
                        "proveedor": proveedor,
                        "precio": prod_data["precio"],
                        "costo": prod_data["costo"],
                        "stock": prod_data["stock"],
                        "stock_minimo": prod_data["stock_minimo"],
                        "unidad_medida": prod_data["unidad_medida"],
                        "estado": Producto.ESTADO_ACTIVO,
                        "creado_por": admin,
                        "modificado_por": admin
                    }
                )
                
                if created:
                    print(f"   ✅ Producto creado: {producto.nombre} (Stock: {producto.stock})")
                    self.created_count += 1
                else:
                    print(f"   ⚠️  Producto ya existe: {producto.nombre}")
                    self.updated_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error creando producto {prod_data['nombre']}: {e}")
                self.error_count += 1
    
    def print_summary(self):
        """Imprimir resumen de la ejecución"""
        print("\n" + "=" * 60)
        print("📊 Resumen de ProductosSeeder")
        print("=" * 60)
        print(f"✅ Creados: {self.created_count}")
        print(f"🔄 Actualizados: {self.updated_count}")
        print(f"❌ Errores: {self.error_count}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    seeder = ProductosSeeder()
    seeder.run()
