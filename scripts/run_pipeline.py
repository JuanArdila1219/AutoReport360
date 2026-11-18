"""Validate, persist and calculate commercial outputs locally."""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extraction.loader import discover, read_files
from src.validation.engine import run_batch
from src.validation.rules import validate
from src.transformation.storage import connect, persist, read_tables
from src.transformation.commercial import prepare
from src.indicators.commercial import calculate


def execute(input_dir: Path, state_dir: Path, output_dir: Path, master_dir: Path | None = None) -> dict:
    """Run a local pipeline, keeping validation and persistence outcomes separate."""
    started = time.perf_counter(); run_id = str(uuid.uuid4()); times = {}; result = {"run_id": run_id}
    try:
        tick = time.perf_counter()
        validation = run_batch(input_dir, state_dir, master_dir)
        times["validation"] = time.perf_counter() - tick
        result["validation_status"] = validation["status"]; result["validation_id"] = validation["run_id"]
        if validation["status"] not in {"APPROVED", "SKIPPED"}:
            result.update(status=validation["status"], errors=validation["errors"])
            return result
        tick = time.perf_counter()
        files, errors = discover(input_dir, master_dir) if master_dir else discover(input_dir)
        tables, metadata = read_files(files)
        if errors or any(metadata[k]["sha256"] != validation["files"][k]["sha256"] for k in metadata):
            raise ValueError("Input changed after validation or files are missing")
        errors, _, clean = validate(tables, files)
        if errors:
            raise ValueError(f"Input revalidation failed: {errors}")
        db = connect(state_dir / "commercial.sqlite3")
        try:
            result["persistence_status"] = "PENDING"
            counts = persist(db, clean, run_id, validation["run_id"], {"files": metadata, "period": validation["period"]})
            result["persistence_status"] = "PERSISTED" if any(counts.values()) else "ALREADY_PERSISTED"
            result["inserted"] = counts
            times["persistence"] = time.perf_counter() - tick
            tick = time.perf_counter(); snapshot = read_tables(db); prepared, reconciliation = prepare(snapshot)
            times["transformation"] = time.perf_counter() - tick
            tick = time.perf_counter(); indicators = calculate(prepared)
            times["indicators"] = time.perf_counter() - tick
        finally:
            db.close()
        tick = time.perf_counter()
        target = output_dir / run_id; target.mkdir(parents=True, exist_ok=False)
        context = {"pipeline_run_id": run_id, "validation_id": validation["run_id"], "period": indicators["period"], "cutoff": indicators["period"]["end"], "formula_version": "3.0"}
        (target / "summary.json").write_text(json.dumps({**context, "summary": indicators["summary"], "reconciliation": reconciliation}, ensure_ascii=False, indent=2), encoding="utf-8")
        for name in ("daily", "stores", "cities", "categories", "ranking", "inventory", "low_rotation"):
            frame = pd.DataFrame(indicators[name])
            if name == "low_rotation" and frame.empty:
                frame = pd.DataFrame(indicators["inventory"]).iloc[0:0]
            frame.to_csv(target / f"{name}.csv", index=False, encoding="utf-8-sig")
        (target / "quality.json").write_text(json.dumps({**context, "validation_status": validation["status"], "errors": validation["errors"], "warnings": validation["warnings"]}, ensure_ascii=False, indent=2), encoding="utf-8")
        (target / "manifest.json").write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
        result.update(status="SUCCESS", output=str(target), summary=indicators["summary"], reconciliation=reconciliation)
        times["outputs"] = time.perf_counter() - tick
    except Exception as exc:
        if result.get("persistence_status") == "PENDING":
            result["persistence_status"] = "FAILED"
        result.update(status="FAILED", error=f"{type(exc).__name__}: {exc}")
    finally:
        times["total"] = time.perf_counter() - started
        result["times_seconds"] = {k: round(v, 6) for k, v in times.items()}
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / f"pipeline_{run_id}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    """Parse arguments and return an automation-friendly status code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--state-dir", type=Path, default=ROOT / "logs" / "validation")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument("--master-dir", type=Path)
    args = parser.parse_args()
    result = execute(args.input, args.state_dir, args.output_dir, args.master_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "SUCCESS" else 2 if result["status"] == "REJECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
