"""Exercise the inline PAD PowerShell block with a fake local Python process."""
from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'automation' / 'pad_action_template.ps1').read_text(encoding='utf-8')
POWERSHELL = shutil.which('powershell.exe')


@pytest.fixture
def fake_project(tmp_path: Path) -> Path:
    """Create a standalone temporary Python launcher and a deterministic stub."""
    project = tmp_path / 'project with spaces'
    scripts = project / '.venv' / 'Scripts'
    scripts.mkdir(parents=True)
    shutil.copy2(sys.executable, scripts / 'python.exe')
    shutil.copy2(ROOT / '.venv' / 'pyvenv.cfg', project / '.venv' / 'pyvenv.cfg')
    entry = project / 'scripts' / 'run_automation.py'
    entry.parent.mkdir()
    entry.write_text('''import json,sys\ncase=sys.argv[1]\nif case == "empty": sys.exit(7)\nif case == "invalid": print("not-json"); sys.exit(1)\nif case == "bad-contract": print("{}"); sys.exit(0)\nif case == "stderr": print("native error",file=sys.stderr); sys.exit(9)\nstatus={"ok":"SUCCESS","skipped":"SKIPPED","reject":"REJECTED","failure":"FAILED","mismatch":"REJECTED"}[case]\ncode={"SUCCESS":0,"SKIPPED":0,"REJECTED":2,"FAILED":1}[status]\nprint(json.dumps({"status":status,"distribution_status":"NOT_PREPARED","errors":[],"reason":"INVALID_BATCH" if status=="REJECTED" else None,"message":"revisión ágil"},ensure_ascii=False))\nsys.exit(0 if case=="mismatch" else code)\n''', encoding='utf-8')
    return project


def invoke(project: Path, batch: str, inject_exception: bool = False) -> tuple[dict, subprocess.CompletedProcess]:
    """Run the exact inline action after substituting PAD variables."""
    if not POWERSHELL: pytest.skip('Windows PowerShell is unavailable')
    script = TEMPLATE.replace('%ProyectoRuta%', str(project)).replace('%Workspace%', str(project / 'workspace with spaces')).replace('%Batch%', batch)
    if inject_exception:
        script = script.replace("    $python = Join-Path $projectRoot", "    throw 'PRUEBA_CONTROLADA_AUTOREPORT360'\n    $python = Join-Path $projectRoot", 1)
    script = "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n" + script
    encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
    completed = subprocess.run([POWERSHELL, '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], capture_output=True, encoding='utf-8', timeout=30)
    assert completed.returncode == 0, completed.stderr
    assert not completed.stderr, completed.stderr
    return json.loads(completed.stdout), completed


@pytest.mark.parametrize(('batch', 'status', 'code'), [('ok', 'SUCCESS', 0), ('skipped', 'SKIPPED', 0), ('reject', 'REJECTED', 2), ('failure', 'FAILED', 1)])
def test_business_status_is_preserved(fake_project: Path, batch: str, status: str, code: int) -> None:
    result, _ = invoke(fake_project, batch)
    assert result['exit_code'] == code and result['result']['status'] == status
    assert result['result']['message'] == 'revisión ágil'
    if status == 'REJECTED': assert result['result']['reason'] == 'INVALID_BATCH'


@pytest.mark.parametrize(('batch', 'reason', 'code'), [('empty', 'EMPTY_OUTPUT', 7), ('invalid', 'INVALID_JSON', 1), ('bad-contract', 'INVALID_CONTRACT', 0), ('stderr', 'EMPTY_OUTPUT', 9), ('mismatch', 'EXIT_STATUS_MISMATCH', 0)])
def test_invalid_native_output_is_technical_failure(fake_project: Path, batch: str, reason: str, code: int) -> None:
    result, _ = invoke(fake_project, batch)
    assert result['exit_code'] == 1 and result['python_exit_code'] == code
    assert result['result']['status'] == 'FAILED' and result['result']['reason'] == reason


def test_missing_python_is_caught(tmp_path: Path) -> None:
    result, _ = invoke(tmp_path / 'missing project', 'ok')
    assert result['result']['reason'] == 'PYTHON_NOT_FOUND' and result['python_exit_code'] is None


def test_controlled_powershell_exception_is_caught(fake_project: Path) -> None:
    result, _ = invoke(fake_project, 'ok', inject_exception=True)
    assert result['exit_code'] == 1 and result['result']['reason'] == 'POWERSHELL_EXCEPTION'
    assert result['result']['automation_id'] == 'NO_DISPONIBLE'


def test_missing_python_has_fallback_automation_id(tmp_path: Path) -> None:
    result, _ = invoke(tmp_path / 'missing project', 'ok')
    assert result['result']['automation_id'] == 'NO_DISPONIBLE'
