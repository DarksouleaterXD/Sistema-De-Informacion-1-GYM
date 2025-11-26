"""
Utilidades para generación de PDFs de Órdenes de Compra
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.utils import timezone


def generar_pdf_orden_compra(orden):
    """
    Genera un PDF de orden de compra

    Args:
        orden: Instancia de OrdenCompra

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

    # Contenedor para elementos del PDF
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#059669"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#059669"),
        spaceAfter=12,
    )

    # Título
    elements.append(Paragraph("ORDEN DE COMPRA", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Información de la orden
    # Convertir fecha_orden (DateTimeField) a zona horaria de Bolivia
    fecha_orden_local = timezone.localtime(orden.fecha_orden)
    # fecha_esperada es DateField, no necesita conversión de timezone
    info_data = [
        ["Número de Orden:", orden.numero_orden],
        ["Fecha de Orden:", fecha_orden_local.strftime("%d/%m/%Y %H:%M")],
        [
            "Fecha Esperada:",
            orden.fecha_esperada.strftime("%d/%m/%Y")
            if orden.fecha_esperada
            else "N/A",
        ],
        ["Estado:", orden.get_estado_display()],
    ]

    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Información del proveedor
    elements.append(Paragraph("DATOS DEL PROVEEDOR", heading_style))
    proveedor_data = [
        ["Razón Social:", orden.proveedor.razon_social],
        ["NIT:", orden.proveedor.nit],
        ["Teléfono:", orden.proveedor.telefono or "N/A"],
        ["Email:", orden.proveedor.email or "N/A"],
        ["Dirección:", orden.proveedor.direccion or "N/A"],
    ]

    proveedor_table = Table(proveedor_data, colWidths=[2 * inch, 4 * inch])
    proveedor_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(proveedor_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Items de la orden
    elements.append(Paragraph("ITEMS DE LA ORDEN", heading_style))

    # Encabezados de la tabla
    items_data = [["Producto", "Cantidad", "Precio Unit.", "Descuento", "Subtotal"]]

    # Agregar items
    for item in orden.items.all():
        items_data.append(
            [
                item.producto.nombre,
                str(item.cantidad),
                f"${item.precio_unitario:.2f}",
                f"${item.descuento:.2f}",
                f"${item.subtotal:.2f}",
            ]
        )

    items_table = Table(
        items_data, colWidths=[2.5 * inch, 0.8 * inch, 1 * inch, 1 * inch, 1 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                # Encabezado
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#059669")),
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
                ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(items_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Totales
    totales_data = [
        ["Subtotal:", f"${orden.subtotal:.2f}"],
        ["Descuento:", f"${orden.descuento:.2f}"],
        ["TOTAL:", f"${orden.total:.2f}"],
    ]

    totales_table = Table(totales_data, colWidths=[4 * inch, 2 * inch])
    totales_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                # Fila de total
                ("FONTSIZE", (0, 2), (-1, 2), 14),
                ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#059669")),
                ("LINEBELOW", (0, 2), (-1, 2), 2, colors.HexColor("#059669")),
            ]
        )
    )
    elements.append(totales_table)

    # Observaciones si existen
    if orden.observaciones:
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("OBSERVACIONES", heading_style))
        elements.append(Paragraph(orden.observaciones, styles["Normal"]))

    # Construir PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer
