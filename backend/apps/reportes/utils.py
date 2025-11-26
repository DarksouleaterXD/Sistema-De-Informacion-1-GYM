"""
Utilidades para generación de reportes
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from collections import defaultdict


def calcular_periodo(tipo_periodo, fecha_inicio=None, fecha_fin=None):
    """
    Calcula las fechas de inicio y fin según el tipo de período

    Args:
        tipo_periodo: 'dia', 'semana', 'mes', 'anio', 'personalizado'
        fecha_inicio: Fecha de inicio (para personalizado)
        fecha_fin: Fecha de fin (para personalizado)

    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    hoy = timezone.now().date()

    if tipo_periodo == "dia":
        return hoy, hoy

    elif tipo_periodo == "semana":
        # Lunes de la semana actual
        inicio = hoy - timedelta(days=hoy.weekday())
        fin = inicio + timedelta(days=6)
        return inicio, fin

    elif tipo_periodo == "mes":
        inicio = date(hoy.year, hoy.month, 1)
        # Último día del mes
        if hoy.month == 12:
            fin = date(hoy.year + 1, 1, 1) - timedelta(days=1)
        else:
            fin = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
        return inicio, fin

    elif tipo_periodo == "anio":
        inicio = date(hoy.year, 1, 1)
        fin = date(hoy.year, 12, 31)
        return inicio, fin

    elif tipo_periodo == "personalizado":
        if not fecha_inicio or not fecha_fin:
            raise ValueError("Las fechas son requeridas para rango personalizado")
        return fecha_inicio, fecha_fin

    else:
        raise ValueError(f"Tipo de período no válido: {tipo_periodo}")


def generar_reporte_ventas(fecha_inicio, fecha_fin):
    """
    Genera reporte de ventas para el período especificado

    Returns:
        dict: Datos del reporte de ventas
    """
    from apps.ventas.models import Venta, DetalleVenta

    # Filtrar ventas del período
    ventas = (
        Venta.objects.filter(
            fecha_venta__date__gte=fecha_inicio,
            fecha_venta__date__lte=fecha_fin,
            estado=Venta.ESTADO_COMPLETADA,
        )
        .select_related("cliente")
        .prefetch_related("detalles__producto")
    )

    # Totales
    total_ventas = ventas.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    cantidad_ventas = ventas.count()

    # Ventas por método de pago
    ventas_por_metodo = (
        ventas.values("metodo_pago")
        .annotate(total=Sum("total"), cantidad=Count("id"))
        .order_by("-total")
    )
    ventas_por_metodo_pago = {
        item["metodo_pago"]: {
            "total": float(item["total"]),
            "cantidad": item["cantidad"],
        }
        for item in ventas_por_metodo
    }

    # Ventas por día
    ventas_por_dia = (
        ventas.extra(select={"dia": "DATE(fecha_venta)"})
        .values("dia")
        .annotate(total=Sum("total"), cantidad=Count("id"))
        .order_by("dia")
    )
    ventas_por_dia_list = [
        {
            "fecha": item["dia"],
            "total": float(item["total"]),
            "cantidad": item["cantidad"],
        }
        for item in ventas_por_dia
    ]

    # Productos más vendidos
    productos_vendidos = (
        DetalleVenta.objects.filter(
            venta__fecha_venta__date__gte=fecha_inicio,
            venta__fecha_venta__date__lte=fecha_fin,
            venta__estado=Venta.ESTADO_COMPLETADA,
        )
        .values("producto__nombre", "producto__codigo")
        .annotate(
            cantidad_vendida=Sum("cantidad"),
            total_vendido=Sum(F("cantidad") * F("precio_unitario") - F("descuento")),
        )
        .order_by("-cantidad_vendida")[:10]
    )
    productos_mas_vendidos = [
        {
            "producto": item["producto__nombre"],
            "codigo": item["producto__codigo"],
            "cantidad": item["cantidad_vendida"],
            "total": float(item["total_vendido"]),
        }
        for item in productos_vendidos
    ]

    # Clientes más frecuentes
    clientes_frecuentes = (
        ventas.values("cliente__nombre", "cliente__apellido", "cliente__ci")
        .annotate(
            cantidad_compras=Count("id"),
            total_gastado=Sum("total"),
        )
        .order_by("-cantidad_compras")[:10]
    )
    clientes_mas_frecuentes = [
        {
            "cliente": f"{item['cliente__nombre']} {item['cliente__apellido']}",
            "ci": item["cliente__ci"],
            "cantidad_compras": item["cantidad_compras"],
            "total_gastado": float(item["total_gastado"]),
        }
        for item in clientes_frecuentes
    ]

    return {
        "total_ventas": float(total_ventas),
        "cantidad_ventas": cantidad_ventas,
        "ventas_por_metodo_pago": ventas_por_metodo_pago,
        "ventas_por_dia": ventas_por_dia_list,
        "productos_mas_vendidos": productos_mas_vendidos,
        "clientes_mas_frecuentes": clientes_mas_frecuentes,
        "periodo": {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
        },
    }


