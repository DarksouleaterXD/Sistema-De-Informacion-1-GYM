"""
Script para verificar las últimas entradas de la bitácora
"""
from apps.audit.models import HistorialActividad

print("\n" + "="*70)
print("📋 ÚLTIMAS 10 ENTRADAS DE BITÁCORA")
print("="*70 + "\n")

bitacoras = HistorialActividad.objects.all().order_by('-fecha_hora')[:10]

for b in bitacoras:
    usuario_str = f"{b.usuario.get_full_name()} ({b.usuario.email})" if b.usuario else "Sistema"
    fecha_str = b.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
    tipo_icon = {
        'login': '🔐',
        'logout': '🚪',
        'create': '➕',
        'update': '✏️',
        'delete': '🗑️',
        'error': '❌',
    }.get(b.tipo_accion, '📝')
    
    print(f"{tipo_icon} {fecha_str}")
    print(f"   Usuario: {usuario_str}")
    print(f"   Acción: {b.accion}")
    print(f"   Descripción: {b.descripcion}")
    if b.ip_address:
        print(f"   IP: {b.ip_address}")
    print()

print("="*70 + "\n")
