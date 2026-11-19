"""Create the commercial workbook using native OpenPyXL objects."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from src.reporting.theme import AREA, BRAND, COLORS, COMPANY, METHODOLOGY, SLOGAN, quality_status, quality_warning

SHEETS = {"daily": "Ventas diarias", "stores": "Tiendas", "cities": "Ciudades", "categories": "Categorías", "ranking": "Ranking", "inventory": "Inventarios", "low_rotation": "Baja rotación"}


def _value(value: object) -> object:
    """Convert missing and NumPy values into safe Excel values."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _sheet(wb: Workbook, title: str, frame: pd.DataFrame, number: int) -> None:
    ws = wb.create_sheet(title); ws.freeze_panes = "B5"; ws.sheet_view.showGridLines = False
    ws["A1"] = f"{BRAND} | {title}"; ws["A1"].font = Font(size=16, bold=True, color=COLORS["navy"])
    ws["A2"] = "← Volver al inicio"; ws["A2"].hyperlink = "#'Inicio'!A1"; ws["A2"].style = "Hyperlink"
    for index, col in enumerate(frame.columns, 1):
        cell = ws.cell(4, index, col.replace("_", " ").capitalize()); cell.fill = PatternFill("solid", fgColor=COLORS["navy"]); cell.font = Font(color="FFFFFF", bold=True)
        ws.column_dimensions[get_column_letter(index)].width = min(30, max(15, len(col) + 3))
    for row_index, row in enumerate(frame.itertuples(index=False, name=None), 5):
        for col_index, value in enumerate(row, 1):
            cell = ws.cell(row_index, col_index, _value(value))
            key = str(frame.columns[col_index - 1])
            if key.endswith("_cop"):
                cell.number_format = '#,##0.00 "COP"' if "promedio" in key else '#,##0 "COP"'
            elif key.endswith("_pct"):
                cell.number_format = '0.00"%"'
            if row_index % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=COLORS["light"])
    if frame.empty:
        ws.cell(5, 1, "No existen registros aplicables.").font = Font(italic=True, color="64748B")
    else:
        end = f"{get_column_letter(len(frame.columns))}{len(frame) + 4}"
        table = Table(displayName=f"Tabla{number}", ref=f"A4:{end}")
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False, showFirstColumn=False, showLastColumn=False)
        ws.add_table(table)
    ws.auto_filter.ref = f"A4:{get_column_letter(len(frame.columns))}{max(5, len(frame) + 4)}"


