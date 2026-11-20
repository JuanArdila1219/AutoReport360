"""Exercise the local orchestration in isolated temporary workspaces."""
from __future__ import annotations
import json
import shutil
import threading
from pathlib import Path
import pytest
from test_validation_engine import batch
from scripts import run_automation as automation


def deliver(source: Path, workspace: Path, name: str = 'batch') -> Path:
    """Copy a fixture into the inbox and commit its completion marker."""
    target = workspace / 'pending' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    files = {p.name: automation.digest(p) for p in target.iterdir() if p.is_file()}
    automation.write_json(target / 'READY.json', {'batch_id': name, 'received_at': '2026-10-01T00:00:00Z', 'files': files})
    return target


def test_full_repeat_and_draft(batch: Path, tmp_path: Path) -> None:
    workspace = tmp_path / 'workspace with spaces'; deliver(batch, workspace)
    first = automation.run('batch', workspace)
    assert first['status'] == 'SUCCESS' and first['distribution_status'] == 'PREPARED'
    draft = json.loads((workspace / 'outbox' / (first['distribution_id'] + '.json')).read_text(encoding='utf-8'))
    assert draft['status'] == 'PREPARED' and len(draft['attachments']) == 2
    deliver(batch, workspace)
    second = automation.run('batch', workspace)
    assert second['status'] == 'SKIPPED' and second['distribution_status'] == 'NOT_DUPLICATED'
    assert len(list((workspace / 'outbox').glob('*.json'))) == 1
    assert json.loads(json.dumps(second))['status'] == 'SKIPPED'


def test_missing_marker_and_corrupt_file(batch: Path, tmp_path: Path) -> None:
    workspace = tmp_path / 'w'; pending = deliver(batch, workspace)
    (pending / 'READY.json').unlink()
    first = automation.run('batch', workspace)
    assert first['status'] == 'FAILED' and pending.exists()
    automation.write_json(pending / 'READY.json', {'batch_id': 'x', 'received_at': 'x', 'files': {'ventas.csv': 'bad'}})
    second = automation.run('batch', workspace)
    assert second['status'] == 'FAILED' and second['distribution_status'] == 'NOT_PREPARED'
    assert len(list((workspace / 'outbox').glob('*.json'))) == 2


def test_validation_rejection(batch: Path, tmp_path: Path) -> None:
    (batch / 'ventas.csv').write_text('bad,data\n1,2\n', encoding='utf-8')
    workspace = tmp_path / 'w'; deliver(batch, workspace)
    result = automation.run('batch', workspace)
    assert result['status'] == 'REJECTED' and result['distribution_status'] == 'NOT_PREPARED'
    assert list((workspace / 'rejected').iterdir())


@pytest.mark.parametrize('stage', ['analyze', 'generate'])
def test_failure_and_resume(batch: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str) -> None:
    workspace = tmp_path / 'w'; deliver(batch, workspace)
    original = getattr(automation, stage)
    def fail(*args: object, **kwargs: object) -> None: raise RuntimeError('simulated')
    monkeypatch.setattr(automation, stage, fail)
    failed = automation.run('batch', workspace)
    assert failed['status'] == 'FAILED' and failed['distribution_status'] == 'NOT_PREPARED'
    monkeypatch.setattr(automation, stage, original)
    deliver(batch, workspace)
    recovered = automation.run('batch', workspace)
    assert recovered['status'] == 'SUCCESS' and recovered['stages']['pipeline']['status'] == 'REUSED'
    assert recovered['distribution_status'] == 'PREPARED'


def test_corrupt_report_requires_explicit_quarantine(batch: Path, tmp_path: Path) -> None:
    workspace = tmp_path / 'w'; deliver(batch, workspace)
    first = automation.run('batch', workspace)
    report = first['stages']['reports']; damaged = Path(report['output_dir']) / report['files'][0]['name']
    damaged.write_bytes(b'damaged')
    deliver(batch, workspace); assert automation.run('batch', workspace)['status'] == 'FAILED'
    deliver(batch, workspace); recovered = automation.run('batch', workspace, recover_corrupt=True)
    assert recovered['status'] == 'SUCCESS' and recovered['distribution_status'] == 'NOT_DUPLICATED'
    assert list((workspace / 'quarantine').iterdir())
    assert (workspace / 'outbox' / ('invalidated-' + first['distribution_id'] + '.json')).is_file()


def test_existing_lock_does_not_process(batch: Path, tmp_path: Path) -> None:
    workspace = tmp_path / 'w'; pending = deliver(batch, workspace); (workspace / '.automation.lock').mkdir()
    result = automation.run('batch', workspace)
    assert result['status'] == 'FAILED' and pending.exists()


def test_two_concurrent_calls(batch: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / 'w'; deliver(batch, workspace)
    entered, release = threading.Event(), threading.Event()
    original = automation.execute
    def paused(*args: object, **kwargs: object) -> dict:
        entered.set(); assert release.wait(30)
        return original(*args, **kwargs)
    monkeypatch.setattr(automation, 'execute', paused)
    results: list[dict] = []
    thread = threading.Thread(target=lambda: results.append(automation.run('batch', workspace)))
    thread.start(); assert entered.wait(30)
    second = automation.run('batch', workspace)
    release.set(); thread.join(60)
    assert not thread.is_alive() and second['status'] == 'FAILED' and results[0]['status'] == 'SUCCESS'


def test_changed_analysis_creates_new_reports_without_new_draft(batch: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.ai_analysis.engine as engine
    workspace = tmp_path / 'w'; deliver(batch, workspace)
    first = automation.run('batch', workspace)
    monkeypatch.setattr(engine, 'fingerprint', lambda: 'different-test-fingerprint')
    deliver(batch, workspace); second = automation.run('batch', workspace)
    assert second['status'] == 'SUCCESS' and second['distribution_status'] == 'NOT_DUPLICATED'
    assert second['stages']['reports']['generation_id'] != first['stages']['reports']['generation_id']
    assert len(list((workspace / 'outbox').glob('*.json'))) == 1
