"""Read and validate the structured output contract from phase 03."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date
from pathlib import Path

import pandas as pd

FILES = ("manifest.json", "summary.json", "daily.csv", "stores.csv", "cities.csv", "categories.csv", "ranking.csv", "inventory.csv", "low_rotation.csv", "quality.json")
KEYS = {"daily": ["fecha"], "stores": ["tienda_id"], "cities": ["ciudad"], "categories": ["categoria"], "ranking": ["producto_id"], "inventory": ["tienda_id", "producto_id"], "low_rotation": ["tienda_id", "producto_id"]}
REQUIRED = {"daily": {"fecha", "ventas_cop", "presupuesto_cop"}, "stores": {"tienda_id", "ventas_cop"}, "cities": {"ciudad", "ventas_cop"}, "categories": {"categoria", "ventas_cop"}, "ranking": {"producto_id", "ventas_cop", "unidades", "puesto_ventas"}, "inventory": {"fecha", "tienda_id", "producto_id", "agotado", "baja_rotacion"}, "low_rotation": {"fecha", "tienda_id", "producto_id", "agotado", "baja_rotacion"}}


def load_source(directory: Path) -> dict:
    """Validate metadata, granularities and consistency before producing reports."""
    if any(not (directory / name).is_file() for name in FILES):
        raise ValueError("Faltan archivos obligatorios de la ejecución de origen")
    raw = {name: (directory / name).read_bytes() for name in FILES}
    manifest, summary, quality = (json.loads(raw[name]) for name in ("manifest.json", "summary.json", "quality.json"))
    fields = ("pipeline_run_id", "validation_id", "period", "cutoff", "formula_version")
    if not all(key in manifest for key in fields) or manifest["formula_version"] != "3.0":
        raise ValueError("Manifiesto incompleto o versión no admitida")
    uuid.UUID(manifest["pipeline_run_id"]); uuid.UUID(manifest["validation_id"])
    start = date.fromisoformat(manifest["period"]["start"]); end = date.fromisoformat(manifest["period"]["end"])
    if start > end or manifest["cutoff"] != end.isoformat():
        raise ValueError("Periodo o fecha de corte inválidos")
    for item in (summary, quality):
        if any(item.get(key) != manifest[key] for key in fields):
            raise ValueError("Identificadores o metadatos de origen inconsistentes")
    if quality.get("validation_status") not in {"APPROVED", "SKIPPED"} or quality.get("errors"):
        raise ValueError("Estado de validación de origen no admisible")
    import io
    frames = {name: pd.read_csv(io.BytesIO(raw[name + ".csv"]), encoding="utf-8-sig") for name in KEYS}
    for name, df in frames.items():
        if not REQUIRED[name].issubset(df.columns) or df.duplicated(KEYS[name]).any() or df[KEYS[name]].isna().any().any():
            raise ValueError(f"Estructura o granularidad inválida: {name}")
    days = pd.to_datetime(frames["daily"].fecha, format="%Y-%m-%d", errors="coerce")
    expected_days = set(pd.date_range(start, end).strftime("%Y-%m-%d"))
    if days.isna().any() or days.empty or set(frames["daily"].fecha) != expected_days:
        raise ValueError("Fechas diarias fuera del periodo")
    if any(frames[name].empty for name in ("stores", "cities", "categories", "ranking", "inventory")):
        raise ValueError("Una tabla obligatoria no contiene datos")
    for name in ("inventory", "low_rotation"):
        if not frames[name].empty and not frames[name].fecha.eq(manifest["cutoff"]).all():
            raise ValueError(f"Fecha de corte inconsistente: {name}")
    inv = frames["inventory"]
    for col in ("agotado", "baja_rotacion"):
        values = set(inv[col].dropna().astype(str).str.lower())
        if not values.issubset({"true", "false"}):
            raise ValueError(f"Indicador booleano inválido: {col}")
    flagged = set(map(tuple, inv.loc[inv.baja_rotacion.astype(str).str.lower().eq("true"), KEYS["inventory"]].to_numpy()))
    low = set(map(tuple, frames["low_rotation"][KEYS["low_rotation"]].to_numpy()))
    if flagged != low:
        raise ValueError("Baja rotación no coincide con inventario")
    amounts = summary.get("summary", {})
    required_summary = {"ventas_cop", "unidades", "presupuesto_cop", "ticket_promedio_cop", "margen_cop", "margen_pct", "rotacion_unidades", "cumplimiento_pct", "costo_cop"}
    if not required_summary.issubset(amounts):
        raise ValueError("Resumen incompleto")
    for name in ("daily", "stores", "cities", "categories", "ranking"):
        if pd.to_numeric(frames[name].ventas_cop, errors="coerce").isna().any() or int(frames[name].ventas_cop.sum()) != amounts["ventas_cop"]:
            raise ValueError(f"Ventas inconsistentes en {name}")
    if int(frames["daily"].presupuesto_cop.sum()) != amounts["presupuesto_cop"]:
        raise ValueError("Presupuesto diario inconsistente")
    return {"manifest": manifest, "summary": amounts, "quality": quality, "frames": frames, "hashes": {n: hashlib.sha256(v).hexdigest() for n, v in raw.items()}}
