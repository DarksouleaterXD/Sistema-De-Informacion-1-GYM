"""
Seeder para crear movimientos de inventario de ejemplo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.productos.models import Producto, MovimientoInventario
from apps.users.models import User


def crear_movimientos_inventario():
    """Crear movimientos de inventario de ejemplo"""
    print("🔄 Iniciando creación de movimientos de inventario...")
    
    # Obtener usuario admin
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No se encontró un usuario administrador")
        return
    
    # Obtener productos existentes
    productos = Producto.objects.all()[:5]
    
    if not productos:
        print("❌ No hay productos en el sistema")
        return
    
    movimientos_creados = 0
    
    for producto in productos:
        # Crear movimiento de ENTRADA
        movimiento_entrada = MovimientoInventario.objects.create(
            producto=producto,
            usuario=admin,
            tipo=MovimientoInventario.TIPO_ENTRADA,
            cantidad=50,
            cantidad_anterior=producto.stock - 50,
            cantidad_nueva=producto.stock,
            motivo="Compra a proveedor - Orden #12345",
            referencia="OC-2024-12345"
        )
        movimientos_creados += 1
        print(f"✅ Movimiento ENTRADA creado: {producto.nombre} (+50)")
        
        # Crear movimiento de SALIDA (si hay stock)
        if producto.stock >= 10:
            stock_anterior = producto.stock
            producto.stock -= 10
            producto.save()
            
            movimiento_salida = MovimientoInventario.objects.create(
                producto=producto,
                usuario=admin,
                tipo=MovimientoInventario.TIPO_SALIDA,
                cantidad=10,
                cantidad_anterior=stock_anterior,
                cantidad_nueva=producto.stock,
                motivo="Venta a cliente - Factura #001234",
                referencia="FAC-001234"
            )
            movimientos_creados += 1
            print(f"✅ Movimiento SALIDA creado: {producto.nombre} (-10)")
    
    # Crear un ajuste de inventario de ejemplo
    if productos:
        producto_ajuste = productos[0]
        stock_anterior = producto_ajuste.stock
        cantidad_real = stock_anterior + 5  # Simular exceso
        diferencia = cantidad_real - stock_anterior
        
        producto_ajuste.stock = cantidad_real
        producto_ajuste.save()
        
        movimiento_ajuste = MovimientoInventario.objects.create(
            producto=producto_ajuste,
            usuario=admin,
            tipo=MovimientoInventario.TIPO_AJUSTE,
            cantidad=abs(diferencia),
            cantidad_anterior=stock_anterior,
            cantidad_nueva=cantidad_real,
            motivo="Ajuste por inventario físico - Exceso detectado en revisión mensual",
            referencia="INV-2024-001"
        )
        movimientos_creados += 1
        print(f"✅ Movimiento AJUSTE creado: {producto_ajuste.nombre} (Diferencia: +{diferencia})")
    
    print(f"\n✅ Total de movimientos creados: {movimientos_creados}")
    print(f"📊 Total de movimientos en BD: {MovimientoInventario.objects.count()}")


if __name__ == '__main__':
    crear_movimientos_inventario()
    print("\n✅ Seeder de movimientos completado!")
