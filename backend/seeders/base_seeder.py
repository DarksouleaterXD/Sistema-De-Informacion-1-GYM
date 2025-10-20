"""
Clase base para todos los seeders del proyecto
"""
from abc import ABC, abstractmethod
from django.db import transaction


class BaseSeeder(ABC):
    """
    Clase base abstracta para seeders
    """
    
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.error_count = 0
    
    @abstractmethod
    def seed(self):
        """
        Método abstracto que debe implementar cada seeder
        """
        pass
    
    def run(self):
        """
        Ejecuta el seeder con manejo de transacciones
        """
        try:
            with transaction.atomic():
                self.seed()
                self.print_summary()
                return True
        except Exception as e:
            print(f"\n❌ Error al ejecutar seeder: {str(e)}")
            return False
    
    def print_summary(self):
        """
        Imprime un resumen de la ejecución del seeder
        """
        print(f"\n{'='*60}")
        print(f"📊 Resumen de {self.__class__.__name__}")
        print(f"{'='*60}")
        print(f"✅ Creados: {self.created_count}")
        print(f"🔄 Actualizados: {self.updated_count}")
        print(f"❌ Errores: {self.error_count}")
        print(f"{'='*60}\n")
