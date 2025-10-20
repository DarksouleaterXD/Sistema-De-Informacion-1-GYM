"""
Comando para ejecutar solo el seeder de roles
"""
from django.core.management.base import BaseCommand
from seeders.roles_seeder import RolesSeeder


class Command(BaseCommand):
    help = 'Crea los roles y permisos del sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando roles y permisos...'))
        seeder = RolesSeeder()
        seeder.run()
        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))
