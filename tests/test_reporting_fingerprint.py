"""Regression coverage for report generator identity and safe retries."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from test_reporting import source
from test_validation_engine import batch
from src.reporting import generator


@pytest.fixture
def components(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Use temporary copies to simulate generator edits safely."""
    copy = tmp_path / "reporting"
    shutil.copytree(generator.REPORTING_COMPONENTS_DIR, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    monkeypatch.setattr(generator, "REPORTING_COMPONENTS_DIR", copy)
    return copy


def sha(path: Path) -> str:
    """Return the file content hash."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_initial_repeated_version_and_previous_preserved(source: Path, tmp_path: Path, components: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "out"
    first = generator.generate(source, out, "excel")
    previous = Path(first["output_dir"]) / first["files"][0]["name"]
    original_hash = sha(previous)
    assert first["generator_version"] == "4.0.5"
    assert len(first["generator_fingerprint"]) == 64
    assert generator.generate(source, out, "excel")["status"] == "SKIPPED"
    monkeypatch.setattr(generator, "GENERATOR_VERSION", "4.0.6")
    second = generator.generate(source, out, "excel")
    assert second["status"] == "SUCCESS" and second["request_key"] != first["request_key"]
    assert sha(previous) == original_hash and previous.exists()


@pytest.mark.parametrize("filename", ["excel.py", "pdf.py", "theme.py", "source.py", "generator.py"])
def test_component_change_invalidates(source: Path, tmp_path: Path, components: Path, filename: str) -> None:
    out = tmp_path / "out"
    first = generator.generate(source, out, "excel")
    file = components / filename
    file.write_bytes(file.read_bytes() + b"\n# fingerprint test\n")
    second = generator.generate(source, out, "excel")
    assert second["status"] == "SUCCESS"
    assert first["generator_fingerprint"] != second["generator_fingerprint"]
    assert first["request_key"] != second["request_key"]


def test_resources_paths_and_mtime_are_deterministic(tmp_path: Path, components: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    initial = generator.generator_fingerprint()
    os.utime(components / "theme.py", (1000000000, 1000000000))
    assert generator.generator_fingerprint() == initial
    other = tmp_path / "other-path"
    shutil.copytree(components, other)
    monkeypatch.setattr(generator, "REPORTING_COMPONENTS_DIR", other)
    assert generator.generator_fingerprint() == initial
    (other / "templates").mkdir()
    (other / "templates" / "report.txt").write_text("resource", encoding="utf-8")
    assert generator.generator_fingerprint() != initial


def test_source_change_invalidates(source: Path, tmp_path: Path, components: Path) -> None:
    out = tmp_path / "out"
    first = generator.generate(source, out, "excel")
    with (source / "stores.csv").open("ab") as stream:
        stream.write(b"\n")
    second = generator.generate(source, out, "excel")
    assert second["status"] == "SUCCESS" and second["request_key"] != first["request_key"]
    assert first["generator_fingerprint"] == second["generator_fingerprint"]


@pytest.mark.parametrize("damage", ["missing", "corrupt"])
def test_missing_or_corrupt_never_skipped(source: Path, tmp_path: Path, components: Path, damage: str) -> None:
    out = tmp_path / "out"
    result = generator.generate(source, out, "excel")
    output = Path(result["output_dir"]) / result["files"][0]["name"]
    if damage == "missing": output.unlink()
    else: output.write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="alterada"):
        generator.generate(source, out, "excel")


def test_failure_then_retry(source: Path, tmp_path: Path, components: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "out"; original = generator.build_excel
    def fail(*args: object) -> None:
        raise OSError("simulated write failure")
    monkeypatch.setattr(generator, "build_excel", fail)
    with pytest.raises(OSError): generator.generate(source, out, "excel")
    assert not list(out.glob("*/manifest.json"))
    monkeypatch.setattr(generator, "build_excel", original)
    assert generator.generate(source, out, "excel")["status"] == "SUCCESS"
    assert generator.generate(source, out, "excel")["status"] == "SKIPPED"
