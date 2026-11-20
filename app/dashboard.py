"""Local, read-only Streamlit view of validated commercial outputs."""
from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.catalog import catalog, local_analyses, provenance, read_entry, report_inventory


def number(value: object, digits: int = 0) -> str:
    """Format a number with Colombian decimal and grouping separators."""
    if value is None or pd.isna(value): return 'No disponible'
    return f'{float(value):,.{digits}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def cop(value: object) -> str:
    """Format Colombian pesos without altering underlying metrics."""
    return 'No disponible' if value is None or pd.isna(value) else '$ ' + number(value, 0) + ' COP'


def compact_cop(value: object) -> str:
    """Use millions only as display units and retain the exact source value."""
    if value is None or pd.isna(value): return 'No disponible'
    return '$' + number(value / 1_000_000, 2) + ' M' if abs(value) >= 1_000_000 else cop(value)


def exact_cop(value: object) -> str:
    """Show the complete numeric value supplied by the official summary."""
    if value is None or pd.isna(value): return 'No disponible'
    rendered = format(Decimal(str(value)), ',f').replace(',', '_').replace('.', ',').replace('_', '.')
    return '$ ' + rendered + ' COP'


def evidence_number(value: object) -> str:
    """Avoid decimal places for whole evidence quantities."""
    if value is None or pd.isna(value): return 'No disponible'
    return number(value, 0 if float(value).is_integer() else 2)


