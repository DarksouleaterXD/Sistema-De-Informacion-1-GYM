"""
Utilidades para generación de PDFs de reportes
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.utils import timezone


def generar_pdf_reporte(reporte_data, tipo_reporte, periodo_info):
    """
    Genera un PDF de reporte

    Args:
        reporte_data: Datos del reporte
        tipo_reporte: Tipo de reporte (ventas, compras, inventario, etc.)
        periodo_info: Información del período

    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1e40af"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1e40af"),
        spaceAfter=12,
    )

    # Título
    titulos = {
        "ventas": "REPORTE DE VENTAS",
        "compras": "REPORTE DE COMPRAS",
        "inventario": "REPORTE DE INVENTARIO",
        "membresias": "REPORTE DE MEMBRESÍAS",
        "financiero": "REPORTE FINANCIERO",
    }
    elements.append(Paragraph(titulos.get(tipo_reporte, "REPORTE"), title_style))

    # Información del período
    if periodo_info:
        fecha_inicio = periodo_info.get("fecha_inicio", "")
        fecha_fin = periodo_info.get("fecha_fin", "")
        periodo_text = f"Período: {fecha_inicio} - {fecha_fin}"
        elements.append(Paragraph(periodo_text, styles["Normal"]))
        # Convertir fecha de generación a zona horaria de Bolivia
        fecha_generacion = timezone.localtime(timezone.now())
        elements.append(
            Paragraph(
                f"Generado: {fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

    # Generar contenido según el tipo de reporte
    if tipo_reporte == "ventas":
        _agregar_contenido_ventas(elements, reporte_data, heading_style, styles)
    elif tipo_reporte == "compras":
        _agregar_contenido_compras(elements, reporte_data, heading_style, styles)
    elif tipo_reporte == "inventario":
        _agregar_contenido_inventario(elements, reporte_data, heading_style, styles)
    elif tipo_reporte == "membresias":
        _agregar_contenido_membresias(elements, reporte_data, heading_style, styles)
    elif tipo_reporte == "financiero":
        _agregar_contenido_financiero(elements, reporte_data, heading_style, styles)

    # Construir PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer


def _agregar_contenido_ventas(elements, data, heading_style, styles):
    """Agrega contenido del reporte de ventas"""
    # Resumen
    elements.append(Paragraph("RESUMEN", heading_style))
    resumen_data = [
        ["Total de Ventas:", f"${data['total_ventas']:,.2f}"],
        ["Cantidad de Ventas:", str(data["cantidad_ventas"])],
    ]
    resumen_table = Table(resumen_data, colWidths=[3 * inch, 2 * inch])
    resumen_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Ventas por método de pago
    if data.get("ventas_por_metodo_pago"):
        elements.append(Paragraph("VENTAS POR MÉTODO DE PAGO", heading_style))
        metodo_data = [["Método", "Cantidad", "Total"]]
        for metodo, info in data["ventas_por_metodo_pago"].items():
            metodo_data.append(
                [metodo, str(info["cantidad"]), f"${info['total']:,.2f}"]
            )
        metodo_table = Table(metodo_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
        metodo_table.setStyle(_get_table_style())
        elements.append(metodo_table)
        elements.append(Spacer(1, 0.3 * inch))

    # Productos más vendidos
    if data.get("productos_mas_vendidos"):
        elements.append(Paragraph("PRODUCTOS MÁS VENDIDOS", heading_style))
        productos_data = [["Producto", "Cantidad", "Total"]]
        for producto in data["productos_mas_vendidos"][:10]:
            productos_data.append(
                [
                    producto["producto"],
                    str(producto["cantidad"]),
                    f"${producto['total']:,.2f}",
                ]
            )
        productos_table = Table(
            productos_data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch]
        )
        productos_table.setStyle(_get_table_style())
        elements.append(productos_table)


def _agregar_contenido_compras(elements, data, heading_style, styles):
    """Agrega contenido del reporte de compras"""
    elements.append(Paragraph("RESUMEN", heading_style))
    resumen_data = [
        ["Total de Compras:", f"${data['total_compras']:,.2f}"],
        ["Cantidad de Órdenes:", str(data["cantidad_ordenes"])],
    ]
    resumen_table = Table(resumen_data, colWidths=[3 * inch, 2 * inch])
    resumen_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Compras por proveedor
    if data.get("compras_por_proveedor"):
        elements.append(Paragraph("COMPRAS POR PROVEEDOR", heading_style))
        proveedor_data = [["Proveedor", "Órdenes", "Total"]]
        for proveedor in data["compras_por_proveedor"][:10]:
            proveedor_data.append(
                [
                    proveedor["proveedor"],
                    str(proveedor["cantidad_ordenes"]),
                    f"${proveedor['total_comprado']:,.2f}",
                ]
            )
        proveedor_table = Table(
            proveedor_data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch]
        )
        proveedor_table.setStyle(_get_table_style())
        elements.append(proveedor_table)


def _agregar_contenido_inventario(elements, data, heading_style, styles):
    """Agrega contenido del reporte de inventario"""
    elements.append(Paragraph("RESUMEN", heading_style))
    resumen_data = [
        ["Total de Productos:", str(data["total_productos"])],
        ["Productos Activos:", str(data["productos_activos"])],
        ["Productos Agotados:", str(data["productos_agotados"])],
        ["Productos Bajo Stock:", str(data["productos_bajo_stock"])],
        ["Productos Vencidos:", str(data["productos_vencidos"])],
        ["Productos Próximos a Vencer:", str(data["productos_proximos_vencer"])],
        ["Valor Total Inventario:", f"${data['valor_total_inventario']:,.2f}"],
    ]
    resumen_table = Table(resumen_data, colWidths=[3 * inch, 2 * inch])
    resumen_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Lista de productos
    if data.get("productos") and len(data["productos"]) > 0:
        elements.append(Paragraph("LISTA DE PRODUCTOS", heading_style))
        productos_data = [
            [
                "Código",
                "Producto",
                "Categoría",
                "Stock",
                "Stock Mín.",
                "Precio",
                "Estado",
            ]
        ]
        for producto in data["productos"]:
            productos_data.append(
                [
                    producto["codigo"][:15]
                    if len(producto["codigo"]) > 15
                    else producto["codigo"],
                    producto["nombre"][:25]
                    if len(producto["nombre"]) > 25
                    else producto["nombre"],
                    producto["categoria"][:15]
                    if len(producto["categoria"]) > 15
                    else producto["categoria"],
                    str(producto["stock"]),
                    str(producto["stock_minimo"]),
                    f"${producto['precio']:,.2f}",
                    producto["estado"][:12]
                    if len(producto["estado"]) > 12
                    else producto["estado"],
                ]
            )
        productos_table = Table(
            productos_data,
            colWidths=[
                1 * inch,
                2.2 * inch,
                1 * inch,
                0.7 * inch,
                0.7 * inch,
                0.9 * inch,
                0.9 * inch,
            ],
        )
        # Estilo personalizado para la tabla de productos
        productos_table_style = TableStyle(
            [
                # Encabezado
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                # Filas de datos
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
                # Bordes
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (3, 0), (4, -1), "CENTER"),  # Stock y Stock Mín.
                ("ALIGN", (5, 0), (5, -1), "RIGHT"),  # Precio
                ("ALIGN", (0, 0), (0, -1), "LEFT"),  # Código
                ("ALIGN", (1, 0), (1, -1), "LEFT"),  # Producto
                ("ALIGN", (2, 0), (2, -1), "LEFT"),  # Categoría
                ("ALIGN", (6, 0), (6, -1), "CENTER"),  # Estado
                # Alternar colores de filas
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f9fafb")],
                ),
            ]
        )
        productos_table.setStyle(productos_table_style)
        elements.append(productos_table)


