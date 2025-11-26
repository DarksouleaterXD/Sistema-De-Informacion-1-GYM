"""
Script de prueba para el endpoint de ajuste de inventario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.productos.models import Producto, MovimientoInventario
from apps.users.models import User
from rest_framework.test import APIRequestFactory
from apps.productos.views import ProductoViewSet


def test_ajustar_stock():
    """Probar el endpoint de ajuste de stock"""
    print("\n🧪 Iniciando prueba de ajuste de stock...")
    
    # Obtener producto
    producto = Producto.objects.first()
    if not producto:
        print("❌ No hay productos en el sistema")
        return
    
    print(f"\n📦 Producto seleccionado: {producto.nombre}")
    print(f"   Código: {producto.codigo}")
    print(f"   Stock actual: {producto.stock}")
    
    # Obtener usuario admin
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No se encontró un usuario administrador")
        return
    
    # Simular ajuste de stock
    cantidad_real = producto.stock + 10  # Simular exceso
    
    print(f"\n🔧 Simulando ajuste:")
    print(f"   Cantidad real a registrar: {cantidad_real}")
    print(f"   Diferencia: +{cantidad_real - producto.stock}")
    
    # Crear request simulado
    factory = APIRequestFactory()
    data = {
        'producto_id': producto.id,
        'cantidad_real': cantidad_real,
        'motivo': 'Prueba de ajuste - Exceso detectado en revisión',
        'referencia': 'TEST-001'
    }
    
    request = factory.post('/api/productos/productos/ajustar-stock/', data, format='json')
    request.user = admin
    
    # Ejecutar vista
    view = ProductoViewSet.as_view({'post': 'ajustar_stock'})
    response = view(request)
    
    print(f"\n📊 Respuesta del servidor:")
    print(f"   Status: {response.status_code}")
    print(f"   Mensaje: {response.data.get('message', 'N/A')}")
    
    if response.status_code == 200:
        ajuste = response.data.get('ajuste', {})
        print(f"\n✅ Ajuste realizado exitosamente:")
        print(f"   Stock anterior: {ajuste.get('stock_anterior')}")
        print(f"   Stock actual: {ajuste.get('stock_actual')}")
        print(f"   Diferencia: {ajuste.get('diferencia')}")
        print(f"   Tipo: {ajuste.get('tipo_ajuste')}")
        
        # Verificar que se creó el movimiento
        movimiento_id = response.data.get('movimiento_id')
        if movimiento_id:
            movimiento = MovimientoInventario.objects.get(id=movimiento_id)
            print(f"\n📝 Movimiento registrado:")
            print(f"   ID: {movimiento.id}")
            print(f"   Tipo: {movimiento.tipo}")
            print(f"   Cantidad: {movimiento.cantidad}")
            print(f"   Motivo: {movimiento.motivo}")
            print(f"   Usuario: {movimiento.usuario.get_full_name()}")
        
        # Verificar stock actualizado
        producto.refresh_from_db()
        print(f"\n✅ Verificación final:")
        print(f"   Stock en BD: {producto.stock}")
        print(f"   Stock esperado: {cantidad_real}")
        print(f"   ¿Coinciden? {'✅ SÍ' if producto.stock == cantidad_real else '❌ NO'}")
    else:
        print(f"\n❌ Error en el ajuste:")
        print(f"   {response.data}")
    
    # Mostrar estadísticas
    print(f"\n📊 Estadísticas finales:")
    print(f"   Total movimientos: {MovimientoInventario.objects.count()}")
    print(f"   Ajustes realizados: {MovimientoInventario.objects.filter(tipo='AJUSTE').count()}")
    print(f"   Total productos: {Producto.objects.count()}")


if __name__ == '__main__':
    test_ajustar_stock()
    print("\n✅ Prueba completada!")
