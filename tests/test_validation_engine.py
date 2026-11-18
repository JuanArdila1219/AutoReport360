"""Exercise batch acceptance, rejection, retry and deduplication."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.validation.engine import run_batch


@pytest.fixture
def batch(tmp_path: Path) -> Path:
    """Create an isolated valid one-day example."""
    folder = tmp_path / "input"; folder.mkdir()
    data = {
        "tiendas": [{"tienda_id": "T1", "nombre": "Tienda", "ciudad": "Cali"}],
        "productos": [{"producto_id": "P1", "nombre": "Producto", "categoria": "Textil", "precio_lista_cop": 100, "costo_unitario_cop": 50}],
        "ventas": [{"transaccion_id": "V1", "fecha": "2026-10-01", "tienda_id": "T1", "producto_id": "P1", "unidades": 1, "precio_unitario_cop": 100, "descuento_pct": 0, "venta_neta_cop": 100, "costo_venta_cop": 50}],
        "inventarios": [{"fecha": "2026-10-01", "tienda_id": "T1", "producto_id": "P1", "inventario_inicial": 10, "entradas": 0, "unidades_vendidas": 1, "inventario_final": 9, "costo_unitario_cop": 50}],
        "presupuestos": [{"fecha": "2026-10-01", "tienda_id": "T1", "meta_ventas_cop": 100}],
    }
    for name, rows in data.items():
        pd.DataFrame(rows).to_csv(folder / f"{name}.csv", index=False)
    return folder


def alter(batch: Path, name: str, column: str, value: object) -> None:
    """Change one isolated input field."""
    path = batch / f"{name}.csv"; df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.loc[0, column] = value; df.to_csv(path, index=False)


def test_valid_and_duplicate(batch: Path, tmp_path: Path) -> None:
    state = tmp_path / "state"
    assert run_batch(batch, state)["status"] == "APPROVED"
    assert run_batch(batch, state)["status"] == "SKIPPED"


@pytest.mark.parametrize("case", ["missing", "column", "type", "null", "duplicate", "reference", "date", "amount", "inventory"])
def test_invalid_batches(batch: Path, tmp_path: Path, case: str) -> None:
    path = batch / "ventas.csv"
    if case == "missing":
        path.unlink()
    elif case == "column":
        pd.read_csv(path).drop(columns="unidades").to_csv(path, index=False)
    elif case == "duplicate":
        df = pd.read_csv(path); pd.concat([df, df]).to_csv(path, index=False)
    else:
        name, column, value = {"type": ("ventas", "unidades", "xyz"), "null": ("ventas", "transaccion_id", ""), "reference": ("ventas", "tienda_id", "X"), "date": ("ventas", "fecha", "2026-02-30"), "amount": ("ventas", "venta_neta_cop", "5"), "inventory": ("inventarios", "inventario_final", "4")}[case]
        alter(batch, name, column, value)
    result = run_batch(batch, tmp_path / "state")
    assert result["status"] == "REJECTED", result
    assert result["errors"]


def test_outlier_is_warning(batch: Path, tmp_path: Path) -> None:
    path = batch / "productos.csv"; df = pd.read_csv(path)
    rows = [dict(df.iloc[0], producto_id=f"P{n}") for n in range(2, 6)]
    rows[-1]["precio_lista_cop"] = 100000
    pd.concat([df, pd.DataFrame(rows)]).to_csv(path, index=False)
    # Provide all store/product/day inventory combinations.
    path = batch / "inventarios.csv"; inv = pd.read_csv(path)
    more = [dict(inv.iloc[0], producto_id=f"P{n}", unidades_vendidas=0, inventario_final=10) for n in range(2, 6)]
    pd.concat([inv, pd.DataFrame(more)]).to_csv(path, index=False)
    result = run_batch(batch, tmp_path / "state")
    assert result["status"] == "APPROVED" and result["warnings"]


def test_failed_retry(batch: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.validation.engine as engine
    original = engine.validate
    def fail(*args: object) -> None:
        raise RuntimeError("simulated failure")
    monkeypatch.setattr(engine, "validate", fail)
    assert run_batch(batch, tmp_path / "state")["status"] == "FAILED"
    monkeypatch.setattr(engine, "validate", original)
    assert run_batch(batch, tmp_path / "state")["status"] == "APPROVED"


def test_daily_and_historical_overlap(batch: Path, tmp_path: Path) -> None:
    daily = tmp_path / "daily"; daily.mkdir()
    for name in ("ventas", "inventarios", "presupuestos"):
        (daily / f"{name}_2026-10-01.csv").write_bytes((batch / f"{name}.csv").read_bytes())
    state = tmp_path / "state"
    assert run_batch(batch, state)["status"] == "APPROVED"
    assert run_batch(daily, state, batch)["status"] == "SKIPPED"
    assert run_batch(daily, tmp_path / "new-state", batch)["status"] == "APPROVED"


def test_excel_input(batch: Path, tmp_path: Path) -> None:
    path = batch / "ventas.csv"
    pd.read_csv(path).to_excel(batch / "ventas.xlsx", index=False)
    path.unlink()
    assert run_batch(batch, tmp_path / "state")["status"] == "APPROVED"


def test_changed_approved_key_is_rejected(batch: Path, tmp_path: Path) -> None:
    """Previously approved keys with changed values must not be skipped."""
    state = tmp_path / "state"
    assert run_batch(batch, state)["status"] == "APPROVED"
    alter(batch, "presupuestos", "meta_ventas_cop", "200")
    result = run_batch(batch, state)
    assert result["status"] == "REJECTED" and result["conflicting_keys"] == 1
