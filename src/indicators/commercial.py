"""Compute reusable indicators from reconciled, separate data grains."""
from __future__ import annotations

import pandas as pd


def ratio(numerator: float, denominator: float, scale: float = 1) -> float | None:
    """Return an undefined ratio as None, never infinity."""
    return float(numerator / denominator * scale) if denominator else None


def summary(sales: pd.DataFrame, budget: int | None = None) -> dict:
    """Calculate totals using additive numerators and denominators."""
    revenue = int(sales.venta_neta_cop.sum()); cost = int(sales.costo_venta_cop.sum())
    valid_tickets = "transaccion_id" in sales and sales.transaccion_id.notna().all() and sales.transaccion_id.astype(str).str.strip().ne("").all() and sales.transaccion_id.is_unique
    tickets = int(sales.transaccion_id.nunique()) if valid_tickets else None
    return {"ventas_cop": revenue, "unidades": int(sales.unidades.sum()), "costo_cop": cost, "margen_cop": revenue - cost,
            "margen_pct": ratio(revenue - cost, revenue, 100), "presupuesto_cop": int(budget) if budget is not None else None,
            "cumplimiento_pct": ratio(revenue, budget, 100) if budget is not None else None,
            "transacciones": tickets, "ticket_promedio_cop": ratio(revenue, tickets) if tickets else None}


def calculate(data: dict[str, pd.DataFrame]) -> dict:
    """Compute outputs at compatible grains and preserve missing history."""
    sales, inv, budgets = (data[k].copy() for k in ("sales", "inventory", "budgets"))
    start, end = str(inv.fecha.min()), str(inv.fecha.max())
    totals = summary(sales, int(budgets.meta_ventas_cop.sum()))
    daily = []
    for day, group in budgets.groupby("fecha", sort=True):
        row = {"fecha": day, **summary(sales[sales.fecha == day], int(group.meta_ventas_cop.sum()))}
        daily.append(row)
    by_date = {r["fecha"]: r for r in daily}
    for row in daily:
        day = pd.Timestamp(row["fecha"])
        previous = by_date.get((day - pd.Timedelta(days=1)).strftime("%Y-%m-%d"))
        row["crecimiento_diario_pct"] = ratio(row["ventas_cop"] - previous["ventas_cop"], previous["ventas_cop"], 100) if previous else None
        current_days = [(day - pd.Timedelta(days=n)).strftime("%Y-%m-%d") for n in range(7)]
        prior_days = [(day - pd.Timedelta(days=n)).strftime("%Y-%m-%d") for n in range(7, 14)]
        if all(d in by_date for d in current_days + prior_days):
            current = sum(by_date[d]["ventas_cop"] for d in current_days); prior = sum(by_date[d]["ventas_cop"] for d in prior_days)
            row["crecimiento_semanal_pct"] = ratio(current - prior, prior, 100)
        else:
            row["crecimiento_semanal_pct"] = None
    stores = [{"tienda_id": key, **summary(sales[sales.tienda_id == key], int(group.meta_ventas_cop.sum()))} for key, group in budgets.groupby("tienda_id", sort=True)]
    cities = [{"ciudad": key, **summary(sales[sales.ciudad == key], int(group.meta_ventas_cop.sum()))} for key, group in budgets.groupby("ciudad", sort=True)]
    categories = [{"categoria": key, **summary(group)} for key, group in sales.groupby("categoria", sort=True)]
    ranking = sales.groupby(["producto_id", "categoria"], as_index=False).agg(ventas_cop=("venta_neta_cop", "sum"), unidades=("unidades", "sum"))
    by_sales = ranking.sort_values(["ventas_cop", "producto_id"], ascending=[False, True]).reset_index(drop=True)
    by_units = ranking.sort_values(["unidades", "producto_id"], ascending=[False, True]).reset_index(drop=True)
    by_sales["puesto_ventas"] = range(1, len(by_sales) + 1); by_units["puesto_unidades"] = range(1, len(by_units) + 1)
    ranking = by_sales.merge(by_units[["producto_id", "puesto_unidades"]], on="producto_id", validate="one_to_one")
    inv = inv.sort_values(["tienda_id", "producto_id", "fecha"])
    first = inv.groupby(["tienda_id", "producto_id"], as_index=False).first()
    last = inv[inv.fecha == end].copy()
    endpoints = first[["tienda_id", "producto_id", "inventario_inicial"]].merge(last, on=["tienda_id", "producto_id"], validate="one_to_one", suffixes=("_inicio", ""))
    avg = (endpoints.inventario_inicial_inicio.sum() + endpoints.inventario_final.sum()) / 2
    expected_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    coverage = inv.groupby(["tienda_id", "producto_id"]).fecha.nunique()
    complete_period = bool(coverage.eq(expected_days).all() and len(last) == len(coverage) and len(first) == len(last))
    totals["inventario_promedio_unidades"] = float(avg) if complete_period else None
    totals["rotacion_unidades"] = ratio(totals["unidades"], avg) if complete_period else None
    cutoff = pd.Timestamp(end); from_day = (cutoff - pd.Timedelta(days=14)).strftime("%Y-%m-%d")
    recent = inv[(inv.fecha >= from_day) & (inv.fecha <= end)]
    complete = recent.groupby(["tienda_id", "producto_id"]).fecha.nunique().eq(15)
    recent_sales = recent.groupby(["tienda_id", "producto_id"]).unidades_vendidas.sum()
    last = last.merge(complete.rename("historial_completo"), on=["tienda_id", "producto_id"], how="left", validate="one_to_one")
    last = last.merge(recent_sales.rename("unidades_15_dias"), on=["tienda_id", "producto_id"], how="left", validate="one_to_one")
    last["agotado"] = last.inventario_final.eq(0)
    last["baja_rotacion"] = pd.Series(pd.NA, index=last.index, dtype="boolean")
    available = last.historial_completo.fillna(False)
    last.loc[available, "baja_rotacion"] = (last.loc[available, "inventario_final"] > 0) & (last.loc[available, "unidades_15_dias"] == 0)
    return {"period": {"start": start, "end": end}, "summary": totals, "daily": daily, "stores": stores, "cities": cities, "categories": categories, "ranking": ranking.to_dict("records"), "inventory": last.to_dict("records"), "low_rotation": last[last.baja_rotacion.fillna(False)].to_dict("records")}
