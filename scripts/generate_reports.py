"""CLI for producing local commercial Excel and PDF reports."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.reporting.generator import generate


def main() -> int:
    """Generate reports or report a local failure without partial publication."""
    parser = argparse.ArgumentParser(description="Generar reportes comerciales locales")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports" / "generated")
    parser.add_argument("--format", choices=("excel", "pdf", "both"), default="both")
    args = parser.parse_args()
    try:
        result = generate(args.source, args.output_dir, args.format)
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "errors": [f"{type(exc).__name__}: {exc}"]}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
