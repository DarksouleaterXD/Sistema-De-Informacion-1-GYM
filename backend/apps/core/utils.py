"""
Utilidades y helpers compartidos
"""
from datetime import datetime, timedelta
from django.utils import timezone


def calcular_fecha_fin(fecha_inicio, dias):
    """
    Calcula la fecha de fin basada en la fecha de inicio y los días de duración
    
    Args:
        fecha_inicio (date): Fecha de inicio
        dias (int): Número de días de duración
        
    Returns:
        date: Fecha de fin calculada
    """
    return fecha_inicio + timedelta(days=dias)


def dias_restantes(fecha_fin):
    """
    Calcula los días restantes hasta una fecha
    
    Args:
        fecha_fin (date): Fecha de finalización
        
    Returns:
        int: Número de días restantes (negativo si ya venció)
    """
    if not fecha_fin:
        return None
    
    hoy = timezone.now().date()
    delta = fecha_fin - hoy
    return delta.days


def esta_activo(fecha_fin):
    """
    Verifica si una membresía está activa basándose en la fecha de fin
    
    Args:
        fecha_fin (date): Fecha de finalización
        
    Returns:
        bool: True si está activa, False si venció
    """
    if not fecha_fin:
        return False
    
    return dias_restantes(fecha_fin) >= 0


def formatear_precio(monto):
    """
    Formatea un monto como precio en bolivianos
    
    Args:
        monto (Decimal): Monto a formatear
        
    Returns:
        str: Monto formateado (ej: "Bs. 250.00")
    """
    return f"Bs. {monto:,.2f}"


def validar_ci(ci):
    """
    Valida que el CI sea un número y tenga entre 6 y 10 dígitos
    
    Args:
        ci (str): Cédula de identidad
        
    Returns:
        bool: True si es válido, False caso contrario
    """
    if not ci:
        return False
    
    ci_limpio = ci.replace('-', '').replace(' ', '')
    return ci_limpio.isdigit() and 6 <= len(ci_limpio) <= 10


def normalizar_telefono(telefono):
    """
    Normaliza un número de teléfono removiendo espacios y guiones
    
    Args:
        telefono (str): Número de teléfono
        
    Returns:
        str: Teléfono normalizado
    """
    if not telefono:
        return ''
    
    return telefono.replace(' ', '').replace('-', '')
