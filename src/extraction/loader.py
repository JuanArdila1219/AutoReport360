"""Discover, fingerprint and read a validation batch."""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "config" / "data_contracts.json"
MASTERS = ROOT / "data" / "simulated"
PATTERN = re.compile(r"^(tiendas|productos|ventas|inventarios|presupuestos)(?:_(\d{4}-\d{2}-\d{2}))?\.(csv|xlsx)$", re.IGNORECASE)


def contracts() -> dict:
    """Load the editable input contracts."""
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def discover(directory: Path, master_dir: Path = MASTERS) -> tuple[dict, list[str]]:
    """Resolve a complete historical batch or a dated daily batch and masters."""
    if not directory.is_dir():
        raise ValueError(f"Input directory does not exist: {directory}")
    found: dict = {}
    errors: list[str] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.name.startswith("~$"):
            continue
        match = PATTERN.fullmatch(path.name)
        if not match:
            if path.suffix.lower() in {".csv", ".xlsx", ".xls"}:
                errors.append(f"Invalid file name or format: {path.name}")
            continue
        name, date, _ = match.groups()
        name = name.lower()
        if name in found:
            errors.append(f"Multiple files for {name}")
        else:
            found[name] = {"path": path, "date": date, "source": "input"}
    transaction_dates = {entry["date"] for name, entry in found.items() if contracts()[name]["kind"] == "transaction"}
    if len(transaction_dates) > 1:
        errors.append("Mixed transaction file dates or historical/daily naming")
    daily = len(transaction_dates) == 1 and None not in transaction_dates
    for name, spec in contracts().items():
        if name not in found and daily and spec["kind"] == "master":
            path = master_dir / f"{name}.csv"
            if path.is_file():
                found[name] = {"path": path, "date": None, "source": "master"}
        if name not in found:
            errors.append(f"Missing required file: {name}")
    if any(entry["date"] for name, entry in found.items() if contracts()[name]["kind"] == "master"):
        errors.append("Master files must not include a date suffix")
    return found, errors


def read_files(files: dict) -> tuple[dict, dict]:
    """Read files as text to validate types without coercion or loss of identifiers."""
    tables, metadata = {}, {}
    for name, entry in files.items():
        path = entry["path"]
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        frame = (pd.read_csv(io.BytesIO(content), dtype=str, encoding="utf-8-sig", keep_default_na=False)
                 if path.suffix.lower() == ".csv" else pd.read_excel(io.BytesIO(content), dtype=str, keep_default_na=False))
        tables[name] = frame
        metadata[name] = {"path": str(path.resolve()), "sha256": digest, "rows": len(frame), "source": entry["source"], "file_date": entry["date"]}
    return tables, metadata
