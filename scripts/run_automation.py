"""Run the commercial pipeline and prepare local, simulated delivery drafts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_pipeline import execute
from src.ai_analysis.engine import analyze
from src.reporting.generator import generate
from src.reporting.source import load_source
from src.ai_analysis.engine import validate_for_reporting


class BatchCondition(Exception):
    """Carry a stable machine-readable condition without changing exit semantics."""
    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


def now() -> str:
    """Return an unambiguous UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    """Return a content digest for a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: dict) -> None:
    """Replace a local journal atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)


def receipt(folder: Path) -> tuple[dict, str]:
    """Validate a completion marker and ensure all input files match its hashes."""
    marker = folder / 'READY.json'
    if not marker.is_file():
        raise ValueError('Falta READY.json: recepción incompleta')
    data = json.loads(marker.read_text(encoding='utf-8'))
    files = data.get('files')
    if not isinstance(data.get('batch_id'), str) or not data['batch_id'] or not isinstance(data.get('received_at'), str) or not isinstance(files, dict) or not files:
        raise ValueError('Manifiesto de recepción inválido')
    for name, expected in files.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or len(relative.parts) > 2 or (len(relative.parts) == 2 and relative.parts[0] != 'masters'):
            raise ValueError('Ruta no admitida en manifiesto')
        path = folder / relative
        if any(part.is_symlink() for part in (path, path.parent) if part != folder) or not path.is_file() or not isinstance(expected, str) or digest(path) != expected:
            raise ValueError('Archivo ausente o huella incorrecta: ' + name)
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name != 'READY.json'}
    if actual != set(files): raise ValueError('Archivos no declarados o ausentes')
    key = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return data, key


def verify_reports(result: dict, analysis_path: Path) -> list[dict]:
    """Verify the expected artifacts, sizes, hashes and analysis association."""
    if result.get('analysis_sha256') != digest(analysis_path): raise ValueError('Análisis del reporte no coincide')
    files = result.get('files', [])
    if len(files) != 2 or {Path(x['name']).suffix for x in files} != {'.xlsx', '.pdf'}: raise ValueError('Entregables incompletos')
    output = Path(result['output_dir'])
    for item in files:
        name = item['name']
        if Path(name).name != name: raise ValueError('Nombre de reporte inválido')
        path = output / name
        if not path.is_file() or path.stat().st_size != item['bytes'] or digest(path) != item['sha256']: raise ValueError('Reporte ausente o corrupto')
    return files


def pending_status(workspace: Path) -> dict:
    """Describe pending folders without processing them or modifying the workspace."""
    folder = workspace / 'pending'
    entries = [] if not folder.is_dir() else [{'batch': p.name, 'receipt_marker_present': (p / 'READY.json').is_file()} for p in sorted(folder.iterdir()) if p.is_dir()]
    return {'status': 'PENDING' if entries else 'EMPTY', 'reason': 'PENDING_BATCHES' if entries else 'INBOX_EMPTY', 'pending': entries, 'distribution_status': 'NOT_PREPARED'}


