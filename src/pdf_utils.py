import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database import get_config

REPORTES_DIR = "storage/reports"

def generar_pdf(nombre_cliente, carrito, mano_obra):
    os.makedirs(REPORTES_DIR, exist_ok=True)

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Cotizacion_{nombre_cliente}_{fecha}.pdf"
    path = os.path.join(REPORTES_DIR, filename)

    doc = SimpleDocTemplate(path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    logo_path = get_config("logo")
    if logo_path and os.path.exists(logo_path) and logo_path != "":
        try:
            elements.append(Image(logo_path, width=100, height=50))
        except Exception:
            pass  # si hay error en imagen, la omite
    else:
        elements.append(Paragraph("Cotización CCTV", styles["Title"]))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Cliente: {nombre_cliente}", styles["Normal"]))
    elements.append(Paragraph(f"Fecha Elaboración: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Paragraph(f"Fecha Validez: {(datetime.now() + timedelta(days=3)).strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Encabezado tabla
    data = [["Producto", "Tipo", "Precio", "Subtotal"]]

    total_productos = 0
    camaras = 0

    for item in carrito:
        nombre, tipo, precio = item[1], item[2], item[3]
        total_productos += precio
        if tipo.lower() == "cámara":
            camaras += 1
        data.append([nombre, tipo, f"${precio:.2f}", f"${precio:.2f}"])

    total_mano_obra = camaras * mano_obra
    total_final = total_productos + total_mano_obra

    table = Table(data, colWidths=[180, 100, 100, 100])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Totales
    elements.append(Paragraph(f"Subtotal: ${total_productos:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Mano de obra ({camaras} cámaras x ${mano_obra:.2f}): ${total_mano_obra:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Total: ${total_final:.2f}</b>", styles["Title"]))

    doc.build(elements)
    return path
