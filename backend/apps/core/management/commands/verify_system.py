"""
Comando Django para verificar el estado del sistema
Uso: python manage.py verify_system
"""
from django.core.management.base import BaseCommand
import sys
import os

# Agregar el directorio de seeders al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..', 'seeders'))

from verify_system import main as verify_main


class Command(BaseCommand):
    help = 'Verifica que todos los componentes del sistema estén funcionando correctamente'

    def handle(self, *args, **options):
        verify_main()