def verify_archived(batch: str, workspace: Path) -> dict | None:
    """Verify archived receipt, journals, source, report and draft without regenerating."""
    successes = []
    for path in (workspace / 'runs').glob('*.json'):
        try:
            item = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            continue
        if item.get('batch') == batch and item.get('status') == 'SUCCESS':
            successes.append(item)
    if not successes:
        return None
    if len({item.get('batch_key') for item in successes}) != 1:
        raise BatchCondition('AMBIGUOUS_HISTORY', 'Hay distintas ejecuciones exitosas con el mismo nombre; revisar historial.')
    previous = successes[0]
    try:
        run_id = str(uuid.UUID(previous['automation_id']))
        archived = workspace / 'processed' / (batch + '-' + run_id)
        info, key = receipt(archived)
        if key != previous['batch_key'] or info['batch_id'] != previous['batch_id'] or info['files'] != previous['files']:
            raise ValueError('Recepción archivada no coincide')
        ledger = json.loads((workspace / 'state' / (key + '.json')).read_text(encoding='utf-8'))
        pipeline = ledger['pipeline']; old_pipeline = previous['stages']['pipeline']['details']
        if pipeline['run_id'] != old_pipeline['run_id'] or pipeline['status'] != 'SUCCESS': raise ValueError('Diario de pipeline no coincide')
        source = load_source(Path(pipeline['output']))
        analysis_path = Path(ledger['analysis_path'])
        analysis = json.loads(analysis_path.read_text(encoding='utf-8'))
        validate_for_reporting(analysis, source)
        report_dir = Path(ledger['report_dir'])
        manifest = json.loads((report_dir / 'manifest.json').read_text(encoding='utf-8'))
        files = verify_reports({**manifest, 'output_dir': str(report_dir)}, analysis_path)
        if manifest['source_hashes'] != source['hashes'] or manifest['pipeline_run_id'] != pipeline['run_id'] or manifest['status'] != 'SUCCESS': raise ValueError('Manifiesto de reporte no coincide')
        distribution_id = ledger['distribution_id']
        if distribution_id != key or (workspace / 'outbox' / ('invalidated-' + distribution_id + '.json')).exists(): raise ValueError('Borrador invalidado o identidad incompatible')
        draft = json.loads((workspace / 'outbox' / (distribution_id + '.json')).read_text(encoding='utf-8'))
        expected = [{'path': str(report_dir / item['name']), 'sha256': item['sha256']} for item in files]
        if draft['distribution_id'] != distribution_id or draft['batch_key'] != key or draft['status'] != 'PREPARED' or draft['attachments'] != expected: raise ValueError('Borrador no coincide')
        return {'prior_automation_id': run_id, 'batch_id': info['batch_id'], 'batch_key': key, 'distribution_id': distribution_id, 'analysis_id': analysis['analysis_id'], 'generation_id': manifest['generation_id']}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise BatchCondition('HISTORY_UNVERIFIED', 'La evidencia archivada está incompleta, alterada o no coincide.') from exc


def absent_reason(batch: str, workspace: Path) -> str:
    """Distinguish a never-received name from an unsuccessful received batch."""
    def matches(path: Path) -> bool:
        if not path.is_dir() or not path.name.startswith(batch + '-'): return False
        try: return str(uuid.UUID(path.name[len(batch) + 1:])) == path.name[len(batch) + 1:]
        except ValueError: return False
    if any(matches(p) for p in (workspace / 'processed').iterdir()):
        return 'HISTORY_UNVERIFIED'
    seen = set()
    for path in (workspace / 'runs').glob('*.json'):
        try: item = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError): continue
        if item.get('batch') == batch and item.get('batch_key') and item.get('status') in {'REJECTED', 'FAILED'}:
            seen.add(item['status'])
    for folder, status in [('rejected', 'REJECTED'), ('failed', 'FAILED')]:
        if any(matches(p) and (p / 'READY.json').is_file() for p in (workspace / folder).iterdir()):
            seen.add(status)
    return 'BATCH_PREVIOUSLY_REJECTED' if 'REJECTED' in seen else 'BATCH_PREVIOUSLY_FAILED' if 'FAILED' in seen else 'BATCH_NOT_RECEIVED'


