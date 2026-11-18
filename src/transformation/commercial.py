"""Prepare separate commercial grains and reconcile their totals."""
from __future__ import annotations
import pandas as pd


def prepare(tables: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict]:
    """Enrich transactions without joining budgets or inventory to sales."""
    sales = tables["ventas"].merge(tables["tiendas"], on="tienda_id", validate="many_to_one", suffixes=("", "_tienda"))
    sales = sales.merge(tables["productos"][["producto_id", "nombre", "categoria"]], on="producto_id", validate="many_to_one", suffixes=("", "_producto"))
    inventory = tables["inventarios"].merge(tables["tiendas"], on="tienda_id", validate="many_to_one")
    inventory = inventory.merge(tables["productos"][["producto_id", "categoria"]], on="producto_id", validate="many_to_one")
    budgets = tables["presupuestos"].merge(tables["tiendas"], on="tienda_id", validate="many_to_one")
    reconciliation = {"sales_rows_source": len(tables["ventas"]), "sales_rows_output": len(sales), "sales_cop_source": int(tables["ventas"].venta_neta_cop.sum()), "sales_cop_output": int(sales.venta_neta_cop.sum()), "cost_cop_source": int(tables["ventas"].costo_venta_cop.sum()), "cost_cop_output": int(sales.costo_venta_cop.sum()), "budget_cop_source": int(tables["presupuestos"].meta_ventas_cop.sum()), "budget_cop_output": int(budgets.meta_ventas_cop.sum())}
    if any(reconciliation[f"{x}_source"] != reconciliation[f"{x}_output"] for x in ("sales_rows", "sales_cop", "cost_cop", "budget_cop")):
        raise ValueError("Commercial reconciliation failed")
    return {"sales": sales, "inventory": inventory, "budgets": budgets}, reconciliation
