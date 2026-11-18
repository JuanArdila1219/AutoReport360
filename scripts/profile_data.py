"""Profile the original simulated data without modifying source files."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.validation.statistics import iqr_outlier_count
DATA = ROOT / "data" / "simulated"
KEYS = {"tiendas": ["tienda_id"], "productos": ["producto_id"],
        "ventas": ["transaccion_id"], "inventarios": ["fecha", "tienda_id", "producto_id"],
        "presupuestos": ["fecha", "tienda_id"]}


def load_data(path: Path = DATA) -> dict[str, pd.DataFrame]:
    """Read the five expected CSV files or raise a descriptive error."""
    return {name: pd.read_csv(path / f"{name}.csv", encoding="utf-8-sig") for name in KEYS}


def profile(tables: dict[str, pd.DataFrame], path: Path = DATA) -> dict:
    """Return reproducible descriptive statistics and integrity checks."""
    result: dict = {"tables": {}, "checks": {}}
    for name, df in tables.items():
        numbers = df.select_dtypes(include="number")
        outliers = {}
        for col in numbers:
            outliers[col] = iqr_outlier_count(numbers[col])
        dates = pd.to_datetime(df["fecha"], errors="coerce") if "fecha" in df else None
        result["tables"][name] = {
            "rows": len(df), "columns": len(df.columns), "fields": list(df.columns),
            "types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "nulls": {col: int(n) for col, n in df.isna().sum().items()},
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_keys": int(df.duplicated(KEYS[name]).sum()),
            "primary_key": KEYS[name],
            "negative_values": {col: int((numbers[col] < 0).sum()) for col in numbers},
            "outliers_iqr": outliers,
            "date_min": str(dates.min().date()) if dates is not None and dates.notna().any() else None,
            "date_max": str(dates.max().date()) if dates is not None and dates.notna().any() else None,
            "invalid_dates": int(dates.isna().sum()) if dates is not None else 0,
            "sha256": hashlib.sha256((path / f"{name}.csv").read_bytes()).hexdigest(),
        }
    c = result["checks"]
    v, i, b, p, t = (tables[x] for x in ("ventas", "inventarios", "presupuestos", "productos", "tiendas"))
    for name, df in (("ventas", v), ("inventarios", i), ("presupuestos", b)):
        c[f"{name}_unknown_store"] = int((~df.tienda_id.isin(t.tienda_id)).sum())
        if "producto_id" in df:
            c[f"{name}_unknown_product"] = int((~df.producto_id.isin(p.producto_id)).sum())
        dates = pd.to_datetime(df.fecha, errors="coerce")
        c[f"{name}_outside_october"] = int((dates.isna() | ~dates.between("2026-10-01", "2026-10-31")).sum())
    c["inventory_balance_errors"] = int((i.inventario_inicial + i.entradas - i.unidades_vendidas != i.inventario_final).sum())
    ordered = i.sort_values(["tienda_id", "producto_id", "fecha"])
    previous = ordered.groupby(["tienda_id", "producto_id"])["inventario_final"].shift()
    c["inventory_continuity_errors"] = int((previous.notna() & (ordered.inventario_inicial != previous)).sum())
    grouped = v.groupby(["fecha", "tienda_id", "producto_id"], as_index=False).unidades.sum()
    reconciliation = i.merge(grouped, on=["fecha", "tienda_id", "producto_id"], how="outer", indicator=True)
    c["sales_inventory_mismatches"] = int(((reconciliation["_merge"] == "right_only") | (reconciliation.unidades_vendidas.fillna(0) != reconciliation.unidades.fillna(0))).sum())
    c["sales_value_errors"] = int(((v.unidades * v.precio_unitario_cop * (1 - v.descuento_pct / 100) - v.venta_neta_cop).abs() > 0.01).sum())
    vp = v.merge(p[["producto_id", "precio_lista_cop", "costo_unitario_cop"]], on="producto_id", how="left")
    c["sales_cost_errors"] = int(((vp.unidades * vp.costo_unitario_cop - vp.costo_venta_cop).abs() > 0.01).sum())
    c["sales_price_differs_from_list"] = int((vp.precio_unitario_cop != vp.precio_lista_cop).sum())
    ip = i.merge(p[["producto_id", "costo_unitario_cop"]], on="producto_id", how="left", suffixes=("_inventory", "_product"))
    c["inventory_cost_differs_from_catalog"] = int((ip.costo_unitario_cop_inventory != ip.costo_unitario_cop_product).sum())
    c["invalid_discounts"] = int((~v.descuento_pct.between(0, 100)).sum())
    expected_budget = pd.MultiIndex.from_product([pd.date_range("2026-10-01", "2026-10-31").strftime("%Y-%m-%d"), t.tienda_id], names=["fecha", "tienda_id"])
    actual_budget = pd.MultiIndex.from_frame(b[["fecha", "tienda_id"]])
    c["missing_store_day_budgets"] = len(expected_budget.difference(actual_budget))
    expected_inventory = pd.MultiIndex.from_product([pd.date_range("2026-10-01", "2026-10-31").strftime("%Y-%m-%d"), t.tienda_id, p.producto_id], names=["fecha", "tienda_id", "producto_id"])
    c["missing_inventory_combinations"] = len(expected_inventory.difference(pd.MultiIndex.from_frame(i[["fecha", "tienda_id", "producto_id"]])))
    c["sales_without_budget"] = int(v.merge(b[["fecha", "tienda_id"]].drop_duplicates(), on=["fecha", "tienda_id"], how="left", indicator=True)["_merge"].eq("left_only").sum())
    result["total_rows"] = sum(len(df) for df in tables.values())
    return result


def main() -> None:
    """Write JSON and Markdown reports from the local input files."""
    result = profile(load_data())
    output = ROOT / "reports"
    output.mkdir(exist_ok=True)
    (output / "01_data_quality.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Calidad de datos — octubre de 2026", "", "Perfil generado a partir de los cinco CSV originales. IQR señala candidatos, no errores; ceros de ventas, entradas o inventario pueden ser válidos comercialmente.", "", "| Tabla | Filas | Columnas | Duplicados de llave | Nulos |", "|---|---:|---:|---:|---:|"]
    for name, info in result["tables"].items():
        lines.append(f"| {name} | {info['rows']} | {info['columns']} | {info['duplicate_keys']} | {sum(info['nulls'].values())} |")
    lines += [f"\nTotal: {result['total_rows']} registros.", "", "## Comprobaciones", "", "Los recuentos son incidencias observadas; diferencias de precio frente a lista pueden reflejar políticas comerciales y requieren interpretación.", ""]
    lines += [f"- `{name}`: {value}" for name, value in result["checks"].items()]
    lines += ["", "El JSON complementario contiene columnas, tipos, nulos, negativos, duplicados, fechas, huellas SHA-256 y candidatos IQR por campo. IQR con rango intercuartílico cero puede señalar numerosos valores válidos."]
    (output / "01_data_quality.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
