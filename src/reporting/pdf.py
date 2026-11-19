"""Create an executive PDF using only local ReportLab graphics."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.reporting.theme import AREA, BRAND, COLORS, COMPANY, METHODOLOGY, SLOGAN, quality_status, quality_warning


def display(value: object, suffix: str = "") -> str:
    """Format a display value without replacing missing values with zero."""
    if value is None:
        return "No disponible"
    if isinstance(value, (int, float)):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + suffix
    return str(value) + suffix


def build_pdf(source: dict, destination: Path, generated_at: str) -> None:
    """Build a paginated, deterministic narrative from official outputs."""
    styles = getSampleStyleSheet(); styles["Title"].textColor = colors.HexColor("#" + COLORS["navy"])
    styles["Heading1"].textColor = colors.HexColor("#" + COLORS["petrol"])
    styles["Heading1"].spaceBefore = 8; styles["Heading1"].spaceAfter = 4
    styles["BodyText"].leading = 13
    styles.add(ParagraphStyle("CardLabel", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.HexColor("#" + COLORS["petrol"])))
    styles.add(ParagraphStyle("CardValue", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#" + COLORS["navy"])))
    styles.add(ParagraphStyle("CoverBrand", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=colors.white))
    styles.add(ParagraphStyle("CoverSub", parent=styles["BodyText"], fontSize=10, leading=14, textColor=colors.white))
    story = []; summary, frames = source["summary"], source["frames"]
    def p(text: str, style: str = "BodyText") -> None:
        story.append(Paragraph(escape(text), styles[style])); story.append(Spacer(1, 1.5 * mm))
    def table(rows: list[list[str]], widths: list[float] | None = None) -> None:
        item = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
        item.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#" + COLORS["navy"])), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#" + COLORS["light"])]), ("FONTSIZE", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3)])); story.append(item); story.append(Spacer(1, 3 * mm))
    cover = Table([[Paragraph(BRAND, styles["CoverBrand"])], [Paragraph(escape(SLOGAN), styles["CoverSub"])]], colWidths=[170*mm])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#" + COLORS["navy"])), ("LEFTPADDING", (0, 0), (-1, -1), 18), ("TOPPADDING", (0, 0), (0, 0), 22), ("BOTTOMPADDING", (0, -1), (0, -1), 22)]))
    story.append(cover); story.append(Spacer(1, 14*mm))
    p("Informe ejecutivo comercial", "Heading1"); p(COMPANY + " | " + AREA)
    p(f"Periodo: {source['manifest']['period']['start']} al {source['manifest']['period']['end']}")
    p(f"Fecha de generación: {generated_at}"); p(f"Ejecución: {source['manifest']['pipeline_run_id']}")
    p("EMPRESA Y DATOS FICTICIOS CON FINES ACADÉMICOS.")
    story.append(Spacer(1, 7*mm)); p("Panorama del periodo", "Heading1")
    p("Este informe presenta los resultados comerciales, el desempeño por segmento y el estado de inventario a partir de la ejecución indicada.")
    p(f"Ventas netas: {display(summary['ventas_cop'], ' COP')}  |  Cumplimiento: {display(summary['cumplimiento_pct'], ' %')}")
    story.append(PageBreak()); p("Resumen ejecutivo e indicadores", "Heading1")
    metrics = [("Ventas netas", "ventas_cop", " COP"), ("Unidades", "unidades", ""), ("Presupuesto", "presupuesto_cop", " COP"), ("Cumplimiento", "cumplimiento_pct", " %"), ("Ticket promedio", "ticket_promedio_cop", " COP"), ("Margen bruto", "margen_cop", " COP"), ("Margen porcentual", "margen_pct", " %"), ("Rotación", "rotacion_unidades", " veces")]
    cards = [[ [Paragraph(escape(label.upper()), styles["CardLabel"]), Spacer(1, 4), Paragraph(escape(display(summary[key], suffix)), styles["CardValue"])] for label, key, suffix in metrics[n:n+2]] for n in range(0, len(metrics), 2)]
    card_table = Table(cards, colWidths=[85*mm, 85*mm], hAlign="LEFT")
    card_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#" + COLORS["light"])), ("BOX", (0, 0), (-1, -1), .5, colors.white), ("INNERGRID", (0, 0), (-1, -1), 4, colors.white), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(card_table); story.append(Spacer(1, 4*mm))
    p("El cumplimiento refleja la relación entre ventas y presupuesto de las fuentes simuladas. No se atribuyen causas comerciales.")
    p("Evolución diaria de ventas frente al presupuesto", "Heading1")
    daily = frames["daily"]
    drawing = Drawing(470, 165); chart = VerticalBarChart(); chart.x = 65; chart.y = 30; chart.width = 390; chart.height = 125
    chart.data = [list(daily.ventas_cop.astype(float)), list(daily.presupuesto_cop.astype(float))]
    chart.valueAxis.valueMin = 0
    chart.categoryAxis.categoryNames = [str(x)[-2:] if n % 5 == 0 or n == len(daily) - 1 else "" for n, x in enumerate(daily.fecha)]; chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontSize = 7
    chart.bars[0].fillColor = colors.HexColor("#" + COLORS["petrol"]); chart.bars[1].fillColor = colors.HexColor("#" + COLORS["yellow"])
    drawing.add(chart); story.append(drawing); p("Verde petróleo: ventas. Amarillo: presupuesto. Eje horizontal: día del mes; valores en COP.")
    story.append(PageBreak()); p("Desempeño comercial", "Heading1")
    for name, label, key, limit in [("categories", "Categorías", "categoria", 10), ("cities", "Ciudades", "ciudad", 10), ("stores", "Tiendas con mayores ventas", "tienda_id", 5), ("ranking", "Productos con mayores ventas", "producto_id", 5)]:
        p(label, "Heading2"); data = frames[name].sort_values("ventas_cop", ascending=False).head(limit)
        table([[label, "Ventas netas COP"]] + [[str(row[key]), display(row["ventas_cop"])] for _, row in data.iterrows()], [90*mm, 65*mm])
    story.append(PageBreak()); p("Inventarios y calidad", "Heading1")
    inventory = frames["inventory"]; stockout = int(inventory.agotado.astype(str).str.lower().eq("true").sum())
    low = "No disponible para el total: hay historial incompleto" if inventory.baja_rotacion.isna().any() else str(len(frames["low_rotation"]))
    table([["Indicador al corte", "Resultado"], ["Combinaciones agotadas", str(stockout)], ["Combinaciones de baja rotación", low]], [90*mm, 70*mm])
    p(f"Último lote recibido: {quality_status(source['quality']['validation_status'])}. Calidad del histórico acumulado: no disponible.")
    for warning in source["quality"].get("warnings", []): p("Advertencia del último lote: " + quality_warning(warning))
    p("Conclusiones descriptivas", "Heading1")
    p(f"Las ventas netas del periodo fueron {display(summary['ventas_cop'], ' COP')}; se observaron {stockout} combinaciones agotadas al corte.")
    p("Acciones sugeridas", "Heading1")
    if stockout:
        p("Revisar las combinaciones agotadas identificadas en el detalle de inventario antes de decidir acciones comerciales.")
    else:
        p("Continuar el seguimiento del inventario al cierre y revisar los cambios en próximas ejecuciones.")
    if source["quality"].get("warnings"):
        p("Revisar las advertencias del último lote y confirmar su interpretación comercial antes de distribuir el informe.")
    else:
        p("Verificar las alertas de calidad en la siguiente ejecución antes de distribuir el informe.")
    p("Metodología y limitaciones", "Heading1")
    for item in METHODOLOGY: p(item)
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#" + COLORS["navy"]))
        canvas.drawString(18*mm, 12*mm, "AutoReport360 | Datos ficticios académicos"); canvas.drawRightString(192*mm, 12*mm, str(doc.page))
    SimpleDocTemplate(str(destination), pagesize=(210*mm, 297*mm), leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm).build(story, onFirstPage=footer, onLaterPages=footer)
