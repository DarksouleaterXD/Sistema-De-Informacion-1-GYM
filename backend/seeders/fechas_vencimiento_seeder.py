"""
Seeder para agregar fechas de vencimiento a productos
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.productos.models import Producto

def seed_fechas_vencimiento():
    """Agregar fechas de vencimiento a productos existentes para testing"""
    
    print("🔧 Agregando fechas de vencimiento a productos...")
    
    productos = Producto.objects.all()
    
    if not productos.exists():
        print("⚠️  No hay productos en la base de datos")
        return
    
    # Obtener algunos productos para asignar fechas
    if productos.count() >= 1:
        # Producto vencido (hace 10 días)
        producto1 = productos[0]
        producto1.fecha_vencimiento = date.today() - timedelta(days=10)
        producto1.save()
        print(f"✅ {producto1.nombre} - Vencido hace 10 días")
    
    if productos.count() >= 2:
        # Producto próximo a vencer (en 15 días)
        producto2 = productos[1]
        producto2.fecha_vencimiento = date.today() + timedelta(days=15)
        producto2.save()
        print(f"✅ {producto2.nombre} - Vence en 15 días")
    
    if productos.count() >= 3:
        # Producto con buen margen (90 días)
        producto3 = productos[2]
        producto3.fecha_vencimiento = date.today() + timedelta(days=90)
        producto3.save()
        print(f"✅ {producto3.nombre} - Vence en 90 días")
    
    print(f"\n✅ Se agregaron fechas de vencimiento a {min(3, productos.count())} productos")

if __name__ == '__main__':
    seed_fechas_vencimiento()
    print("\n✅ Seeder completado exitosamente")
