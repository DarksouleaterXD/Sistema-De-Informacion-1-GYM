"""
Comando para ejecutar solo el seeder de clientes
"""
from django.core.management.base import BaseCommand
from seeders.clients_seeder import ClientsSeeder


class Command(BaseCommand):
    help = 'Crea clientes y membresías de prueba'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando clientes y membresías de prueba...'))
        seeder = ClientsSeeder()
        seeder.run()
        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))