def generar_reporte_compras(fecha_inicio, fecha_fin):
    """
    Genera reporte de compras para el período especificado

    Returns:
        dict: Datos del reporte de compras
    """
    from apps.compras.models import OrdenCompra, ItemOrdenCompra

    # Filtrar órdenes del período
    ordenes = (
        OrdenCompra.objects.filter(
            fecha_orden__date__gte=fecha_inicio,
            fecha_orden__date__lte=fecha_fin,
            estado__in=[OrdenCompra.ESTADO_CONFIRMADA, OrdenCompra.ESTADO_RECIBIDA],
        )
        .select_related("proveedor")
        .prefetch_related("items__producto")
    )

    # Totales
    total_compras = ordenes.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    cantidad_ordenes = ordenes.count()

    # Compras por proveedor
    compras_por_proveedor = (
        ordenes.values("proveedor__razon_social", "proveedor__nit")
        .annotate(
            cantidad_ordenes=Count("id"),
            total_comprado=Sum("total"),
        )
        .order_by("-total_comprado")
    )
    compras_por_proveedor_list = [
        {
            "proveedor": item["proveedor__razon_social"],
            "nit": item["proveedor__nit"],
            "cantidad_ordenes": item["cantidad_ordenes"],
            "total_comprado": float(item["total_comprado"]),
        }
        for item in compras_por_proveedor
    ]

    # Compras por día
    compras_por_dia = (
        ordenes.extra(select={"dia": "DATE(fecha_orden)"})
        .values("dia")
        .annotate(total=Sum("total"), cantidad=Count("id"))
        .order_by("dia")
    )
    compras_por_dia_list = [
        {
            "fecha": item["dia"],
            "total": float(item["total"]),
            "cantidad": item["cantidad"],
        }
        for item in compras_por_dia
    ]

    # Productos más comprados
    productos_comprados = (
        ItemOrdenCompra.objects.filter(
            orden__fecha_orden__date__gte=fecha_inicio,
            orden__fecha_orden__date__lte=fecha_fin,
            orden__estado__in=[
                OrdenCompra.ESTADO_CONFIRMADA,
                OrdenCompra.ESTADO_RECIBIDA,
            ],
        )
        .values("producto__nombre", "producto__codigo")
        .annotate(
            cantidad_comprada=Sum("cantidad"),
            total_comprado=Sum(F("cantidad") * F("precio_unitario") - F("descuento")),
        )
        .order_by("-cantidad_comprada")[:10]
    )
    productos_mas_comprados = [
        {
            "producto": item["producto__nombre"],
            "codigo": item["producto__codigo"],
            "cantidad": item["cantidad_comprada"],
            "total": float(item["total_comprado"]),
        }
        for item in productos_comprados
    ]

    return {
        "total_compras": float(total_compras),
        "cantidad_ordenes": cantidad_ordenes,
        "compras_por_proveedor": compras_por_proveedor_list,
        "compras_por_dia": compras_por_dia_list,
        "productos_mas_comprados": productos_mas_comprados,
        "periodo": {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
        },
    }