def build_excel(source: dict, destination: Path, generated_at: str) -> None:
    """Write a workbook with dashboard, detail sheets and six native charts."""
    wb = Workbook(); home = wb.active; home.title = "Inicio"; home.sheet_view.showGridLines = False
    for col in range(1, 10): home.column_dimensions[get_column_letter(col)].width = 15
    home.sheet_properties.pageSetUpPr.fitToPage = True
    home.merge_cells("B2:I3"); home["B2"] = BRAND; home["B2"].font = Font(name="Aptos Display", size=27, bold=True, color=COLORS["white"]); home["B2"].alignment = Alignment(vertical="center", indent=1)
    for row in home["B2:I3"]:
        for cell in row: cell.fill = PatternFill("solid", fgColor=COLORS["navy"])
    home.merge_cells("B4:I4"); home["B4"] = SLOGAN; home["B4"].font = Font(name="Aptos", size=12, italic=True, color=COLORS["petrol"])
    home.merge_cells("B6:I6"); home["B6"] = "REPORTE COMERCIAL"; home["B6"].font = Font(name="Aptos", size=15, bold=True, color=COLORS["navy"])
    for row, text in [(8, COMPANY), (9, AREA), (10, f"Periodo: {source['manifest']['period']['start']} al {source['manifest']['period']['end']}"), (11, f"Generado: {generated_at}"), (12, f"Ejecución: {source['manifest']['pipeline_run_id']}"), (13, "Empresa y datos ficticios con fines académicos")]:
        home.merge_cells(start_row=row, start_column=2, end_row=row, end_column=9)
        home.cell(row, 2, text).font = Font(name="Aptos", size=11, color=COLORS["petrol"] if row == 13 else COLORS["navy"], bold=row in (8, 13))
    home.merge_cells("B15:I15"); home["B15"] = "EXPLORAR EL INFORME"; home["B15"].font = Font(name="Aptos", bold=True, color=COLORS["petrol"], size=11)
    dash = wb.create_sheet("Dashboard"); dash.sheet_view.showGridLines = False; dash.sheet_view.zoomScale = 65; dash.freeze_panes = "A4"
    dash.column_dimensions["A"].hidden = True; dash.column_dimensions["B"].hidden = True; dash.column_dimensions["C"].width = 3
    for col in range(4, 24): dash.column_dimensions[get_column_letter(col)].width = 13
    dash.merge_cells("D1:W2"); dash["D1"] = "PANEL COMERCIAL  |  " + COMPANY; dash["D1"].font = Font(name="Aptos Display", size=17, bold=True, color="FFFFFF"); dash["D1"].alignment = Alignment(vertical="center", indent=1)
    for row in dash["D1:W2"]:
        for cell in row: cell.fill = PatternFill("solid", fgColor=COLORS["navy"])
    dash["D3"] = "← Volver al inicio"; dash["D3"].hyperlink = "#'Inicio'!A1"; dash["D3"].style = "Hyperlink"
    dash.merge_cells("I3:W3"); dash["I3"] = f"{source['manifest']['period']['start']} al {source['manifest']['period']['end']}  |  Datos ficticios académicos"; dash["I3"].font = Font(name="Aptos", size=10, color=COLORS["petrol"]); dash["I3"].alignment = Alignment(horizontal="right")
    summary, frames = source["summary"], source["frames"]
    unavailable = frames["inventory"].baja_rotacion.isna().any()
    cards = [("Ventas netas (COP)", summary["ventas_cop"]), ("Unidades vendidas", summary["unidades"]), ("Cumplimiento (%)", summary["cumplimiento_pct"]), ("Presupuesto (COP)", summary["presupuesto_cop"]), ("Ticket promedio (COP)", summary["ticket_promedio_cop"]), ("Margen bruto (COP)", summary["margen_cop"]), ("Margen (%)", summary["margen_pct"]), ("Rotación (veces)", summary["rotacion_unidades"]), ("Agotados", int(frames["inventory"].agotado.astype(str).str.lower().eq("true").sum())), ("Baja rotación", "No disponible: historial incompleto" if unavailable else len(frames["low_rotation"]))]
    for row, (label, value) in enumerate(cards, 4):
        dash.cell(row, 1, label); dash.cell(row, 2, _value(value) if value is not None else "No disponible")
        dash.cell(row, 1).font = Font(bold=True, color=COLORS["navy"]); dash.cell(row, 2).fill = PatternFill("solid", fgColor=COLORS["light"])
        if isinstance(value, (int, float)): dash.cell(row, 2).number_format = '#,##0.00' if isinstance(value, float) else '#,##0'
    # Preserve the original KPI cells and values; the card layout only adds visual copies.
    for index, (label, value) in enumerate(cards):
        col = 4 + (index % 5) * 4; row = 5 if index < 5 else 9
        left, right = get_column_letter(col), get_column_letter(col + 3)
        dash.merge_cells(f"{left}{row}:{right}{row}"); dash.merge_cells(f"{left}{row+1}:{right}{row+2}")
        for line in dash.iter_rows(min_row=row, max_row=row+2, min_col=col, max_col=col+3):
            for cell in line: cell.fill = PatternFill("solid", fgColor=COLORS["light"]); cell.border = Border(bottom=Side(style="thin", color="D9E4EC"))
        label_cell = dash.cell(row, col, label.upper()); label_cell.font = Font(name="Aptos", size=9, bold=True, color=COLORS["petrol"]); label_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        value_cell = dash.cell(row+1, col, _value(value) if value is not None else "No disponible")
        value_cell.font = Font(name="Aptos Display", size=18 if not isinstance(value, str) else 11, bold=True, color=COLORS["navy"]); value_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1, wrap_text=True)
        if isinstance(value, (float, int)):
            value_cell.number_format = '#,##0.00"%"' if "(%)" in label else '#,##0.00 "COP"' if label == "Ticket promedio (COP)" else '#,##0.00,, "M COP"' if "(COP)" in label else '#,##0.00' if isinstance(value, float) else '#,##0'
    for idx, (name, title) in enumerate(SHEETS.items(), 1):
        _sheet(wb, title, frames[name], idx)
    exhausted = frames["inventory"][frames["inventory"].agotado.astype(str).str.lower().eq("true")]
    _sheet(wb, "Agotados", exhausted, 8)
    quality = pd.DataFrame([{"ámbito": "Último lote", "estado": quality_status(source["quality"]["validation_status"]), "detalle": quality_warning(x)} for x in source["quality"].get("warnings", [])] or [{"ámbito": "Último lote", "estado": quality_status(source["quality"]["validation_status"]), "detalle": "Sin advertencias registradas"}])
    quality.loc[len(quality)] = ["Histórico acumulado", "No disponible", "La fuente no proporciona una evaluación acumulada"]
    _sheet(wb, "Calidad de datos", quality, 9)
    _sheet(wb, "Metodología", pd.DataFrame({"criterio": METHODOLOGY}), 10)
    wb["Metodología"].column_dimensions["A"].width = 110
    wb["Calidad de datos"].column_dimensions["C"].width = 70
    # The chart data sheets are references to existing details; no KPI is recalculated.
    def chart(sheet_name: str, labels: str, values: list[str], title: str, anchor: str, chart_type: str = "bar", limit: int | None = None) -> None:
        ws = wb[sheet_name]; headers = {ws.cell(4, c).value.lower(): c for c in range(1, ws.max_column + 1)}
        count = min(ws.max_row, (limit + 4) if limit else ws.max_row)
        if count < 5: return
        graph = LineChart() if chart_type == "line" else BarChart()
        graph.title = title; graph.height = 7; graph.width = 15
        for key in values:
            graph.add_data(Reference(ws, min_col=headers[key], min_row=4, max_row=count), titles_from_data=True)
        graph.set_categories(Reference(ws, min_col=headers[labels], min_row=5, max_row=count))
        for series, color in zip(graph.series, (COLORS["petrol"], COLORS["yellow"])):
            series.graphicalProperties.line.solidFill = color
            if chart_type != "line": series.graphicalProperties.solidFill = color
        dash.add_chart(graph, anchor)
    chart("Ventas diarias", "fecha", ["ventas cop", "presupuesto cop"], "Ventas y presupuesto diario (COP)", "D14", "line")
    chart("Categorías", "categoria", ["ventas cop"], "Ventas por categoría (COP)", "N14")
    chart("Ciudades", "ciudad", ["ventas cop"], "Ventas por ciudad (COP)", "D29")
    # Sort a private chart-only sheet to keep the full official store detail intact.
    chart_data = wb.create_sheet("Datos gráficos"); chart_data.sheet_state = "hidden"
    top = frames["stores"].sort_values("ventas_cop", ascending=False).head(10)
    chart_data.append(["tienda", "ventas cop"])
    for row in top.itertuples(): chart_data.append([_value(row.tienda_id), int(row.ventas_cop)])
    graph = BarChart(); graph.title = "Top 10 tiendas (COP)"; graph.height = 7; graph.width = 15
    graph.add_data(Reference(chart_data, min_col=2, min_row=1, max_row=len(top)+1), titles_from_data=True); graph.set_categories(Reference(chart_data, min_col=1, min_row=2, max_row=len(top)+1)); graph.series[0].graphicalProperties.solidFill = COLORS["petrol"]; dash.add_chart(graph, "N29")
    chart("Ranking", "producto id", ["ventas cop"], "Top 10 productos (COP)", "D44", limit=10)
    chart_data["D1"] = "Componente"; chart_data["E1"] = "COP"; chart_data["D2"] = "Margen"; chart_data["E2"] = summary["margen_cop"]; chart_data["D3"] = "Costo"; chart_data["E3"] = summary["costo_cop"]
    pie = PieChart(); pie.title = "Composición de ventas"; pie.height = 7; pie.width = 15
    pie.add_data(Reference(chart_data, min_col=5, min_row=1, max_row=3), titles_from_data=True); pie.set_categories(Reference(chart_data, min_col=4, min_row=2, max_row=3)); dash.add_chart(pie, "N44")
    dash.conditional_formatting.add("B6", CellIsRule(operator="lessThan", formula=["100"], fill=PatternFill("solid", fgColor=COLORS["yellow"])))
    conclusions = wb.create_sheet("Conclusiones ejecutivas")
    conclusions.sheet_view.showGridLines = False; conclusions.column_dimensions["A"].width = 5; conclusions.column_dimensions["B"].width = 115
    conclusions.merge_cells("B2:H3"); conclusions["B2"] = "CONCLUSIONES EJECUTIVAS"; conclusions["B2"].font = Font(name="Aptos Display", size=17, bold=True, color="FFFFFF"); conclusions["B2"].alignment = Alignment(vertical="center", indent=1)
    for line in conclusions["B2:H3"]:
        for cell in line: cell.fill = PatternFill("solid", fgColor=COLORS["navy"])
    conclusions["B4"] = "← Volver al inicio"; conclusions["B4"].hyperlink = "#'Inicio'!A1"; conclusions["B4"].style = "Hyperlink"
    def formatted(value: object, suffix: str = "") -> str:
        if value is None or pd.isna(value): return "no disponible"
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + suffix
    findings = [f"Ventas netas del periodo: {formatted(summary['ventas_cop'], ' COP')}; cumplimiento presupuestal: {formatted(summary['cumplimiento_pct'], ' %')}.",
                f"Ticket promedio: {formatted(summary['ticket_promedio_cop'], ' COP')}; margen bruto: {formatted(summary['margen_cop'], ' COP')} ({formatted(summary['margen_pct'], ' %')}).",
                f"Rotación de inventario: {formatted(summary['rotacion_unidades'], ' veces')}. El promedio de inventario utiliza los extremos del periodo.",
                f"Al corte se registran {cards[8][1]} combinaciones agotadas. Baja rotación: {cards[9][1]}.",
                "Los resultados corresponden a datos ficticios. Las advertencias registradas describen el último lote; la calidad acumulada no está disponible."]
    for row, text in enumerate(findings, 6):
        conclusions.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
        cell = conclusions.cell(row, 2, text); cell.font = Font(name="Aptos", size=11, color=COLORS["navy"]); cell.alignment = Alignment(vertical="center", wrap_text=True, indent=1); cell.fill = PatternFill("solid", fgColor=COLORS["light"] if row % 2 == 0 else COLORS["white"]); conclusions.row_dimensions[row].height = 35
    for index, name in enumerate(["Dashboard"] + list(SHEETS.values()) + ["Agotados", "Calidad de datos", "Metodología", "Conclusiones ejecutivas"], 17):
        home.merge_cells(start_row=index, start_column=2, end_row=index, end_column=4)
        cell = home.cell(index, 2, "→  " + name); cell.hyperlink = f"#'{name}'!A1"; cell.style = "Hyperlink"; home.row_dimensions[index].height = 21
    wb.save(destination)
