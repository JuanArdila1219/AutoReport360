"""Integration and failure tests for local report generation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from openpyxl import load_workbook
from pypdf import PdfReader

from test_validation_engine import batch
from scripts.run_pipeline import execute
from src.reporting.generator import generate


@pytest.fixture
def source(batch: Path, tmp_path: Path) -> Path:
    """Produce a small valid contract via the existing phase-03 pipeline."""
    result = execute(batch, tmp_path / "state", tmp_path / "processed")
    assert result["status"] == "SUCCESS", result
    return Path(result["output"])


def test_excel_pdf_consistency_and_idempotence(source: Path, tmp_path: Path) -> None:
    output = tmp_path / "reports"
    result = generate(source, output, "both")
    assert result["status"] == "SUCCESS" and len(result["files"]) == 2
    folder = Path(result["output_dir"])
    xlsx = next(folder.glob("*.xlsx")); pdf = next(folder.glob("*.pdf"))
    wb = load_workbook(xlsx)
    assert {"Inicio", "Dashboard", "Ventas diarias", "Tiendas", "Ciudades", "Categorías", "Ranking", "Inventarios", "Agotados", "Baja rotación", "Calidad de datos", "Metodología"}.issubset(wb.sheetnames)
    assert len(wb["Dashboard"]._charts) == 6
    assert wb["Dashboard"]["B4"].value == 100
    assert wb["Baja rotación"]["A4"].value == "Fecha"
    assert wb["Baja rotación"]["A5"].value == "No existen registros aplicables."
    assert "No disponible" in str(wb["Dashboard"]["B13"].value)
    wb.close()
    reader = PdfReader(pdf); text = " ".join(page.extract_text() for page in reader.pages)
    assert "100,00 COP" in text and "FICTICIOS" in text
    repeated = generate(source, output, "both")
    assert repeated["status"] == "SKIPPED" and repeated["generation_id"] == result["generation_id"]
    assert len(list(output.glob("*/manifest.json"))) == 1


def test_missing_invalid_manifest_and_inconsistent_data(source: Path, tmp_path: Path) -> None:
    (source / "cities.csv").unlink()
    with pytest.raises(ValueError): generate(source, tmp_path / "out")
    assert not list((tmp_path / "out").glob("*/manifest.json"))


def test_invalid_manifest(source: Path, tmp_path: Path) -> None:
    path = source / "manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8")); manifest["formula_version"] = "9.9"; path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError): generate(source, tmp_path / "out")


def test_failed_write_leaves_no_partial_output(source: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.reporting.generator as module
    def fail(*args: object) -> None: raise OSError("fallo de escritura simulado")
    monkeypatch.setattr(module, "build_pdf", fail)
    with pytest.raises(OSError): generate(source, tmp_path / "out", "both")
    assert not list((tmp_path / "out").glob("*/manifest.json"))
    assert len(list((tmp_path / "out" / ".failures").glob("*.json"))) == 1


def test_modified_output_is_not_overwritten(source: Path, tmp_path: Path) -> None:
    result = generate(source, tmp_path / "out", "excel")
    file = next(Path(result["output_dir"]).glob("*.xlsx")); file.write_bytes(b"alterado")
    with pytest.raises(ValueError): generate(source, tmp_path / "out", "excel")
    assert file.read_bytes() == b"alterado"


def test_unavailable_kpi_is_not_zero(source: Path, tmp_path: Path) -> None:
    path = source / "summary.json"; data = json.loads(path.read_text(encoding="utf-8"))
    data["summary"]["ticket_promedio_cop"] = None
    path.write_text(json.dumps(data), encoding="utf-8")
    result = generate(source, tmp_path / "out", "both")
    workbook = load_workbook(next(Path(result["output_dir"]).glob("*.xlsx")))
    assert workbook["Dashboard"]["B8"].value == "No disponible"
    workbook.close()
    text = " ".join(page.extract_text() for page in PdfReader(next(Path(result["output_dir"]).glob("*.pdf"))).pages)
    assert "No disponible" in text


def test_inconsistent_summary_rejected(source: Path, tmp_path: Path) -> None:
    path = source / "summary.json"; data = json.loads(path.read_text(encoding="utf-8"))
    data["summary"]["ventas_cop"] += 1
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Ventas inconsistentes"):
        generate(source, tmp_path / "out")
