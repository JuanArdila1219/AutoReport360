"""Independent business scenarios for the prescriptive analysis."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import pytest
from test_reporting import source
from test_validation_engine import batch
from src.reporting.source import load_source
from src.ai_analysis.engine import DEFAULT_CONFIG, build_findings
from src.ai_analysis.commercial_rules import enrich


@pytest.fixture
def scenario(source: Path) -> tuple[dict, dict]:
    return load_source(source), json.loads(DEFAULT_CONFIG.read_text(encoding='utf-8'))


def result(source: dict, config: dict) -> dict:
    return enrich(source, config, build_findings(source, config))


@pytest.mark.parametrize(('value', 'priority', 'text'), [(80, 'alta', 'brechas'), (250, 'media', 'calibración')])
def test_budget_scenarios(scenario: tuple[dict, dict], value: int, priority: str, text: str) -> None:
    s, c = scenario; s['summary']['cumplimiento_pct'] = value
    r = result(s, c); recommendation = next(x for x in r['recommendations'] if x['finding_id'] == 'presupuesto')
    assert recommendation['priority'] == priority and text in recommendation['action']


def test_low_margin_and_prioritization(scenario: tuple[dict, dict]) -> None:
    s, c = scenario; s['summary']['margen_pct'] = 5; s['summary']['cumplimiento_pct'] = 50
    r = result(s, c)
    assert any(x['finding_id'] == 'margen' for x in r['recommendations'])
    order = {'alta': 0, 'media': 1, 'baja': 2}
    assert [order[x['priority']] for x in r['recommendations']] == sorted(order[x['priority']] for x in r['recommendations'])
    assert all(x['evidencia'] == next(y['evidencia'] for y in r['findings'] if y['id'] == x['finding_id']) for x in r['recommendations'])


@pytest.mark.parametrize('candidate', [True, False])
def test_stockout_replenishment_is_conditional(scenario: tuple[dict, dict], candidate: bool) -> None:
    s, c = scenario; inv = s['frames']['inventory']; row = inv.iloc[0].copy(); row['tienda_id'] = 'T2'; row['inventario_final'] = 3 if candidate else 0; row['agotado'] = False
    inv.loc[inv.index[0], 'agotado'] = True; inv.loc[inv.index[0], 'inventario_final'] = 0
    s['frames']['inventory'] = pd.concat([inv, row.to_frame().T], ignore_index=True)
    r = result(s, c); item = next(x for x in r['findings'] if x['id'] == 'agotados')
    assert bool(item['evidencia']['combinaciones'][0]['tiendas_candidatas']) is candidate
    assert any(x['finding_id'] == 'agotados' for x in r['opportunities']) is candidate
    assert 'no se proponen cantidades' in next(x for x in r['recommendations'] if x['finding_id'] == 'agotados')['condiciones_limitaciones']


def test_low_rotation_and_missing_history(scenario: tuple[dict, dict]) -> None:
    s, c = scenario; inv = s['frames']['inventory']; inv['baja_rotacion'] = inv['baja_rotacion'].astype(object); inv.loc[inv.index[0], 'baja_rotacion'] = True
    s['frames']['low_rotation'] = inv.iloc[[0]].copy()
    assert any(x['finding_id'] == 'baja_rotacion' for x in result(s, c)['recommendations'])
    inv.loc[inv.index[0], 'baja_rotacion'] = None
    assert next(x for x in result(s, c)['findings'] if x['id'] == 'baja_rotacion')['evidencia']['valor'] is None


@pytest.mark.parametrize('variation', [-20, 20])
def test_variations(scenario: tuple[dict, dict], variation: int) -> None:
    s, c = scenario; s['frames']['daily'].loc[s['frames']['daily'].index[-1], 'crecimiento_diario_pct'] = variation
    assert any(x['finding_id'] == 'diario' for x in result(s, c)['recommendations'])


def test_missing_indicators_and_no_opportunities(scenario: tuple[dict, dict]) -> None:
    s, c = scenario; s['summary']['cumplimiento_pct'] = None; s['summary']['margen_pct'] = None
    s['frames']['inventory']['agotado'] = False
    r = result(s, c)
    assert not r['opportunities'] and not any(x['id'] in {'margen', 'presupuesto'} for x in r['findings'])


def test_budget_opportunity_and_config(scenario: tuple[dict, dict]) -> None:
    s, c = scenario; s['summary']['cumplimiento_pct'] = 120
    assert any(x['finding_id'] == 'presupuesto' for x in result(s, c)['opportunities'])
    c['budget_exceptional_percent'] = 110
    assert any(x['finding_id'] == 'presupuesto' for x in result(s, c)['recommendations'])
