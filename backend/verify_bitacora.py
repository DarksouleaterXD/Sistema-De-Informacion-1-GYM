from apps.audit.models import HistorialActividad

# Contar registros
total = HistorialActividad.objects.count()
print(f"✅ Total de registros en bitácora: {total}")

# Mostrar últimos 10
print("\n📋 Últimos 10 registros:")
print("-" * 100)
for i, log in enumerate(HistorialActividad.objects.all()[:10], 1):
    usuario = log.usuario.username if log.usuario else "Sistema"
    fecha = log.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")
    print(f"{i}. {usuario:20} | {log.tipo_accion:20} | {log.accion:30} | {fecha}")

# Estadísticas por tipo
print("\n📊 Registros por tipo de acción:")
print("-" * 100)
from django.db.models import Count
stats = HistorialActividad.objects.values('tipo_accion').annotate(total=Count('id')).order_by('-total')
for stat in stats[:10]:
    tipo = dict(HistorialActividad.TIPO_ACCION_CHOICES).get(stat['tipo_accion'], stat['tipo_accion'])
    print(f"  {tipo:40} : {stat['total']:3} registros")

# Estadísticas por nivel
print("\n⚠️ Registros por nivel:")
print("-" * 100)
niveles = HistorialActividad.objects.values('nivel').annotate(total=Count('id')).order_by('-total')
for nivel in niveles:
    nivel_label = dict(HistorialActividad.NIVEL_CHOICES).get(nivel['nivel'], nivel['nivel'])
    print(f"  {nivel_label:20} : {nivel['total']:3} registros")

print("\n✅ Verificación completada!")