def generar_reporte_inventario(search=None, estado=None, stock_bajo=False):
    """
    Genera reporte de inventario (no requiere período)

    Args:
        search: Término de búsqueda (opcional)
        estado: Filtro por estado (opcional)
        stock_bajo: Si es True, solo productos con stock bajo (opcional)

    Returns:
        dict: Datos del reporte de inventario
    """
    from apps.productos.models import Producto, MovimientoInventario
    from django.db.models import Q

    productos = Producto.objects.all()

    # Aplicar filtros si se proporcionan
    if search:
        productos = productos.filter(
            Q(nombre__icontains=search)
            | Q(codigo__icontains=search)
            | Q(descripcion__icontains=search)
        )

    if estado:
        productos = productos.filter(estado=estado)

    if stock_bajo:
        productos = productos.filter(
            stock__lte=F("stock_minimo"), estado=Producto.ESTADO_ACTIVO
        )

    total_productos = productos.count()
    productos_activos = productos.filter(estado=Producto.ESTADO_ACTIVO).count()
    productos_agotados = productos.filter(estado=Producto.ESTADO_AGOTADO).count()
    productos_bajo_stock = productos.filter(
        stock__lte=F("stock_minimo"), estado=Producto.ESTADO_ACTIVO
    ).count()

    # Productos vencidos y próximos a vencer
    productos_vencidos = productos.filter(
        fecha_vencimiento__lt=date.today(), fecha_vencimiento__isnull=False
    ).count()
    productos_proximos_vencer = productos.filter(
        fecha_vencimiento__gte=date.today(),
        fecha_vencimiento__lte=date.today() + timedelta(days=30),
        fecha_vencimiento__isnull=False,
    ).count()

    # Valor total del inventario
    valor_total = productos.aggregate(total=Sum(F("stock") * F("precio")))[
        "total"
    ] or Decimal("0.00")

    # Movimientos recientes (últimos 20)
    movimientos = MovimientoInventario.objects.select_related(
        "producto", "usuario"
    ).order_by("-created_at")[:20]
    movimientos_recientes = [
        {
            "id": mov.id,
            "producto": mov.producto.nombre,
            "codigo": mov.producto.codigo,
            "tipo": mov.get_tipo_display(),
            "cantidad": mov.cantidad,
            "usuario": mov.usuario.get_full_name(),
            "fecha": mov.created_at.isoformat(),
            "motivo": mov.motivo,
        }
        for mov in movimientos
    ]

    # Lista de productos con información relevante
    productos_lista = productos.select_related("categoria", "proveedor").order_by(
        "nombre"
    )  # Incluir todos los productos
    productos_detalle = [
        {
            "nombre": producto.nombre,
            "codigo": producto.codigo,
            "categoria": producto.categoria.nombre
            if producto.categoria
            else "Sin categoría",
            "stock": producto.stock,
            "stock_minimo": producto.stock_minimo,
            "precio": float(producto.precio),
            "estado": producto.get_estado_display(),
            "unidad_medida": producto.unidad_medida,
        }
        for producto in productos_lista
    ]

    return {
        "total_productos": total_productos,
        "productos_activos": productos_activos,
        "productos_agotados": productos_agotados,
        "productos_bajo_stock": productos_bajo_stock,
        "productos_vencidos": productos_vencidos,
        "productos_proximos_vencer": productos_proximos_vencer,
        "valor_total_inventario": float(valor_total),
        "movimientos_recientes": movimientos_recientes,
        "productos": productos_detalle,
    }


