"""Command-line entry point for local and safely disabled generative analysis."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ai_analysis.engine import DEFAULT_CONFIG, OpenAIAdapter, analyze


def main() -> int:
    """Run one local or fallback analysis without transmitting data."""
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports" / "ai_analysis")
    parser.add_argument("--mode", choices=("local", "generative"), default="local")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        model = os.getenv("AUTOREPORT_AI_MODEL")
        provider = OpenAIAdapter(model, float(os.getenv("AUTOREPORT_AI_TIMEOUT_SECONDS", "10")), int(os.getenv("AUTOREPORT_AI_MAX_RETRIES", "1"))) if args.mode == "generative" else None
        result = analyze(args.source, args.output_dir, args.mode, args.config, provider=provider, model=model)
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}), file=sys.stderr); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
