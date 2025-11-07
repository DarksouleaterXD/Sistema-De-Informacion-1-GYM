"""
Comando de Django para ver las últimas entradas de la bitácora
"""
from django.core.management.base import BaseCommand
from apps.audit.models import HistorialActividad


class Command(BaseCommand):
    help = 'Muestra las últimas entradas de la bitácora'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número de entradas a mostrar (default: 10)'
        )
        parser.add_argument(
            '--tipo',
            type=str,
            help='Filtrar por tipo de acción (ej: login, logout, create, etc.)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        tipo = options.get('tipo')
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS(f"📋 ÚLTIMAS {limit} ENTRADAS DE BITÁCORA"))
        if tipo:
            self.stdout.write(self.style.SUCCESS(f"    Filtrado por tipo: {tipo}"))
        self.stdout.write("="*80 + "\n")
        
        queryset = HistorialActividad.objects.all()
        if tipo:
            queryset = queryset.filter(tipo_accion=tipo)
        
        bitacoras = queryset.order_by('-fecha_hora')[:limit]
        
        if not bitacoras:
            self.stdout.write(self.style.WARNING("⚠️  No se encontraron entradas en la bitácora.\n"))
            return
        
        for i, b in enumerate(bitacoras, 1):
            # Determinar el usuario
            if b.usuario:
                usuario_str = f"{b.usuario.get_full_name()} ({b.usuario.email})"
                usuario_color = self.style.SUCCESS
            else:
                usuario_str = "Sistema (No autenticado)"
                usuario_color = self.style.WARNING
            
            # Fecha formateada
            fecha_str = b.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            
            # Icono según tipo de acción
            tipo_icon = {
                'login': '🔐',
                'logout': '🚪',
                'create': '➕',
                'create_user': '👤➕',
                'update': '✏️',
                'update_user': '👤✏️',
                'delete': '🗑️',
                'delete_user': '👤🗑️',
                'create_role': '🛡️➕',
                'update_role': '🛡️✏️',
                'delete_role': '🛡️🗑️',
                'assign_role': '🔗',
                'create_client': '👨‍💼➕',
                'update_client': '👨‍💼✏️',
                'delete_client': '👨‍💼🗑️',
                'error': '❌',
            }.get(b.tipo_accion, '📝')
            
            # Nivel de severidad
            nivel_style = {
                'info': self.style.SUCCESS,
                'warning': self.style.WARNING,
                'error': self.style.ERROR,
                'critical': self.style.ERROR,
            }.get(b.nivel, self.style.SUCCESS)
            
            self.stdout.write(f"\n{i}. {tipo_icon} {fecha_str} - {nivel_style(b.nivel.upper())}")
            self.stdout.write(f"   Usuario: {usuario_color(usuario_str)}")
            self.stdout.write(f"   Tipo: {b.get_tipo_accion_display()}")
            self.stdout.write(f"   Acción: {b.accion}")
            
            if b.descripcion:
                # Limitar descripción a 100 caracteres
                desc = b.descripcion[:100] + "..." if len(b.descripcion) > 100 else b.descripcion
                self.stdout.write(f"   Descripción: {desc}")
            
            if b.ip_address:
                self.stdout.write(f"   IP: {b.ip_address}")
            
            if b.datos_adicionales and b.datos_adicionales != {}:
                self.stdout.write(f"   Datos: {b.datos_adicionales}")
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS(f"Total de entradas mostradas: {len(bitacoras)}"))
        self.stdout.write("="*80 + "\n")