def generar_reporte_membresias(fecha_inicio, fecha_fin):
    """
    Genera reporte de membresías para el período especificado

    Returns:
        dict: Datos del reporte de membresías
    """
    from apps.membresias.models import Membresia, InscripcionMembresia
    from apps.core.constants import ESTADO_ACTIVO, ESTADO_VENCIDO

    # Membresías activas
    membresias_activas = Membresia.objects.filter(estado=ESTADO_ACTIVO).count()

    # Membresías vencidas
    membresias_vencidas = Membresia.objects.filter(estado=ESTADO_VENCIDO).count()

    # Nuevas membresías en el período
    nuevas_membresias = Membresia.objects.filter(
        fecha_inicio__gte=fecha_inicio, fecha_inicio__lte=fecha_fin
    ).count()

    # Renovaciones (membresías que se renovaron en el período)
    renovaciones = (
        Membresia.objects.filter(
            created_at__date__gte=fecha_inicio,
            created_at__date__lte=fecha_fin,
        )
        .exclude(fecha_inicio__gte=fecha_inicio)
        .count()
    )

    # Ingresos por membresías en el período
    inscripciones = InscripcionMembresia.objects.filter(
        created_at__date__gte=fecha_inicio, created_at__date__lte=fecha_fin
    )
    ingresos_membresias = inscripciones.aggregate(total=Sum("monto"))[
        "total"
    ] or Decimal("0.00")

    # Membresías por plan
    membresias_por_plan = (
        Membresia.objects.values("plan__nombre")
        .annotate(cantidad=Count("id"))
        .order_by("-cantidad")
    )
    membresias_por_plan_list = [
        {"plan": item["plan__nombre"], "cantidad": item["cantidad"]}
        for item in membresias_por_plan
    ]

    total_membresias = Membresia.objects.count()

    return {
        "total_membresias": total_membresias,
        "membresias_activas": membresias_activas,
        "membresias_vencidas": membresias_vencidas,
        "nuevas_membresias": nuevas_membresias,
        "renovaciones": renovaciones,
        "ingresos_membresias": float(ingresos_membresias),
        "membresias_por_plan": membresias_por_plan_list,
        "periodo": {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
        },
    }


def generar_reporte_financiero(fecha_inicio, fecha_fin):
    """
    Genera reporte financiero consolidado para el período especificado

    Returns:
        dict: Datos del reporte financiero
    """
    from apps.ventas.models import Venta
    from apps.compras.models import OrdenCompra
    from apps.membresias.models import InscripcionMembresia

    # Ingresos
    # Ventas
    ventas = Venta.objects.filter(
        fecha_venta__date__gte=fecha_inicio,
        fecha_venta__date__lte=fecha_fin,
        estado=Venta.ESTADO_COMPLETADA,
    )
    ingresos_ventas = ventas.aggregate(total=Sum("total"))["total"] or Decimal("0.00")

    # Membresías
    inscripciones = InscripcionMembresia.objects.filter(
        created_at__date__gte=fecha_inicio, created_at__date__lte=fecha_fin
    )
    ingresos_membresias = inscripciones.aggregate(total=Sum("monto"))[
        "total"
    ] or Decimal("0.00")

    ingresos_totales = ingresos_ventas + ingresos_membresias

    # Egresos
    # Compras
    compras = OrdenCompra.objects.filter(
        fecha_orden__date__gte=fecha_inicio,
        fecha_orden__date__lte=fecha_fin,
        estado__in=[OrdenCompra.ESTADO_CONFIRMADA, OrdenCompra.ESTADO_RECIBIDA],
    )
    egresos_compras = compras.aggregate(total=Sum("total"))["total"] or Decimal("0.00")

    egresos_totales = egresos_compras

    # Ganancia neta
    ganancia_neta = ingresos_totales - egresos_totales

    return {
        "ingresos_totales": float(ingresos_totales),
        "egresos_totales": float(egresos_totales),
        "ganancia_neta": float(ganancia_neta),
        "ingresos_por_fuente": {
            "ventas": float(ingresos_ventas),
            "membresias": float(ingresos_membresias),
        },
        "egresos_por_categoria": {
            "compras": float(egresos_compras),
        },
        "periodo": {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
        },
    }
