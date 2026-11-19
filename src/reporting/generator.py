"""Generate reports atomically and make identical requests idempotent."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import shutil
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook
from pypdf import PdfReader

from src.reporting.excel import build_excel
from src.reporting.pdf import build_pdf
from src.reporting.source import load_source

GENERATOR_VERSION = "4.0.5"
REPORTING_COMPONENTS_DIR = Path(__file__).resolve().parent
RESOURCE_DIRS = ("assets", "resources", "templates")
RELEVANT_PACKAGES = ("openpyxl", "pandas", "pypdf", "reportlab")


def generator_fingerprint() -> str:
    """Hash report modules, declared resource trees and relevant package versions."""
    root = REPORTING_COMPONENTS_DIR
    files = list(root.glob("*.py"))
    for resource in RESOURCE_DIRS:
        folder = root / resource
        if folder.is_dir():
            files.extend(path for path in folder.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"} and not any(part.startswith(".") for part in path.relative_to(root).parts))
    components = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files, key=lambda item: item.relative_to(root).as_posix())}
    dependencies = {name: importlib.metadata.version(name) for name in RELEVANT_PACKAGES}
    payload = {"components": components, "dependencies": dependencies}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def generate(source_dir: Path, output_dir: Path, output_format: str = "both", analysis_path: Path | None = None) -> dict:
    """Record failures separately without exposing an incomplete final report."""
    started = time.perf_counter(); generation_id = str(uuid.uuid4())
    try:
        return _generate(source_dir, output_dir, output_format, analysis_path)
    except Exception as exc:
        failures = output_dir / ".failures"
        failures.mkdir(parents=True, exist_ok=True)
        record = {"generation_id": generation_id, "generated_at": datetime.now(timezone.utc).isoformat(), "status": "FAILED", "format": output_format, "duration_total_seconds": round(time.perf_counter() - started, 6), "files": [], "errors": [f"{type(exc).__name__}: {exc}"], "warnings": []}
        (failures / f"{generation_id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        raise


def _generate(source_dir: Path, output_dir: Path, output_format: str = "both", analysis_path: Path | None = None) -> dict:
    """Create verified reports as an atomic, content-addressed output directory."""
    if output_format not in {"excel", "pdf", "both"}:
        raise ValueError("Formato no admitido")
    start = time.perf_counter(); source = load_source(source_dir)
    fingerprint = generator_fingerprint()
    identity = {"hashes": source["hashes"], "format": output_format, "generator_version": GENERATOR_VERSION, "generator_fingerprint": fingerprint}
    if analysis_path is not None:
        from src.ai_analysis.engine import validate_for_reporting
        raw_analysis = analysis_path.read_bytes()
        analysis = json.loads(raw_analysis)
        validate_for_reporting(analysis, source)
        source["analysis"] = analysis
        identity["analysis_sha256"] = hashlib.sha256(raw_analysis).hexdigest()
    request_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / request_key
    lock = output_dir / (".lock-" + request_key)
    lock.mkdir()
    temporary = None
    try:
        if target.exists():
            manifest_path = target / "manifest.json"
            if not manifest_path.is_file(): raise ValueError("Destino existente incompleto")
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            if existing.get("request_key") != request_key or existing.get("status") != "SUCCESS" or existing.get("generator_version") != GENERATOR_VERSION or existing.get("generator_fingerprint") != fingerprint: raise ValueError("Manifiesto de destino incompatible")
            expected_formats = {"excel", "pdf"} if output_format == "both" else {output_format}
            expected_names = {f"AutoReport360_Reporte_Comercial_{source['manifest']['cutoff'][:7]}.xlsx" if fmt == "excel" else f"AutoReport360_Informe_Ejecutivo_{source['manifest']['cutoff'][:7]}.pdf" for fmt in expected_formats}
            if {item.get("name") for item in existing.get("files", [])} != expected_names or len(existing["files"]) != len(expected_names):
                raise ValueError("Manifiesto de destino incompleto")
            for item in existing["files"]:
                path = target / item["name"]
                if not path.is_file() or path.stat().st_size != item["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]: raise ValueError("Salida existente alterada")
            return {**existing, "status": "SKIPPED", "output_dir": str(target)}
        temporary = Path(tempfile.mkdtemp(prefix=".staging-", dir=output_dir))
        generation_id = str(uuid.uuid4()); generated = datetime.now(timezone.utc).isoformat()
        period = source["manifest"]["cutoff"][:7]; timings = {}; names = []
        for fmt in (["excel", "pdf"] if output_format == "both" else [output_format]):
            tick = time.perf_counter()
            name = f"AutoReport360_Reporte_Comercial_{period}.xlsx" if fmt == "excel" else f"AutoReport360_Informe_Ejecutivo_{period}.pdf"
            path = temporary / name
            if fmt == "excel":
                build_excel(source, path, generated); workbook = load_workbook(path, read_only=False); workbook.close()
            else:
                build_pdf(source, path, generated)
                if not PdfReader(str(path)).pages: raise ValueError("PDF vacío")
            if path.stat().st_size == 0: raise ValueError("Archivo generado vacío")
            names.append(name); timings[fmt] = round(time.perf_counter() - tick, 6)
        files = [{"name": n, "bytes": (temporary / n).stat().st_size, "sha256": hashlib.sha256((temporary / n).read_bytes()).hexdigest()} for n in names]
        manifest = {"generation_id": generation_id, "pipeline_run_id": source["manifest"]["pipeline_run_id"], "generated_at": generated, "status": "SUCCESS", "request_key": request_key, "generator_version": GENERATOR_VERSION, "generator_fingerprint": fingerprint, "analysis_sha256": identity.get("analysis_sha256"), "source_hashes": source["hashes"], "format": output_format, "files": files, "durations_seconds": timings, "duration_total_seconds": round(time.perf_counter() - start, 6), "errors": [], "warnings": ["La calidad histórica acumulada no está disponible en el contrato de origen."]}
        (temporary / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        os.rename(temporary, target); temporary = None
        return {**manifest, "output_dir": str(target)}
    finally:
        if temporary is not None and temporary.parent.resolve() == output_dir.resolve(): shutil.rmtree(temporary)
        lock.rmdir()
