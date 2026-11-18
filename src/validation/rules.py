"""Validate contracts and commercial consistency without changing source data."""
from __future__ import annotations

import pandas as pd

from src.extraction.loader import contracts
from src.validation.statistics import iqr_outlier_count


def validate(tables: dict, files: dict) -> tuple[list[str], list[str], dict]:
    """Return critical errors, IQR warnings and validated data frames."""
    errors: list[str] = []
    warnings: list[str] = []
    clean = {}
    for name, spec in contracts().items():
        if name not in tables:
            continue
        df = tables[name].copy()
        missing = set(spec["fields"]) - set(df.columns)
        if missing:
            errors.append(f"{name}: missing columns {sorted(missing)}")
            continue
        if df.empty:
            errors.append(f"{name}: empty table")
        for col, kind in spec["fields"].items():
            values = df[col].astype("string").str.strip()
            null = values.isna() | values.eq("")
            if null.any():
                errors.append(f"{name}.{col}: {int(null.sum())} required nulls")
            if kind == "int":
                parsed = pd.to_numeric(values, errors="coerce")
                invalid = ~null & (parsed.isna() | (parsed % 1 != 0))
                if invalid.any():
                    errors.append(f"{name}.{col}: {int(invalid.sum())} invalid integers")
                if (parsed < 0).any():
                    errors.append(f"{name}.{col}: negative values")
                df[col] = parsed
            elif kind == "date":
                dates = pd.to_datetime(values.where(values.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False)), format="%Y-%m-%d", errors="coerce")
                if (dates.isna() & ~null).any():
                    errors.append(f"{name}.{col}: invalid dates")
                if files[name]["date"] and (values != files[name]["date"]).any():
                    errors.append(f"{name}: dates differ from file date")
                df[col] = values
            else:
                df[col] = values
        if df.duplicated(spec["key"]).any():
            errors.append(f"{name}: duplicate primary keys")
        clean[name] = df
    if errors or len(clean) != len(contracts()):
        return errors, warnings, clean
    t, p, v, i, b = (clean[x] for x in ("tiendas", "productos", "ventas", "inventarios", "presupuestos"))
    for name in ("ventas", "inventarios", "presupuestos"):
        df = clean[name]
        if (~df.tienda_id.isin(t.tienda_id)).any():
            errors.append(f"{name}: unknown store")
        if "producto_id" in df and (~df.producto_id.isin(p.producto_id)).any():
            errors.append(f"{name}: unknown product")
    if not v.descuento_pct.between(0, 100).all():
        errors.append("ventas: invalid discount")
    if ((v.unidades * v.precio_unitario_cop * (100 - v.descuento_pct) / 100 - v.venta_neta_cop).abs() > .01).any():
        errors.append("ventas: inconsistent net amount")
    vp = v.merge(p[["producto_id", "costo_unitario_cop"]], on="producto_id", how="left")
    if ((vp.unidades * vp.costo_unitario_cop - vp.costo_venta_cop).abs() > .01).any():
        errors.append("ventas: inconsistent cost amount")
    ip = i.merge(p[["producto_id", "costo_unitario_cop"]], on="producto_id", how="left", suffixes=("_inventory", "_product"))
    if (ip.costo_unitario_cop_inventory != ip.costo_unitario_cop_product).any():
        errors.append("inventarios: cost differs from product master")
    if (i.inventario_inicial + i.entradas - i.unidades_vendidas != i.inventario_final).any():
        errors.append("inventarios: inconsistent balance")
    ordered = i.sort_values(["tienda_id", "producto_id", "fecha"])
    previous = ordered.groupby(["tienda_id", "producto_id"])["inventario_final"].shift()
    prior_date = pd.to_datetime(ordered.groupby(["tienda_id", "producto_id"])["fecha"].shift())
    consecutive = (pd.to_datetime(ordered.fecha) - prior_date).dt.days.eq(1)
    if (consecutive & previous.ne(ordered.inventario_inicial)).any():
        errors.append("inventarios: inconsistent consecutive balances")
    sales = v.groupby(["fecha", "tienda_id", "producto_id"], as_index=False).unidades.sum()
    joined = i.merge(sales, on=["fecha", "tienda_id", "producto_id"], how="outer", indicator=True)
    if ((joined["_merge"] == "right_only") | joined.unidades_vendidas.fillna(0).ne(joined.unidades.fillna(0))).any():
        errors.append("ventas/inventarios: units do not reconcile")
    budgets = v.merge(b[["fecha", "tienda_id"]], on=["fecha", "tienda_id"], how="left", indicator=True)
    if budgets["_merge"].eq("left_only").any():
        errors.append("ventas: missing store/day budget")
    dates = set(i.fecha) | set(v.fecha) | set(b.fecha)
    date_range = pd.date_range(min(dates), max(dates)).strftime("%Y-%m-%d")
    expected = pd.MultiIndex.from_product([date_range, t.tienda_id, p.producto_id])
    if len(expected.difference(pd.MultiIndex.from_frame(i[["fecha", "tienda_id", "producto_id"]]))):
        errors.append("inventarios: missing store/product/day coverage")
    expected_b = pd.MultiIndex.from_product([date_range, t.tienda_id])
    if len(expected_b.difference(pd.MultiIndex.from_frame(b[["fecha", "tienda_id"]]))):
        errors.append("presupuestos: missing store/day coverage")
    for name, df in clean.items():
        for col in df.select_dtypes(include="number"):
            count = iqr_outlier_count(df[col])
            if count:
                warnings.append(f"{name}.{col}: {count} IQR candidates")
    return errors, warnings, clean
