"""Command-line interface for the local batch validator."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.validation.engine import run_batch


def main() -> int:
    """Run one batch and return a process-friendly exit code."""
    parser = argparse.ArgumentParser(description="Validate an AutoReport360 batch")
    parser.add_argument("input", type=Path, help="Batch directory")
    parser.add_argument("--state-dir", type=Path, default=ROOT / "logs" / "validation")
    parser.add_argument("--master-dir", type=Path, help="Directory containing master CSV files")
    args = parser.parse_args()
    args.state_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=args.state_dir / "validation.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
    result = run_batch(args.input, args.state_dir, args.master_dir)
    logging.info("run=%s status=%s duration=%s", result["run_id"], result["status"], result["duration_seconds"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"APPROVED", "SKIPPED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
