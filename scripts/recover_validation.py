"""Recover interrupted runs protected by the current validation lock protocol."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.validation.engine import now, state_lock


def recover(state_dir: Path) -> dict:
    """Mark interrupted protocol-aware runs failed, never touching legacy runs."""
    recovered, legacy = [], []
    with state_lock(state_dir):
        db = sqlite3.connect(state_dir / "runs.sqlite3", timeout=0)
        try:
            db.execute("BEGIN IMMEDIATE")
            for run_id, evidence in db.execute("SELECT id, evidence FROM runs WHERE status IN ('RECEIVED','VALIDATING')").fetchall():
                item = json.loads(evidence)
                if item.get("recovery_protocol") != 1:
                    legacy.append(run_id); continue
                item["status"] = "FAILED"; item["finished_at"] = now()
                item.setdefault("history", []).append("FAILED")
                item.setdefault("errors", []).append("Interrupted execution recovered; retry the batch")
                db.execute("UPDATE runs SET status='FAILED', evidence=? WHERE id=?", (json.dumps(item), run_id))
                recovered.append(run_id)
            db.commit()
        except Exception:
            db.rollback(); raise
        finally:
            db.close()
    return {"recovered": recovered, "legacy_unmodified": legacy}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("state_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(recover(args.state_dir), indent=2))
