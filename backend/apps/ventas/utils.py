"""
Utilidades para generación de PDFs de Ventas
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings


def generar_pdf_venta(venta):
    """
    Genera un PDF de factura/recibo para una venta
    
    Args:
        venta: Instancia de Venta
        
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Contenedor para elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12
    )
    
    # Título
    elements.append(Paragraph("FACTURA / RECIBO", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información de la venta
    info_data = [
        ['Número de Venta:', venta.numero_venta],
        ['Fecha:', venta.fecha_venta.strftime('%d/%m/%Y %H:%M')],
        ['Estado:', venta.get_estado_display()],
        ['Método de Pago:', venta.get_metodo_pago_display()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del cliente
    elements.append(Paragraph("DATOS DEL CLIENTE", heading_style))
    cliente_data = [
        ['Nombre:', venta.cliente.nombre_completo],
        ['Cédula:', venta.cliente.ci],
        ['Teléfono:', venta.cliente.telefono or 'N/A'],
        ['Email:', venta.cliente.email or 'N/A'],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detalles de la venta
    elements.append(Paragraph("DETALLES DE LA VENTA", heading_style))
    
    # Encabezados de la tabla
    detalles_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Descuento', 'Subtotal']]
    
    # Agregar detalles
    for detalle in venta.detalles.all():
        detalles_data.append([
            detalle.producto.nombre,
            str(detalle.cantidad),
            f"${detalle.precio_unitario:.2f}",
            f"${detalle.descuento:.2f}",
            f"${detalle.subtotal:.2f}"
        ])
    
    detalles_table = Table(detalles_data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
    detalles_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Filas de datos
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
    ]))
    elements.append(detalles_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totales
    totales_data = [
        ['Subtotal:', f"${venta.subtotal:.2f}"],
        ['Descuento:', f"${venta.descuento:.2f}"],
        ['TOTAL:', f"${venta.total:.2f}"],
    ]
    
    totales_table = Table(totales_data, colWidths=[4*inch, 2*inch])
    totales_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        # Fila de total
        ('FONTSIZE', (0, 2), (-1, 2), 14),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#1e40af')),
        ('LINEBELOW', (0, 2), (-1, 2), 2, colors.HexColor('#1e40af')),
    ]))
    elements.append(totales_table)
    
    # Observaciones si existen
    if venta.observaciones:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("OBSERVACIONES", heading_style))
        elements.append(Paragraph(venta.observaciones, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