def display_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Format a copy for Colombian presentation without changing contracts."""
    result = frame.copy()
    for column in result.columns:
        if column.endswith('_cop'):
            result[column] = result[column].map(cop)
        elif column.endswith('_pct'):
            result[column] = result[column].map(percent)
        elif column == 'fecha' or column.startswith('fecha_'):
            result[column] = result[column].map(lambda x: day(str(x)[:10]) if pd.notna(x) else 'No disponible')
        elif pd.api.types.is_integer_dtype(result[column]):
            result[column] = result[column].map(number)
    names = {'tienda_id': 'Código de tienda', 'producto_id': 'Código de producto', 'ventas_cop': 'Ventas netas (COP)', 'presupuesto_cop': 'Presupuesto (COP)', 'unidades': 'Unidades vendidas', 'ciudad': 'Ciudad', 'categoria': 'Categoría', 'fecha': 'Fecha', 'agotado': 'Agotado', 'baja_rotacion': 'Baja rotación'}
    return result.rename(columns={name: names.get(name, name.replace('_', ' ').capitalize()) for name in result.columns})


def percent(value: object) -> str:
    """Format percentages already expressed on a 0–100 scale."""
    return 'No disponible' if value is None or pd.isna(value) else number(value, 2) + ' %'


def day(value: str) -> str:
    """Format an ISO date for local display."""
    return date.fromisoformat(value).strftime('%d/%m/%Y')


def timestamp(value: str) -> str:
    """Display a valid ISO timestamp with a Colombian-style date."""
    try: return datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M %z')
    except (ValueError, AttributeError): return 'Fecha no disponible'


def metric(label: str, value: str, help_text: str | None = None) -> None:
    """Render an executive indicator using the official value."""
    st.metric(label, value, border=True, help=help_text)


def main() -> None:
    """Display data without running any pipeline or modifying its sources."""
    st.set_page_config(page_title='AutoReport360', page_icon='◈', layout='wide', initial_sidebar_state='expanded')
    st.markdown('''<style>
    .stApp {background:#F5F7FA;color:#101E33}
    [data-testid="stSidebar"] {background:#101E33}
    [data-testid="stSidebar"] * {color:#F3F7FA}
    [data-testid="stMetric"] {background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:16px}
    h1,h2,h3 {color:#101E33} a {color:#0C6266}
    .brand-accent {color:#0C6266;font-weight:700;letter-spacing:.08em;font-size:.75rem}
    </style>''', unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('### AutoReport360')
        st.caption('Menos tareas operativas. Más decisiones estratégicas.')
        st.divider()
        page = st.radio('Navegación', ['Resumen ejecutivo', 'Análisis comercial', 'Inventarios', 'Recomendaciones', 'Calidad y trazabilidad', 'Informes'])
        st.divider(); st.caption('Datos ficticios · Consulta local')
    st.markdown('<span class="brand-accent">NOVARETAIL COLOMBIA · INTELIGENCIA COMERCIAL</span>', unsafe_allow_html=True)
    st.title(page)
    entries = catalog()
    if not entries:
        st.info('No hay ejecuciones locales disponibles. El dashboard no ejecuta el procesamiento.'); return
    labels = {f'{e.label} · {e.run_id}': e for e in entries}
    default = 0
    for index, candidate in enumerate(entries):
        try:
            read_entry(candidate); default = index; break
        except Exception: continue
    selected = st.sidebar.selectbox('Ejecución disponible', list(labels), index=default)
    entry = labels[selected]
    try: source = read_entry(entry)
    except Exception:
        st.error('La ejecución seleccionada está incompleta o no supera las validaciones del contrato. Revise el origen local.'); return
    s, frames, manifest = source['summary'], source['frames'], source['manifest']
    st.caption(f"Periodo {day(manifest['period']['start'])} – {day(manifest['period']['end'])} · Corte {day(manifest['cutoff'])} · Información simulada")

    if page == 'Resumen ejecutivo':
        st.caption('M = millones de pesos colombianos (COP).')
        cards = [('Ventas netas', compact_cop(s['ventas_cop']), exact_cop(s['ventas_cop'])), ('Unidades vendidas', number(s['unidades']), None), ('Cumplimiento', percent(s['cumplimiento_pct']), 'Cumplimiento presupuestal del periodo.'), ('Margen bruto', compact_cop(s['margen_cop']), exact_cop(s['margen_cop'])), ('Margen comercial', percent(s['margen_pct']), None), ('Ticket promedio', compact_cop(s['ticket_promedio_cop']), exact_cop(s['ticket_promedio_cop'])), ('Rotación', number(s['rotacion_unidades'], 2) + (' veces' if s['rotacion_unidades'] is not None and not pd.isna(s['rotacion_unidades']) else ''), 'Rotación de inventario por extremos del periodo.')]
        for start in range(0, len(cards), 3):
            cols = st.columns(3)
            for col, (label, value, detail) in zip(cols, cards[start:start + 3]):
                with col: metric(label, value, detail)
        if s['cumplimiento_pct'] is not None and s['cumplimiento_pct'] >= 200:
            st.info('El cumplimiento excepcional corresponde a los datos simulados. Revise la calibración presupuestal sin asumir un error.')
        st.subheader('Evolución diaria · ventas y presupuesto')
        daily = frames['daily'][['fecha', 'ventas_cop', 'presupuesto_cop']].copy()
        chart = daily.copy()
        chart['fecha'] = pd.to_datetime(chart['fecha'])
        chart = chart.set_index('fecha').rename(columns={'ventas_cop': 'Ventas netas', 'presupuesto_cop': 'Presupuesto'})
        st.line_chart(chart, color=['#168C91', '#D8A43A'], x_label='Fecha', y_label='Valor (COP)')
        st.caption('Valores en COP · presupuesto a granularidad de fecha. Consulte los importes con formato colombiano en el detalle.')
        with st.expander('Detalle diario en COP'): st.dataframe(display_table(daily), hide_index=True, width='stretch')

    elif page == 'Análisis comercial':
        st.caption('Cada vista conserva su granularidad original. Los filtros de una tabla no modifican los indicadores generales.')
        choice = st.selectbox('Vista comercial', ['Tiendas', 'Ciudades', 'Categorías', 'Productos'])
        key, dimension = {'Tiendas': ('stores', 'tienda_id'), 'Ciudades': ('cities', 'ciudad'), 'Categorías': ('categories', 'categoria'), 'Productos': ('ranking', 'producto_id')}[choice]
        frame = frames[key].copy().sort_values('ventas_cop', ascending=False)
        options = sorted(frame[dimension].dropna().astype(str).unique().tolist())
        chosen = st.multiselect('Filtrar ' + choice.lower(), options)
        if chosen: frame = frame[frame[dimension].astype(str).isin(chosen)]
        chart = frame.head(15).set_index(dimension)['ventas_cop'].rename('Ventas netas')
        st.bar_chart(chart, color='#168C91', horizontal=True, x_label='Ventas netas (COP)', y_label=choice)
        st.caption('Ventas netas en COP · gráfico limitado a los primeros 15 elementos de la selección.')
        st.dataframe(display_table(frame), hide_index=True, width='stretch')

    elif page == 'Inventarios':
        inv = frames['inventory'].copy()
        agotados = inv.agotado.astype(str).str.lower().eq('true')
        unknown = inv.baja_rotacion.isna()
        cols = st.columns(3)
        with cols[0]: metric('Combinaciones al corte', number(len(inv)))
        with cols[1]: metric('Combinaciones agotadas', number(int(agotados.sum())))
        with cols[2]: metric('Sin historial suficiente', number(int(unknown.sum())))
        st.info('Baja rotación identificada: ' + number(len(frames['low_rotation'])) + ' combinaciones con historial completo.')
        if unknown.any(): st.warning('Hay combinaciones sin historial suficiente: no equivalen a cero casos de baja rotación.')
        stores = sorted(inv.tienda_id.dropna().astype(str).unique().tolist())
        products = sorted(inv.producto_id.dropna().astype(str).unique().tolist())
        selected_stores = st.multiselect('Tiendas', stores); selected_products = st.multiselect('Productos', products)
        if selected_stores: inv = inv[inv.tienda_id.astype(str).isin(selected_stores)]
        if selected_products: inv = inv[inv.producto_id.astype(str).isin(selected_products)]
        view = st.radio('Mostrar', ['Todos', 'Agotados', 'Baja rotación', 'Sin historial suficiente'], horizontal=True)
        if view == 'Agotados': inv = inv[inv.agotado.astype(str).str.lower().eq('true')]
        if view == 'Baja rotación': inv = inv[inv.baja_rotacion.astype(str).str.lower().eq('true')]
        if view == 'Sin historial suficiente': inv = inv[inv.baja_rotacion.isna()]
        st.dataframe(display_table(inv), hide_index=True, width='stretch')
        st.caption('La baja rotación se evalúa con 15 días completos. Un agotado identifica una combinación tienda-producto.')

    elif page == 'Recomendaciones':
        analyses = local_analyses(entry, source)
        if not analyses: st.info('No hay análisis local validado para esta ejecución.'); return
        analyses.sort(key=lambda x: x[1].get('generated_at', ''), reverse=True)
        analysis = analyses[0][1]
        st.subheader('Resumen basado en evidencia'); st.write(analysis['executive_summary'])
        st.caption('Las acciones son sugerencias académicas y requieren evaluación humana.')
        for rec in analysis['recommendations']:
            with st.container(border=True):
                st.markdown('**Prioridad ' + rec['priority'].upper() + ' · ' + rec.get('descripcion', rec['finding_id']) + '**')
                st.write('**Acción sugerida:**', rec['action'])
                evidence = rec.get('evidencia', analysis['evidence'].get(rec['finding_id'], {}))
                st.caption(f"Evidencia: {evidence_number(evidence.get('valor'))} {evidence.get('unidad', '')} · {evidence.get('fuente', '')}")
                if rec.get('responsable_sugerido'): st.caption('Responsable sugerido: ' + rec['responsable_sugerido'] + ' · ' + rec['condiciones_limitaciones'])
        st.subheader('Oportunidades potenciales')
        if not analysis['opportunities']: st.info('No se identificaron oportunidades con las reglas disponibles.')
        for opportunity in analysis['opportunities']: st.write(opportunity['descripcion'])
        with st.expander('Todos los hallazgos y evidencias'): st.json(analysis['findings'])

    elif page == 'Calidad y trazabilidad':
        quality = source['quality']
        trace = provenance(entry)
        cols = st.columns(3)
        with cols[0]: metric('Validación del último lote', quality['validation_status'])
        with cols[1]: metric('Advertencias estadísticas', number(len(quality.get('warnings', []))))
        with cols[2]: metric('Procesamiento', 'Salida validada')
        st.write('**Ejecución de procesamiento:**', manifest['pipeline_run_id'])
        st.write('**Identificador de validación del lote:**', manifest['validation_id'])
        if trace:
            st.write('**Lote recibido:**', trace['batch_id'])
            st.write('**Automatización:**', trace['automation_id'])
            st.write('**Distribución local:**', trace['distribution_status'])
        else: st.caption('No hay metadatos de recepción asociados disponibles en este catálogo.')
        for warning in quality.get('warnings', []):
            label = str(warning).replace('IQR candidates', 'candidatos IQR').replace('_', ' ')
            st.warning('Revisión estadística · ' + label)
        st.info('Las advertencias IQR son candidatos estadísticos, no errores confirmados. La calidad del histórico acumulado no está disponible.')
        with st.expander('Definiciones y limitaciones'):
            st.write('Ticket: ventas netas / transacciones únicas; la simulación usa una línea por transacción. Rotación: unidades vendidas / promedio de inventario por extremos del periodo. Baja rotación: requiere 15 días completos. No hay crecimiento mensual frente a septiembre.')
            st.write('Las fuentes son ficticias; el contrato de salida no autentica por sí solo cambios coordinados en sus archivos.')

    else:
        st.info('Los informes existentes se comprueban antes de habilitar la descarga. PREPARED significa borrador local; no acredita un correo enviado.')
        trace = provenance(entry)
        if trace: st.caption('Estado registrado: ' + trace['distribution_status'])
        reports, issues = report_inventory(entry, source)
        if issues:
            st.warning(f'{len(issues)} generación(es) no pudieron verificarse y no están disponibles para descarga. Las huellas por sí solas no validan el análisis asociado.')
            for issue in issues: st.caption('Histórica no verificada · ' + issue['id'] + ' · ' + issue['reason'])
        if not reports: st.info('No hay informes verificados disponibles para esta ejecución. No se generan informes automáticamente.')
        if reports:
            reports.sort(key=lambda item: item['generated_at'], reverse=True)
            choices = {timestamp(item['generated_at']) + ' · ' + item['id']: item for item in reports}
            report = choices[st.selectbox('Generaciones históricas verificadas', list(choices))]
            cols = st.columns(2)
            for index, item in enumerate(report['files']):
                mime = 'application/pdf' if item['name'].endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                with cols[index]: st.download_button('Descargar ' + ('PDF' if mime == 'application/pdf' else 'Excel'), data=item['bytes'], file_name=item['name'], mime=mime, key=report['id'] + item['name'])


if __name__ == '__main__': main()
