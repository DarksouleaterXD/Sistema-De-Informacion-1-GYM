"""
Comando para ejecutar solo el seeder del superusuario
"""
from django.core.management.base import BaseCommand
from seeders.superuser_seeder import SuperUserSeeder


class Command(BaseCommand):
    help = 'Crea el superusuario del sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando superusuario...'))
        seeder = SuperUserSeeder()
        seeder.run()
        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))
