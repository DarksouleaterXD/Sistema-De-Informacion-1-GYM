"""
Script para verificar los datos creados por los seeders
"""
from apps.users.models import User
from apps.roles.models import Role, Permiso
from apps.clients.models import Client, InscripcionMembresia

print("=" * 60)
print("VERIFICACIÓN DE DATOS EN LA BASE DE DATOS")
print("=" * 60)

print("\n=== USUARIOS ===")
print(f"Total usuarios: {User.objects.count()}")
for u in User.objects.all():
    roles = ", ".join([r.nombre for r in u.roles.all()])
    print(f"  • {u.email}")
    print(f"    Nombre: {u.first_name} {u.last_name}")
    print(f"    Staff: {u.is_staff} | Superuser: {u.is_superuser}")
    print(f"    Roles: {roles or 'Sin roles'}")

print("\n=== ROLES ===")
print(f"Total roles: {Role.objects.count()}")
for r in Role.objects.all():
    permisos = r.permisos.all()
    print(f"  • {r.nombre}")
    print(f"    Descripción: {r.descripcion}")
    print(f"    Permisos ({permisos.count()}):")
    for p in permisos:
        print(f"      - {p.nombre}")

print("\n=== PERMISOS ===")
print(f"Total permisos: {Permiso.objects.count()}")
for p in Permiso.objects.all():
    print(f"  • {p.nombre}")
    print(f"    {p.descripcion}")

print("\n=== CLIENTES ===")
print(f"Total clientes: {Client.objects.count()}")
for c in Client.objects.all():
    print(f"  • {c.nombre} {c.apellido}")
    print(f"    Teléfono: {c.telefono}")
    print(f"    Peso: {c.peso}kg | Altura: {c.altura}m")
    print(f"    Experiencia: {c.experiencia}")

print("\n=== INSCRIPCIONES A MEMBRESÍA ===")
print(f"Total inscripciones: {InscripcionMembresia.objects.count()}")
for i in InscripcionMembresia.objects.all():
    print(f"  • Cliente: {i.cliente.nombre} {i.cliente.apellido}")
    print(f"    Monto: Bs. {i.monto}")
    print(f"    Método de pago: {i.metodo_de_pago}")
    print(f"    Fecha inscripción: {i.created_at}")

print("\n" + "=" * 60)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 60)
