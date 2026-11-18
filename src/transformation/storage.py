"""Atomic local persistence of validated commercial tables."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from src.extraction.loader import contracts


def connect(path: Path) -> sqlite3.Connection:
    """Open and initialize the commercial database with foreign keys enabled."""
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=60)
    db.execute("PRAGMA foreign_keys=ON")
    for name, spec in contracts().items():
        cols = [f'"{col}" {"INTEGER" if kind == "int" else "TEXT"} NOT NULL' for col, kind in spec["fields"].items()]
        pk = ", ".join(f'"{key}"' for key in spec["key"])
        foreign = []
        if name in {"ventas", "inventarios", "presupuestos"}:
            foreign.append('FOREIGN KEY (tienda_id) REFERENCES tiendas(tienda_id)')
        if name in {"ventas", "inventarios"}:
            foreign.append('FOREIGN KEY (producto_id) REFERENCES productos(producto_id)')
        db.execute(f'CREATE TABLE IF NOT EXISTS "{name}" ({", ".join(cols)}, PRIMARY KEY ({pk}){", " if foreign else ""}{", ".join(foreign)})')
    db.execute("CREATE TABLE IF NOT EXISTS persistence_runs (run_id TEXT PRIMARY KEY, validation_id TEXT NOT NULL, status TEXT NOT NULL, metadata TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS row_lineage (table_name TEXT NOT NULL, key_value TEXT NOT NULL, run_id TEXT NOT NULL REFERENCES persistence_runs(run_id), PRIMARY KEY(table_name, key_value))")
    db.commit()
    return db


def persist(db: sqlite3.Connection, tables: dict[str, pd.DataFrame], run_id: str, validation_id: str, metadata: dict) -> dict[str, int]:
    """Insert validated rows atomically, rejecting conflicting existing records."""
    counts = {}
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT INTO persistence_runs VALUES (?, ?, 'PERSISTED', ?)", (run_id, validation_id, json.dumps(metadata, ensure_ascii=False)))
        for name, spec in contracts().items():
            columns = list(spec["fields"])
            names = ",".join(f'"{col}"' for col in columns)
            where = " AND ".join(f'"{col}"=?' for col in spec["key"])
            sql = f'INSERT INTO "{name}" ({names}) VALUES ({",".join("?" for _ in columns)})'
            inserted = 0
            for raw in tables[name][columns].itertuples(index=False, name=None):
                values = tuple(int(v) if spec["fields"][col] == "int" else str(v) for col, v in zip(columns, raw))
                lookup = tuple(values[columns.index(col)] for col in spec["key"])
                existing = db.execute(f'SELECT {names} FROM "{name}" WHERE {where}', lookup).fetchone()
                if existing is not None:
                    if existing != values:
                        raise ValueError(f"Conflicting persisted {name} key: {lookup}")
                    continue
                db.execute(sql, values)
                key = json.dumps(lookup, ensure_ascii=False, separators=(",", ":"))
                db.execute("INSERT INTO row_lineage VALUES (?, ?, ?)", (name, key, run_id))
                inserted += 1
            counts[name] = inserted
        db.commit()
    except Exception:
        db.rollback()
        raise
    return counts


def read_tables(db: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Read a consistent snapshot for transformation."""
    db.execute("BEGIN")
    try:
        result = {name: pd.read_sql_query(f'SELECT * FROM "{name}"', db) for name in contracts()}
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
