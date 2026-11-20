"""Regression coverage for archived batches and empty inbox conditions."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
import pytest
from test_validation_engine import batch
from test_automation import deliver
from scripts import run_automation as automation


def test_archive_repeat_verifies_evidence_without_duplicate(batch: Path, tmp_path: Path) -> None:
    workspace = tmp_path / 'workspace'; deliver(batch, workspace)
    first = automation.run('batch', workspace)
    before = set((workspace / 'outbox').iterdir())
    result = automation.run('batch', workspace)
    assert result['status'] == 'SKIPPED' and result['reason'] == 'ALREADY_PROCESSED_VERIFIED'
    assert result['prior_automation_id'] == first['automation_id'] and result['distribution_status'] == 'NOT_DUPLICATED'
    assert set((workspace / 'outbox').iterdir()) == before
    assert json.loads(json.dumps(result))['inbox_status'] == 'EMPTY'


@pytest.mark.parametrize('target', ['report', 'draft', 'receipt', 'analysis', 'invalidated'])
def test_altered_or_invalidated_archive_is_not_skipped(batch: Path, tmp_path: Path, target: str) -> None:
    workspace = tmp_path / 'workspace'; deliver(batch, workspace)
    first = automation.run('batch', workspace)
    ledger = json.loads((workspace / 'state' / (first['batch_key'] + '.json')).read_text(encoding='utf-8'))
    if target == 'report': path = Path(ledger['report_dir']) / first['stages']['reports']['files'][0]['name']
    elif target == 'draft': path = workspace / 'outbox' / (first['distribution_id'] + '.json')
    elif target == 'analysis': path = Path(ledger['analysis_path'])
    elif target == 'receipt': path = workspace / 'processed' / ('batch-' + first['automation_id']) / 'ventas.csv'
    else: path = workspace / 'outbox' / ('invalidated-' + first['distribution_id'] + '.json')
    path.write_text('{}', encoding='utf-8')
    result = automation.run('batch', workspace)
    assert result['status'] == 'FAILED' and result['reason'] == 'HISTORY_UNVERIFIED'
    assert result['distribution_status'] == 'NOT_PREPARED'


def test_empty_pending_and_unknown_batch(tmp_path: Path) -> None:
    workspace = tmp_path / 'workspace'
    assert automation.pending_status(workspace)['status'] == 'EMPTY'
    result = automation.run('unknown', workspace)
    assert result['status'] == 'FAILED' and result['reason'] == 'BATCH_NOT_RECEIVED' and result['inbox_status'] == 'EMPTY'
    assert automation.run('unknown', workspace)['reason'] == 'BATCH_NOT_RECEIVED'


def test_pending_list_and_incomplete_receipt(batch: Path, tmp_path: Path) -> None:
    workspace = tmp_path / 'workspace'; pending = deliver(batch, workspace)
    (pending / 'READY.json').unlink()
    assert automation.pending_status(workspace)['pending'] == [{'batch': 'batch', 'receipt_marker_present': False}]
    result = automation.run('batch', workspace)
    assert result['status'] == 'FAILED' and result['reason'] == 'BATCH_INCOMPLETE' and pending.exists()


def test_invalid_batch_and_previous_rejection(batch: Path, tmp_path: Path) -> None:
    (batch / 'ventas.csv').write_text('bad,data\n1,2\n', encoding='utf-8')
    workspace = tmp_path / 'workspace'; deliver(batch, workspace)
    first = automation.run('batch', workspace)
    assert first['status'] == 'REJECTED' and first['reason'] == 'INVALID_BATCH'
    assert automation.run('batch', workspace)['reason'] == 'BATCH_PREVIOUSLY_REJECTED'


def test_technical_failure_classified(batch: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / 'workspace'; deliver(batch, workspace)
    def fail(*args: object, **kwargs: object) -> None: raise OSError('test')
    monkeypatch.setattr(automation, 'analyze', fail)
    assert automation.run('batch', workspace)['reason'] == 'TECHNICAL_ERROR'
    assert automation.run('batch', workspace)['reason'] == 'BATCH_PREVIOUSLY_FAILED'


def test_pending_cli_json_does_not_create_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / 'not created'
    script = Path(automation.__file__)
    proc = subprocess.run([sys.executable, str(script), '--workspace', str(workspace), '--list-pending'], capture_output=True, text=True, check=True)
    assert json.loads(proc.stdout)['reason'] == 'INBOX_EMPTY' and not workspace.exists()


def test_archive_without_success_journal_is_not_unknown(tmp_path: Path) -> None:
    workspace = tmp_path / 'workspace'; (workspace / 'processed' / 'batch-00000000-0000-0000-0000-000000000001').mkdir(parents=True)
    result = automation.run('batch', workspace)
    assert result['status'] == 'FAILED' and result['reason'] == 'HISTORY_UNVERIFIED'
