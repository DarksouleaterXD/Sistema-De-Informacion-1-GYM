"""
Comando para ejecutar todos los seeders del sistema
"""
from django.core.management.base import BaseCommand
from seeders.run_all_seeders import run_all_seeders


class Command(BaseCommand):
    help = 'Ejecuta todos los seeders del sistema para poblar la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando seeders...'))
        run_all_seeders()
        self.stdout.write(self.style.SUCCESS('Proceso de seeders finalizado.'))
