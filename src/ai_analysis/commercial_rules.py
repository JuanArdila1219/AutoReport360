"""Deterministic, evidence-bound academic retail recommendations."""
from __future__ import annotations

import re
import pandas as pd


def _identifier(value: object) -> str | None:
    """Accept only compact identifiers for inclusion in output."""
    text = str(value)
    return text if re.fullmatch(r"[A-Za-z0-9_-]{1,30}", text) else None


def enrich(source: dict, config: dict, base: list[dict]) -> dict:
    """Derive recommendations from current evidence without predicting impact."""
    findings = [dict(item) for item in base]
    by_id = {item['id']: item for item in findings}
    summary, frames = source['summary'], source['frames']
    opportunities: list[dict] = []
    recommendations: list[dict] = []

    def recommend(key: str, action: str, owner: str, horizon: str, reason: str, metric: str, limit: str) -> None:
        item = by_id.get(key)
        if item is None:
            return
        item['accion'] = action
        recommendations.append({'id': 'rec_' + key, 'finding_id': key, 'descripcion': item['descripcion'],
            'evidencia': item['evidencia'], 'fuente': item['evidencia']['fuente'], 'justificacion': reason,
            'action': action, 'priority': item['prioridad'], 'responsable_sugerido': owner,
            'horizonte_sugerido': horizon, 'impacto_esperado': 'Mejor información para la decisión comercial',
            'indicador_seguimiento': metric, 'condiciones_limitaciones': limit})

    def add(key: str, description: str, value: object, unit: str, origin: str, priority: str, limit: str) -> None:
        item = {'id': key, 'tipo': 'segmento', 'descripcion': description, 'evidencia': {'valor': value, 'unidad': unit, 'fuente': origin}, 'prioridad': priority, 'accion': '', 'limitacion': limit, 'naturaleza': 'hecho'}
        findings.append(item); by_id[key] = item

    budget = summary.get('cumplimiento_pct')
    if budget is not None and pd.notna(budget):
        if budget < config['budget_target_percent']:
            by_id['presupuesto']['prioridad'] = 'alta'
            recommend('presupuesto', 'Analizar brechas por tienda y revisar el plan comercial.', 'Gerencia comercial', 'Corto plazo', 'El cumplimiento está por debajo de la meta académica.', 'Cumplimiento presupuestal', 'Investigar causas antes de decidir.')
        elif budget >= config['budget_exceptional_percent']:
            by_id['presupuesto']['prioridad'] = 'media'
            recommend('presupuesto', 'Revisar la calibración del presupuesto y validar sus supuestos.', 'Planeación comercial', 'Corto plazo', 'La desviación positiva supera el umbral académico.', 'Cumplimiento presupuestal', 'Una desviación alta no demuestra un error.')
        else:
            opportunities.append({'finding_id': 'presupuesto', 'tipo': 'oportunidad potencial', 'descripcion': 'Examinar prácticas comerciales asociadas al cumplimiento de la meta; no se ha establecido causalidad.'})
    if 'margen' in by_id and summary.get('margen_pct') is not None and summary['margen_pct'] < config['low_margin_percent']:
        recommend('margen', 'Revisar mezcla, precios y costos antes de ajustar el surtido.', 'Gerencia comercial', 'Corto plazo', 'El margen está por debajo del umbral académico.', 'Margen porcentual', 'La relación no establece una causa.')

    inventory = frames['inventory']; stock = inventory[inventory.agotado.astype(str).str.lower().eq('true')]
    affected = []
    if 'inventario_final' in inventory.columns:
        for _, row in stock.iterrows():
            store, product = _identifier(row.tienda_id), _identifier(row.producto_id)
            if not store or not product: continue
            candidates = inventory[(inventory.producto_id == row.producto_id) & (inventory.tienda_id != row.tienda_id) & (pd.to_numeric(inventory.inventario_final, errors='coerce') > 0)]
            affected.append({'tienda_id': store, 'producto_id': product, 'tiendas_candidatas': sorted(filter(None, (_identifier(x) for x in candidates.tienda_id)))})
    if len(stock):
        by_id['agotados']['evidencia']['combinaciones'] = affected
        recommend('agotados', 'Validar existencias y factibilidad de reposición o redistribución para las combinaciones afectadas.', 'Abastecimiento', 'Inmediato', 'Hay combinaciones sin existencias al corte.', 'Combinaciones agotadas', 'Las candidatas muestran saldo positivo, no excedente; faltan mínimos y no se proponen cantidades.')
        if any(x['tiendas_candidatas'] for x in affected):
            opportunities.append({'finding_id': 'agotados', 'tipo': 'oportunidad potencial', 'descripcion': 'Evaluar redistribución desde tiendas candidatas con saldo positivo, sujeta a mínimos y factibilidad.'})
    if 'baja_rotacion' in by_id and by_id['baja_rotacion']['evidencia']['valor'] is None:
        recommend('baja_rotacion', 'Completar el historial antes de evaluar la baja rotación.', 'Analítica de datos', 'Corto plazo', 'La cobertura de historial es insuficiente.', 'Cobertura de historial', 'No asumir ausencia de casos.')
    elif len(frames['low_rotation']) >= config['medium_low_rotation']:
        by_id['baja_rotacion']['prioridad'] = 'media'
        recommend('baja_rotacion', 'Revisar inventario y surtido de las combinaciones identificadas.', 'Gestión de inventarios', 'Corto plazo', 'Existen combinaciones con baja rotación.', 'Combinaciones de baja rotación', 'La definición requiere 15 días completos.')
    if len(source['quality'].get('warnings', [])) >= config['medium_quality_warnings']:
        recommend('calidad', 'Examinar los casos señalados y confirmar su validez comercial.', 'Analítica de datos', 'Corto plazo', 'El último lote presenta advertencias estadísticas.', 'Advertencias del último lote', 'Los valores atípicos no son errores confirmados; no se conoce la calidad acumulada.')
    else:
        by_id['calidad']['prioridad'] = 'baja'

    stores = frames['stores']
    if 'cumplimiento_pct' in stores:
        available = stores.dropna(subset=['cumplimiento_pct'])
        below = available[available.cumplimiento_pct < config['budget_target_percent']]
        if len(below):
            ids = sorted(filter(None, (_identifier(x) for x in below.tienda_id)))
            add('tiendas_bajo_presupuesto', 'Tiendas por debajo de la meta', len(below), 'tiendas', 'stores.csv:cumplimiento_pct', 'media', 'Solo tiendas con indicador disponible.')
            by_id['tiendas_bajo_presupuesto']['evidencia']['tiendas'] = ids
            recommend('tiendas_bajo_presupuesto', 'Revisar presupuestos y ventas de las tiendas identificadas.', 'Gerencia comercial', 'Corto plazo', 'Hay tiendas bajo la meta académica.', 'Cumplimiento por tienda', 'No se atribuyen causas.')
    for key, field, label in [('diario', 'crecimiento_diario_pct', 'diaria'), ('semanal', 'crecimiento_semanal_pct', 'semanal')]:
        item = by_id.get(key)
        if item and abs(item['evidencia']['valor']) >= config['variation_alert_percent']:
            item['prioridad'] = 'media'
            recommend(key, f'Examinar los segmentos asociados a la variación {label}.', 'Inteligencia comercial', 'Corto plazo', 'La variación supera el umbral académico en valor absoluto.', 'Crecimiento ' + label, 'La variación semanal compara dos ventanas consecutivas de siete días completos.')
    ranking = frames['ranking']
    if 'unidades' in ranking and not ranking.empty:
        row = ranking.sort_values('unidades', ascending=False).iloc[0]; ident = _identifier(row.producto_id)
        if ident:
            add('producto_unidades', 'Producto líder en unidades: ' + ident, int(row.unidades), 'unidades', 'ranking.csv:unidades', 'baja', 'Las unidades no implican rentabilidad.')
    for frame, label in [('categories', 'categoría'), ('stores', 'tienda')]:
        table = frames[frame]
        if 'margen_pct' in table and table.margen_pct.notna().any():
            row = table.dropna(subset=['margen_pct']).sort_values('margen_pct').iloc[0]
            add('margen_' + frame, 'Menor margen por ' + label + ' (ver detalle)', float(row.margen_pct), '%', frame + '.csv:margen_pct', 'media' if row.margen_pct < config['low_margin_percent'] else 'baja', 'La rentabilidad por producto no está disponible en el ranking.')
            maximum = table.dropna(subset=['margen_pct']).sort_values('margen_pct').iloc[-1]
            add('margen_max_' + frame, 'Mayor margen por ' + label + ' (ver detalle)', float(maximum.margen_pct), '%', frame + '.csv:margen_pct', 'baja', 'El detalle identifica el segmento.')
    for frame, label in [('stores', 'tiendas'), ('cities', 'ciudades')]:
        table = frames[frame]
        if len(table) > 1:
            gap = int(table.ventas_cop.max() - table.ventas_cop.min())
            add('brecha_' + frame, 'Diferencia de ventas entre ' + label + ' extrema', gap, 'COP', frame + '.csv:ventas_cop', 'baja', 'Los segmentos pueden diferir en tamaño y potencial; no implica causalidad.')
    if summary.get('ventas_cop') and not ranking.empty:
        row = ranking.sort_values('ventas_cop', ascending=False).iloc[0]
        share = 100 * float(row.ventas_cop) / summary['ventas_cop']
        add('concentracion', 'Participación del producto líder en ventas', share, '%', 'ranking.csv:ventas_cop / summary.json:ventas_cop', 'baja', 'Participación descriptiva, no medida de rentabilidad.')

    recommendations.sort(key=lambda x: {'alta': 0, 'media': 1, 'baja': 2}[x['priority']])
    risk_ids = [x['id'] for x in findings if x['prioridad'] == 'alta']
    sales = summary.get('ventas_cop')
    overview = f"Ventas del periodo: {sales:,.0f} COP." if sales is not None else 'Ventas del periodo no disponibles.'
    if budget is not None and pd.notna(budget): overview += f' Cumplimiento: {budget:.2f} %.'
    overview += f' Agotados: {len(stock)} combinaciones. Acciones priorizadas: {len(recommendations)}; oportunidades potenciales: {len(opportunities)}.'
    overview += ' Los datos son ficticios; las causas e impactos futuros no están demostrados.'
    return {'findings': findings, 'recommendations': recommendations, 'risks': risk_ids, 'opportunities': opportunities, 'executive_summary': overview}
