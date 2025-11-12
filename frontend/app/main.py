from flask import Flask, render_template, request, send_file, abort, jsonify
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import os

app = Flask(__name__)
API_URL = os.getenv('API_URL', 'http://backend:8000')


@app.route('/')
def index():
    """Página principal del generador de facturas"""
    return render_template('index.html')


@app.route('/api/factura/<numero_factura>')
def obtener_factura(numero_factura):
    """Endpoint para obtener datos de factura desde el backend"""
    try:
        response = requests.get(f'{API_URL}/facturas/v1/{numero_factura}', timeout=10)
        
        if response.status_code != 200:
            return jsonify({"error": "Factura no encontrada"}), 404
            
        return jsonify(response.json())
        
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Error de conexión con el servidor"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Tiempo de espera agotado"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    """Genera y descarga un PDF de la factura"""
    try:
        numero_factura = request.form.get('numero_factura')
        
        if not numero_factura:
            abort(400, description="Número de factura requerido")
        
        # Obtener datos de la factura desde el backend
        response = requests.get(f'{API_URL}/facturas/v1/{numero_factura}', timeout=10)
        
        if response.status_code != 200:
            abort(404, description="Factura no encontrada")
            
        factura = response.json()
        
        # Crear buffer y documento PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30*mm, bottomMargin=20*mm)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6*mm,
            alignment=TA_CENTER
        )
        style_heading = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=3*mm
        )
        style_normal = styles['Normal']
        
        # Título
        elements.append(Paragraph("FACTURA DE VENTA", style_title))
        elements.append(Paragraph(f"Número: {factura['numero_factura']}", style_heading))
        elements.append(Paragraph(f"Fecha: {factura['fecha']}", style_normal))
        elements.append(Spacer(1, 8*mm))
        
        # Información de la empresa
        elements.append(Paragraph("ELECTRODOMÉSTICOS HACEB", style_heading))
        empresa_data = [
            ["NIT:", "900.123.456-7"],
            ["Dirección:", "Carrera 50 #12-34, Medellín, Colombia"],
            ["Teléfono:", "+57 (4) 444-5555"],
            ["Email:", "ventas@haceb.com.co"]
        ]
        tabla_empresa = Table(empresa_data, colWidths=[40*mm, 120*mm])
        tabla_empresa.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(tabla_empresa)
        elements.append(Spacer(1, 6*mm))
        
        # Información del cliente
        elements.append(Paragraph("DATOS DEL CLIENTE", style_heading))
        cliente_data = [
            ["Nombre:", factura['cliente_nombre']],
            ["Documento:", str(factura['cliente_documento'])],
            ["Dirección:", factura['cliente_direccion']],
            ["Teléfono:", factura['cliente_telefono']],
            ["Email:", factura['cliente_email']]
        ]
        tabla_cliente = Table(cliente_data, colWidths=[40*mm, 120*mm])
        tabla_cliente.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(tabla_cliente)
        elements.append(Spacer(1, 8*mm))
        
        # Detalle de productos
        elements.append(Paragraph("DETALLE DE PRODUCTOS", style_heading))
        
        # Encabezados de la tabla de productos
        productos_data = [['Código', 'Producto', 'Cant.', 'Precio Unit.', 'Subtotal']]
        
        # Agregar productos
        for producto in factura['productos']:
            productos_data.append([
                producto['codigo'],
                producto['nombre'],
                str(producto['cantidad']),
                f"${producto['precio_unitario']:,.0f}",
                f"${producto['subtotal']:,.0f}"
            ])
        
        tabla_productos = Table(
            productos_data, 
            colWidths=[25*mm, 70*mm, 15*mm, 30*mm, 30*mm]
        )
        tabla_productos.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Cuerpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))
        elements.append(tabla_productos)
        elements.append(Spacer(1, 6*mm))
        
        # Totales
        totales_data = [
            ['Subtotal:', f"${factura['subtotal']:,.0f}"],
            ['IVA (19%):', f"${factura['iva']:,.0f}"],
            ['TOTAL:', f"${factura['total']:,.0f}"]
        ]
        
        tabla_totales = Table(totales_data, colWidths=[140*mm, 30*mm])
        tabla_totales.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 10),
            ('FONTSIZE', (0, 2), (-1, 2), 12),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#2c3e50')),
            ('LINEABOVE', (0, 2), (-1, 2), 1.5, colors.HexColor('#34495e')),
            ('TOPPADDING', (0, 2), (-1, 2), 6),
        ]))
        elements.append(tabla_totales)
        
        # Pie de página
        elements.append(Spacer(1, 10*mm))
        style_footer = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#95a5a6'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph(
            "Gracias por su compra. Para soporte técnico visite www.haceb.com.co", 
            style_footer
        ))
        
        # Generar el documento
        doc.build(elements)
        buffer.seek(0)
        
        # Retornar el PDF para descargar
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'factura_{numero_factura}.pdf',
            mimetype='application/pdf'
        )
        
    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")
    except requests.exceptions.Timeout:
        abort(504, description="Tiempo de espera agotado")
    except Exception as e:
        abort(500, description=str(e))


@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({"status": "ok", "service": "frontend-facturas"})


if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=3000, debug=debug_mode)