def run(batch: str, workspace: Path, mode: str = 'local', recover_corrupt: bool = False) -> dict:
    """Serialize one workspace and resume a previously persisted batch safely."""
    if Path(batch).name != batch or batch in {'', '.', '..'}: raise ValueError('Nombre de lote inválido')
    if mode != 'local': raise ValueError('Solo se admite análisis local sin servicios externos')
    started = time.perf_counter(); run_id = str(uuid.uuid4())
    workspace = workspace.resolve()
    for name in ('pending', 'processing', 'processed', 'rejected', 'failed', 'state', 'runs', 'outbox', 'analysis', 'reports', 'processed_data', 'quarantine'):
        (workspace / name).mkdir(parents=True, exist_ok=True)
    result = {'automation_id': run_id, 'batch': batch, 'started_at': now(), 'status': 'FAILED', 'distribution_status': 'NOT_PREPARED', 'stages': {}, 'errors': [], 'warnings': []}
    lock = workspace / '.automation.lock'
    acquired = False; claimed = False; active = workspace / 'processing' / batch
    try:
        try: lock.mkdir(); acquired = True
        except FileExistsError: raise RuntimeError('Otra automatización usa el mismo espacio de trabajo')
        pending = workspace / 'pending' / batch
        if pending.exists() and active.exists(): raise ValueError('Ya existe un lote en procesamiento con ese nombre')
        if pending.exists():
            if not (pending / 'READY.json').is_file(): raise ValueError('Falta READY.json: recepción incompleta')
            pending.rename(active)
        if not active.is_dir():
            previous = verify_archived(batch, workspace)
            if previous:
                result.update(previous, status='SKIPPED', reason='ALREADY_PROCESSED_VERIFIED', distribution_status='NOT_DUPLICATED', inbox_status=pending_status(workspace)['status'])
                return result
            raise BatchCondition(absent_reason(batch, workspace), 'No hay un lote activo ni una ejecución exitosa verificable para ese nombre.')
        claimed = True
        tick = time.perf_counter()
        try: info, key = receipt(active)
        except (ValueError, OSError) as exc: raise BatchCondition('INVALID_BATCH', 'Manifiesto o archivos del lote inválidos.') from exc
        result.update(batch_id=info['batch_id'], received_at=info['received_at'], batch_key=key, files=info['files'])
        result['stages']['receipt'] = {'status': 'SUCCESS', 'seconds': round(time.perf_counter()-tick, 6)}
        ledger_path = workspace / 'state' / (key + '.json')
        ledger = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else {}
        already_prepared = bool(ledger.get('distribution_id'))
        pipeline = ledger.get('pipeline')
        if pipeline is None:
            tick = time.perf_counter()
            pipeline = execute(active, workspace / 'state' / 'pipeline', workspace / 'processed_data', active / 'masters')
            result['stages']['pipeline'] = {'status': pipeline['status'], 'seconds': round(time.perf_counter()-tick, 6), 'details': pipeline}
            if pipeline['status'] != 'SUCCESS':
                if pipeline.get('persistence_status') == 'PERSISTED':
                    ledger['recovering_after_persistence'] = True
                    write_json(ledger_path, ledger)
                result['status'] = 'REJECTED' if pipeline['status'] == 'REJECTED' else 'FAILED'
                result['reason'] = 'INVALID_BATCH' if pipeline['status'] == 'REJECTED' else 'TECHNICAL_ERROR'
                result['errors'] = pipeline.get('errors', [pipeline.get('error', 'Pipeline failed')])
                raise RuntimeError('Pipeline no completado')
            ledger['pipeline'] = pipeline
            write_json(ledger_path, ledger)
        else:
            result['stages']['pipeline'] = {'status': 'REUSED', 'details': pipeline}
        # Recheck the claimed immutable reception before allowing outputs.
        if receipt(active)[1] != key: raise ValueError('Lote modificado durante el procesamiento')
        source = Path(pipeline['output'])
        quality = json.loads((source / 'quality.json').read_text(encoding='utf-8'))
        result['warnings'] = quality.get('warnings', [])
        tick = time.perf_counter(); analysis = analyze(source, workspace / 'analysis', mode)
        result['stages']['analysis'] = {'status': analysis['execution_status'], 'analysis_id': analysis['analysis_id'], 'seconds': round(time.perf_counter()-tick, 6)}
        analysis_path = Path(analysis['path'])
        tick = time.perf_counter()
        try:
            report = generate(source, workspace / 'reports', 'both', analysis_path)
        except ValueError:
            if not recover_corrupt or not ledger.get('report_dir') or ledger.get('analysis_path') != str(analysis_path): raise
            old = Path(ledger['report_dir'])
            if old.parent != workspace / 'reports' or not old.is_dir(): raise ValueError('Destino de recuperación no válido')
            # Quarantine only the previously recorded, demonstrably damaged directory.
            try:
                previous = json.loads((old / 'manifest.json').read_text(encoding='utf-8'))
                verify_reports({**previous, 'output_dir': str(old)}, Path(ledger['analysis_path']))
            except (ValueError, OSError, KeyError, json.JSONDecodeError):
                if ledger.get('distribution_id'):
                    write_json(workspace / 'outbox' / ('invalidated-' + ledger['distribution_id'] + '.json'), {'status': 'INVALIDATED', 'distribution_id': ledger['distribution_id'], 'reason': 'Reporte original ausente o alterado; requiere revisión manual', 'created_at': now()})
                old.rename(workspace / 'quarantine' / (old.name + '-' + uuid.uuid4().hex))
            else: raise ValueError('No se detectó daño en la generación registrada')
            report = generate(source, workspace / 'reports', 'both', analysis_path)
        files = verify_reports(report, analysis_path)
        result['stages']['reports'] = {'status': report['status'], 'seconds': round(time.perf_counter()-tick, 6), 'generation_id': report['generation_id'], 'files': files, 'output_dir': report['output_dir']}
        ledger.update(report_dir=report['output_dir'], analysis_path=str(analysis_path))
        if not already_prepared and (pipeline.get('persistence_status') != 'ALREADY_PERSISTED' or ledger.get('recovering_after_persistence')):
            distribution_id = key
            recommendations = [x['action'] for x in analysis['recommendations'][:3]]
            draft = {'distribution_id': distribution_id, 'batch_key': key, 'status': 'PREPARED', 'subject': 'AutoReport360 — informe comercial', 'body': 'Se prepararon los informes comerciales para revisión. ' + analysis['executive_summary'], 'executive_summary': analysis['executive_summary'], 'recommendations': recommendations, 'attachments': [{'path': str(Path(report['output_dir']) / x['name']), 'sha256': x['sha256']} for x in files], 'created_at': now()}
            draft_path = workspace / 'outbox' / (distribution_id + '.json')
            if not draft_path.exists():
                try:
                    with draft_path.open('x', encoding='utf-8') as stream: json.dump(draft, stream, ensure_ascii=False, indent=2)
                except FileExistsError: pass
            existing = json.loads(draft_path.read_text(encoding='utf-8'))
            if existing.get('batch_key') != key or existing.get('status') != 'PREPARED': raise ValueError('Borrador existente inválido')
            if existing.get('attachments') != draft['attachments']:
                raise ValueError('Borrador previo requiere revisión de adjuntos')
            ledger['distribution_id'] = distribution_id
            result.update(distribution_status='PREPARED', distribution_id=distribution_id)
        else:
            result['distribution_status'] = 'NOT_DUPLICATED'
            result['distribution_id'] = ledger.get('distribution_id')
        result['stages']['distribution'] = {'status': result['distribution_status'], 'distribution_id': result['distribution_id']}
        write_json(ledger_path, ledger)
        result['status'] = 'SKIPPED' if already_prepared and analysis['execution_status'] == 'SKIPPED' and report['status'] == 'SKIPPED' else 'SUCCESS'
        if result['status'] == 'SKIPPED': result['reason'] = 'IDENTICAL_BATCH'
    except Exception as exc:
        result.setdefault('reason', exc.reason if isinstance(exc, BatchCondition) else 'BATCH_INCOMPLETE' if str(exc).startswith('Falta READY.json') else 'TECHNICAL_ERROR')
        result['inbox_status'] = pending_status(workspace)['status']
        result['errors'].append(type(exc).__name__ + ': ' + str(exc))
        alert = {'distribution_id': str(uuid.uuid4()), 'automation_id': run_id, 'status': 'PREPARED_ERROR', 'subject': 'AutoReport360 — incidencia de procesamiento', 'body': 'No se preparó distribución comercial. Revisar el registro local.', 'created_at': now()}
        write_json(workspace / 'outbox' / (alert['distribution_id'] + '.json'), alert)
        result['alert_id'] = alert['distribution_id']
    finally:
        result['finished_at'] = now(); result['robot_seconds'] = round(time.perf_counter()-started, 6)
        if acquired:
            if claimed and active.is_dir():
                destination = {'SUCCESS': 'processed', 'SKIPPED': 'processed', 'REJECTED': 'rejected'}.get(result['status'], 'failed')
                active.rename(workspace / destination / (batch + '-' + run_id))
            lock.rmdir()
        write_json(workspace / 'runs' / (run_id + '.json'), result)
    return result


def main() -> int:
    """Expose a single JSON result and stable automation exit codes."""
    parser = argparse.ArgumentParser()
    parser.add_argument('batch', nargs='?'); parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--mode', choices=['local'], default='local'); parser.add_argument('--recover-corrupt', action='store_true')
    parser.add_argument('--list-pending', action='store_true', help='List pending batches without processing')
    args = parser.parse_args()
    if args.list_pending and args.batch: parser.error('Do not combine a batch name with --list-pending')
    if not args.list_pending and not args.batch: parser.error('A batch name is required')
    try: result = pending_status(args.workspace) if args.list_pending else run(args.batch, args.workspace, args.mode, args.recover_corrupt)
    except Exception as exc: result = {'status': 'FAILED', 'errors': [type(exc).__name__ + ': ' + str(exc)], 'distribution_status': 'NOT_PREPARED'}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] in {'SUCCESS', 'SKIPPED', 'EMPTY', 'PENDING'} else 2 if result['status'] == 'REJECTED' else 1


if __name__ == '__main__': raise SystemExit(main())
