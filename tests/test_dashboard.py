"""Exercise dashboard catalog, official contracts and report integrity."""
from __future__ import annotations
import json
import shutil
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from test_reporting import source
from test_validation_engine import batch
from app import catalog as module
from src.ai_analysis.engine import analyze
from src.reporting.generator import generate


@pytest.fixture
def catalog_case(source: Path, tmp_path: Path) -> tuple[Path, Path]:
    """Copy a valid pipeline output into a fixed isolated catalog root."""
    run_id = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))['pipeline_run_id']
    root = tmp_path / 'project'; directory = root / 'data' / 'processed' / run_id
    directory.parent.mkdir(parents=True); shutil.copytree(source, directory)
    return root, directory


def test_empty_and_unlisted_paths(tmp_path: Path, catalog_case: tuple[Path, Path]) -> None:
    root, directory = catalog_case
    assert module.catalog(tmp_path / 'missing') == []
    entry = module.CatalogEntry('Ejecución local', directory.parent / 'unknown', 'unknown', root)
    with pytest.raises(ValueError): module.read_entry(entry, root)


def test_source_metrics_and_integrity(catalog_case: tuple[Path, Path]) -> None:
    root, directory = catalog_case; entry = module.catalog(root)[0]
    source = module.read_entry(entry, root)
    assert source['summary']['ventas_cop'] == 100 and source['summary']['unidades'] == 1
    (directory / 'daily.csv').unlink()
    with pytest.raises(ValueError): module.read_entry(entry, root)


def test_inconsistent_manifest_is_rejected(catalog_case: tuple[Path, Path]) -> None:
    root, directory = catalog_case; entry = module.catalog(root)[0]
    path = directory / 'manifest.json'; data = json.loads(path.read_text(encoding='utf-8')); data['formula_version'] = 'invalid'; path.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(ValueError): module.read_entry(entry, root)


def test_analysis_and_downloads_match_and_corruption_is_rejected(catalog_case: tuple[Path, Path]) -> None:
    root, directory = catalog_case; entry = module.catalog(root)[0]
    result = analyze(directory, root / 'reports' / 'ai_analysis')
    generated = generate(directory, root / 'reports' / 'ai_enriched', 'both', Path(result['path']))
    official = module.read_entry(entry, root)
    assert module.local_analyses(entry, official)[0][1]['evidence']['ventas']['valor'] == 100
    reports, invalid = module.verified_reports(entry, official)
    assert len(reports) == 1 and invalid == 0 and len(reports[0]['files']) == 2
    report_file = Path(generated['output_dir']) / generated['files'][0]['name']; report_file.write_bytes(b'corrupt')
    reports, invalid = module.verified_reports(entry, official)
    assert not reports and invalid == 1
    report_file.unlink()
    reports, issues = module.report_inventory(entry, official)
    assert not reports and len(issues) == 1 and issues[0]['id']


def test_invalid_analysis_cannot_be_displayed(catalog_case: tuple[Path, Path]) -> None:
    root, directory = catalog_case; entry = module.catalog(root)[0]
    result = analyze(directory, root / 'reports' / 'ai_analysis')
    path = Path(result['path']); data = json.loads(path.read_text(encoding='utf-8')); data['findings'][0]['evidencia']['valor'] = 999
    path.write_text(json.dumps(data), encoding='utf-8')
    assert module.local_analyses(entry, module.read_entry(entry, root)) == []


def test_streamlit_starts_without_unhandled_exceptions() -> None:
    """Smoke-test Streamlit; this does not replace a browser visual review."""
    app = AppTest.from_file(str(module.ROOT / 'app' / 'dashboard.py'), default_timeout=30).run()
    assert not app.exception
    assert app.title and app.title[0].value == 'Resumen ejecutivo'


def test_streamlit_sections_with_isolated_official_source(catalog_case: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Navigate all sections using an isolated source, without executing a pipeline."""
    root, directory = catalog_case
    original_catalog, original_read = module.catalog, module.read_entry
    monkeypatch.setattr(module, 'catalog', lambda *args: original_catalog(root))
    monkeypatch.setattr(module, 'read_entry', lambda entry: original_read(entry, root))
    app = AppTest.from_file(str(module.ROOT / 'app' / 'dashboard.py'), default_timeout=30).run()
    assert not app.exception and any(item.label == 'Ventas netas' and '100' in item.value for item in app.metric)
    for name in ['Análisis comercial', 'Inventarios', 'Recomendaciones', 'Calidad y trazabilidad', 'Informes']:
        app.sidebar.radio[0].set_value(name).run()
        assert not app.exception, name
        assert app.title[0].value == name


def test_colombian_formats_and_missing_values() -> None:
    """Keep presentation formatting separate from the official metrics."""
    from app.dashboard import compact_cop, cop, evidence_number, number, percent

    assert cop(8001670200) == '$ 8.001.670.200 COP'
    assert percent(300.1453225) == '300,15 %'
    assert number(1234.5, 2) == '1.234,50'
    assert cop(None) == 'No disponible'
    assert compact_cop(8001670200) == '$8.001,67 M'
    assert compact_cop(3367158450) == '$3.367,16 M'
    assert evidence_number(6) == '6'
    assert evidence_number(2.5) == '2,50'


def test_table_formatting_keeps_official_columns_and_values() -> None:
    """Formatting must not mutate the original contract data frame."""
    import pandas as pd
    from app.dashboard import display_table

    original = pd.DataFrame({'fecha': ['2026-10-01'], 'ventas_cop': [1250000], 'unidades': [4]})
    formatted = display_table(original)
    assert original.columns.tolist() == ['fecha', 'ventas_cop', 'unidades']
    assert original.loc[0, 'ventas_cop'] == 1250000
    assert formatted.loc[0, 'Ventas netas (COP)'] == '$ 1.250.000 COP'
    assert formatted.loc[0, 'Fecha'] == '01/10/2026'


def test_streamlit_empty_catalog_explains_no_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty catalog should not trigger processing or an unhandled error."""
    monkeypatch.setattr(module, 'catalog', lambda *args: [])
    app = AppTest.from_file(str(module.ROOT / 'app' / 'dashboard.py'), default_timeout=30).run()
    assert not app.exception
    assert any('No hay ejecuciones locales disponibles' in item.value for item in app.info)