def _agregar_contenido_membresias(elements, data, heading_style, styles):
    """Agrega contenido del reporte de membresías"""
    elements.append(Paragraph("RESUMEN", heading_style))
    resumen_data = [
        ["Total de Membresías:", str(data["total_membresias"])],
        ["Membresías Activas:", str(data["membresias_activas"])],
        ["Membresías Vencidas:", str(data["membresias_vencidas"])],
        ["Nuevas Membresías:", str(data["nuevas_membresias"])],
        ["Renovaciones:", str(data["renovaciones"])],
        ["Ingresos por Membresías:", f"${data['ingresos_membresias']:,.2f}"],
    ]
    resumen_table = Table(resumen_data, colWidths=[3 * inch, 2 * inch])
    resumen_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Membresías por plan
    if data.get("membresias_por_plan"):
        elements.append(Paragraph("MEMBRESÍAS POR PLAN", heading_style))
        plan_data = [["Plan", "Cantidad"]]
        for plan in data["membresias_por_plan"]:
            plan_data.append([plan["plan"], str(plan["cantidad"])])
        plan_table = Table(plan_data, colWidths=[3 * inch, 2 * inch])
        plan_table.setStyle(_get_table_style())
        elements.append(plan_table)


def _agregar_contenido_financiero(elements, data, heading_style, styles):
    """Agrega contenido del reporte financiero"""
    elements.append(Paragraph("RESUMEN FINANCIERO", heading_style))
    resumen_data = [
        ["Ingresos Totales:", f"${data['ingresos_totales']:,.2f}"],
        ["Egresos Totales:", f"${data['egresos_totales']:,.2f}"],
        ["Ganancia Neta:", f"${data['ganancia_neta']:,.2f}"],
    ]
    resumen_table = Table(resumen_data, colWidths=[3 * inch, 2 * inch])
    resumen_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 2), (-1, 2), 14),
                ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#1e40af")),
            ]
        )
    )
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Ingresos por fuente
    if data.get("ingresos_por_fuente"):
        elements.append(Paragraph("INGRESOS POR FUENTE", heading_style))
        ingresos_data = [["Fuente", "Total"]]
        for fuente, total in data["ingresos_por_fuente"].items():
            ingresos_data.append([fuente.title(), f"${total:,.2f}"])
        ingresos_table = Table(ingresos_data, colWidths=[3 * inch, 2 * inch])
        ingresos_table.setStyle(_get_table_style())
        elements.append(ingresos_table)
        elements.append(Spacer(1, 0.3 * inch))

    # Egresos por categoría
    if data.get("egresos_por_categoria"):
        elements.append(Paragraph("EGRESOS POR CATEGORÍA", heading_style))
        egresos_data = [["Categoría", "Total"]]
        for categoria, total in data["egresos_por_categoria"].items():
            egresos_data.append([categoria.title(), f"${total:,.2f}"])
        egresos_table = Table(egresos_data, colWidths=[3 * inch, 2 * inch])
        egresos_table.setStyle(_get_table_style())
        elements.append(egresos_table)


def _get_table_style():
    """Retorna un estilo estándar para tablas"""
    return TableStyle(
        [
            # Encabezado
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            # Filas de datos
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            # Bordes
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ]
    )
