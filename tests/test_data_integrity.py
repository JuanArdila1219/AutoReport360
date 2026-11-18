"""Integration checks for the supplied simulated reference data."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.profile_data import load_data, profile


def test_reference_integrity() -> None:
    """Verify keys, coverage, references and commercial reconciliations."""
    result = profile(load_data())
    assert {k: v["rows"] for k, v in result["tables"].items()} == {
        "tiendas": 30, "productos": 60, "ventas": 38922, "inventarios": 55800, "presupuestos": 930}
    for info in result["tables"].values():
        assert info["duplicate_keys"] == 0
        assert sum(info["nulls"].values()) == 0
        assert sum(info["negative_values"].values()) == 0
    assert all(value == 0 for value in result["checks"].values()), result["checks"]


def test_detects_broken_reference_and_balance() -> None:
    """Detect a missing store reference and an inconsistent inventory balance."""
    tables = load_data()
    tables["ventas"].loc[0, "tienda_id"] = "UNKNOWN"
    tables["inventarios"].loc[0, "inventario_final"] += 1
    result = profile(tables)
    assert result["checks"]["ventas_unknown_store"] == 1
    assert result["checks"]["inventory_balance_errors"] == 1
