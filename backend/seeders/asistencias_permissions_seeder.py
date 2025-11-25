#!/usr/bin/env python
"""
Script para crear los permisos de asistencias
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.roles.models import Permiso

def crear_permisos_asistencias():
    """Crear permisos del módulo de asistencias"""
    print("🔐 Creando permisos de asistencias...")
    
    permisos = [
        {
            'codigo': 'asistencia.view',
            'nombre': 'Ver Asistencias',
            'descripcion': 'Permite ver el listado de asistencias a clases'
        },
        {
            'codigo': 'asistencia.create',
            'nombre': 'Registrar Asistencia',
            'descripcion': 'Permite registrar asistencia de clientes a clases'
        },
        {
            'codigo': 'asistencia.edit',
            'nombre': 'Editar Asistencia',
            'descripcion': 'Permite modificar registros de asistencia'
        },
        {
            'codigo': 'asistencia.delete',
            'nombre': 'Eliminar Asistencia',
            'descripcion': 'Permite eliminar registros de asistencia'
        },
        {
            'codigo': 'asistencia.view_details',
            'nombre': 'Ver Detalles de Asistencia',
            'descripcion': 'Permite ver información detallada de asistencias'
        },
    ]
    
    creados = 0
    actualizados = 0
    
    for perm_data in permisos:
        perm, created = Permiso.objects.get_or_create(
            codigo=perm_data['codigo'],
            defaults={
                'nombre': perm_data['nombre'],
                'descripcion': perm_data['descripcion']
            }
        )
        
        if created:
            print(f"  ✅ Creado: {perm.codigo} - {perm.nombre}")
            creados += 1
        else:
            print(f"  ♻️  Ya existe: {perm.codigo}")
            actualizados += 1
    
    print(f"\n✅ Proceso completado:")
    print(f"   - {creados} permisos creados")
    print(f"   - {actualizados} permisos existentes")
    print(f"   - {creados + actualizados} permisos totales")

if __name__ == '__main__':
    crear_permisos_asistencias()
