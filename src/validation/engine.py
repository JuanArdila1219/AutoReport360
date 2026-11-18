"""Run validation with persistent, transactional deduplication and evidence."""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
import uuid
import contextlib
import msvcrt
from datetime import datetime, timezone
from pathlib import Path

from src.extraction.loader import contracts, discover, read_files
from src.validation.rules import validate

LOGGER = logging.getLogger(__name__)


def now() -> str:
    """Return an unambiguous timestamp."""
    return datetime.now(timezone.utc).isoformat()


@contextlib.contextmanager
def state_lock(state_dir: Path):
    """Hold an OS-level lock for the entire validation or recovery operation."""
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / "validation.lock").open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0"); handle.flush()
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        try:
            yield
        finally:
            handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def run_batch(input_dir: Path, state_dir: Path, master_dir: Path | None = None) -> dict:
    """Serialize validation and safe recovery using a process-held lock."""
    with state_lock(state_dir):
        return _run_batch(input_dir, state_dir, master_dir)


def _run_batch(input_dir: Path, state_dir: Path, master_dir: Path | None = None) -> dict:
    """Validate and atomically reserve approved transaction keys in SQLite."""
    state_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(uuid.uuid4())
    started, timer = now(), time.perf_counter()
    result = {"run_id": run_id, "started_at": started, "finished_at": None, "status": "RECEIVED", "history": ["RECEIVED"], "files": {}, "errors": [], "warnings": [], "period": None, "recovery_protocol": 1}
    db = sqlite3.connect(state_dir / "runs.sqlite3", timeout=60)
    try:
        db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, status TEXT NOT NULL, evidence TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS approved_keys (table_name TEXT NOT NULL, key_value TEXT NOT NULL, run_id TEXT NOT NULL, row_hash TEXT NOT NULL, PRIMARY KEY(table_name, key_value))")
        db.execute("INSERT INTO runs VALUES (?, ?, ?)", (run_id, result["status"], json.dumps(result)))
        db.commit()
        result["status"] = "VALIDATING"; result["history"].append("VALIDATING")
        db.execute("UPDATE runs SET status=?, evidence=? WHERE id=?", (result["status"], json.dumps(result), run_id))
        db.commit()
        # A write lock serializes the check-and-reserve operation across concurrent runs.
        db.execute("BEGIN IMMEDIATE")
        files, errors = discover(input_dir, master_dir) if master_dir else discover(input_dir)
        result["errors"].extend(errors)
        tables, metadata = read_files(files)
        result["files"] = metadata
        if not errors:
            errors, warnings, clean = validate(tables, files)
            result["errors"].extend(errors); result["warnings"].extend(warnings)
            if not errors:
                dates = sorted(set().union(*(set(clean[n].fecha) for n in ("ventas", "inventarios", "presupuestos"))))
                result["period"] = {"start": dates[0], "end": dates[-1]}
                keys = []
                for name, spec in contracts().items():
                    if spec["kind"] != "transaction":
                        continue
                    frame = clean[name][list(spec["fields"])].astype(str)
                    for row in frame.to_dict("records"):
                        key = json.dumps([row[col] for col in spec["key"]], ensure_ascii=False, separators=(",", ":"))
                        digest = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
                        keys.append((name, key, digest))
                overlaps = [db.execute("SELECT row_hash FROM approved_keys WHERE table_name=? AND key_value=?", (name, key)).fetchone() for name, key, _ in keys]
                existing = sum(item is not None for item in overlaps)
                conflicts = sum(item is not None and item[0] != key[2] for item, key in zip(overlaps, keys))
                result["overlapping_keys"] = existing
                result["conflicting_keys"] = conflicts
                if conflicts:
                    result["errors"].append(f"Approved keys have different contents: {conflicts}")
                elif existing == len(keys) and existing:
                    result["status"] = "SKIPPED"
                elif existing:
                    result["errors"].append(f"Partial overlap with approved data: {existing} keys")
                else:
                    db.executemany("INSERT INTO approved_keys VALUES (?, ?, ?, ?)", ((name, key, run_id, digest) for name, key, digest in keys))
                    result["status"] = "APPROVED"
        if result["errors"]:
            result["status"] = "REJECTED"
    except Exception as exc:
        db.rollback()
        LOGGER.exception("Validation run failed: %s", run_id)
        result["status"] = "FAILED"
        result["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        result["finished_at"] = now()
        result["duration_seconds"] = round(time.perf_counter() - timer, 6)
        result["history"].append(result["status"])
        evidence = json.dumps(result, ensure_ascii=False, indent=2)
        db.execute("UPDATE runs SET status=?, evidence=? WHERE id=?", (result["status"], evidence, run_id))
        db.commit()
        db.close()
        (state_dir / f"{run_id}.json").write_text(evidence + "\n", encoding="utf-8")
    return result
