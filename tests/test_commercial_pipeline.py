"""Persistence, recovery and hand-verifiable commercial calculations."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from test_validation_engine import batch
from src.extraction.loader import discover, read_files
from src.validation.rules import validate
from src.validation.engine import state_lock
from src.transformation.storage import connect, persist, read_tables
from src.transformation.commercial import prepare
from src.indicators.commercial import calculate, ratio, summary
from scripts.recover_validation import recover
from scripts.run_pipeline import execute


def clean_batch(batch: Path) -> dict:
    """Load a validated isolated batch."""
    files, errors = discover(batch); assert not errors
    tables, _ = read_files(files); errors, _, clean = validate(tables, files)
    assert not errors
    return clean


def test_persistence_idempotency_rollback_and_fk(batch: Path, tmp_path: Path) -> None:
    tables = clean_batch(batch); db = connect(tmp_path / "db.sqlite")
    assert persist(db, tables, "r1", "v1", {})["ventas"] == 1
    assert persist(db, tables, "r2", "v2", {})["ventas"] == 0
    bad = {k: v.copy() for k, v in tables.items()}
    bad["ventas"].loc[0, "venta_neta_cop"] = 999
    with pytest.raises(ValueError):
        persist(db, bad, "r3", "v3", {})
    assert db.execute("SELECT count(*) FROM persistence_runs WHERE run_id='r3'").fetchone()[0] == 0
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO presupuestos VALUES ('2026-10-02','UNKNOWN',1)")
    db.close()


def test_pipeline_reexecution(batch: Path, tmp_path: Path) -> None:
    state = tmp_path / "state"; out = tmp_path / "output"
    first = execute(batch, state, out); second = execute(batch, state, out)
    assert first["status"] == "SUCCESS" and first["persistence_status"] == "PERSISTED"
    assert second["status"] == "SUCCESS" and second["validation_status"] == "SKIPPED"
    assert second["persistence_status"] == "ALREADY_PERSISTED"
    assert second["summary"]["ventas_cop"] == 100


def test_manual_formulas(batch: Path, tmp_path: Path) -> None:
    db = connect(tmp_path / "db.sqlite"); persist(db, clean_batch(batch), "r1", "v1", {})
    prepared, rec = prepare(read_tables(db)); result = calculate(prepared)
    assert rec["sales_cop_source"] == rec["sales_cop_output"] == 100
    assert rec["cost_cop_source"] == rec["cost_cop_output"] == 50
    assert rec["budget_cop_source"] == rec["budget_cop_output"] == 100
    assert result["summary"]["margen_cop"] == 50
    assert result["summary"]["margen_pct"] == 50
    assert result["summary"]["cumplimiento_pct"] == 100
    assert result["cities"][0]["ventas_cop"] == 100
    assert result["summary"]["rotacion_unidades"] == pytest.approx(1 / 9.5)
    assert result["daily"][0]["crecimiento_diario_pct"] is None
    assert result["inventory"][0]["baja_rotacion"] is None
    assert ratio(3, 0) is None
    assert summary(prepared["sales"].drop(columns="transaccion_id"))["ticket_promedio_cop"] is None
    db.close()


def test_fifteen_days_stockout_and_weekly_growth(batch: Path) -> None:
    tables = clean_batch(batch)
    sales = tables["ventas"].iloc[0:0].copy()
    inventory = pd.concat([tables["inventarios"].assign(fecha=f"2026-10-{d:02}", unidades_vendidas=0, inventario_final=10) for d in range(1, 16)], ignore_index=True)
    budgets = pd.concat([tables["presupuestos"].assign(fecha=f"2026-10-{d:02}") for d in range(1, 16)], ignore_index=True)
    tables.update(ventas=sales, inventarios=inventory, presupuestos=budgets)
    data, _ = prepare(tables); result = calculate(data)
    assert bool(result["inventory"][0]["baja_rotacion"])
    assert result["daily"][-1]["crecimiento_semanal_pct"] is None
    inventory.loc[inventory.fecha == "2026-10-15", "inventario_final"] = 0
    tables["inventarios"] = inventory
    data, _ = prepare(tables); result = calculate(data)
    assert bool(result["inventory"][0]["agotado"])
    assert not bool(result["inventory"][0]["baja_rotacion"])


def test_recovery_does_not_touch_legacy_or_active(tmp_path: Path) -> None:
    state = tmp_path / "state"; state.mkdir()
    db = sqlite3.connect(state / "runs.sqlite3")
    db.execute("CREATE TABLE runs (id TEXT PRIMARY KEY, status TEXT, evidence TEXT)")
    for name, data in (("new", {"recovery_protocol": 1}), ("legacy", {})):
        db.execute("INSERT INTO runs VALUES (?, 'VALIDATING', ?)", (name, json.dumps(data)))
    db.commit(); db.close()
    with state_lock(state):
        with pytest.raises(OSError):
            recover(state)
    result = recover(state)
    assert result == {"recovered": ["new"], "legacy_unmodified": ["legacy"]}


def test_comparable_growth_and_budget_not_multiplied(batch: Path) -> None:
    """Check daily and weekly growth using known totals at separate grains."""
    tables = clean_batch(batch)
    sales, inventory, budgets = [], [], []
    for day in range(1, 15):
        date = f"2026-10-{day:02}"
        value = 100 if day <= 7 else 200
        sales.append(tables["ventas"].assign(fecha=date, transaccion_id=f"V{day}", venta_neta_cop=value))
        inventory.append(tables["inventarios"].assign(fecha=date))
        budgets.append(tables["presupuestos"].assign(fecha=date))
    tables.update(ventas=pd.concat(sales), inventarios=pd.concat(inventory), presupuestos=pd.concat(budgets))
    data, rec = prepare(tables); result = calculate(data)
    assert result["daily"][-1]["crecimiento_semanal_pct"] == 100
    assert result["daily"][7]["crecimiento_diario_pct"] == 100
    assert result["summary"]["presupuesto_cop"] == 1400
    assert rec["budget_cop_output"] == 1400
