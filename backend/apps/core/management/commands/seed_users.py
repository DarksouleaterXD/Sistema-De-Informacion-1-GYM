"""
Comando para ejecutar solo el seeder de usuarios
"""
from django.core.management.base import BaseCommand
from seeders.users_seeder import UsersSeeder


class Command(BaseCommand):
    help = 'Crea usuarios de prueba del sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando usuarios de prueba...'))
        seeder = UsersSeeder()
        seeder.run()
        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))
