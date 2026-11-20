"""Read only verified local pipeline artifacts from fixed project roots."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from src.ai_analysis.engine import validate_for_reporting
from src.reporting.source import FILES, load_source

ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ('workspace_pad', 'workspace_pad_success', 'workspace_pad_rejected')


@dataclass(frozen=True)
class CatalogEntry:
    """A predefined local artifact root and a pipeline identifier."""
    label: str
    path: Path
    run_id: str
    artifact_root: Path


def contained(path: Path, root: Path) -> bool:
    """Reject links and paths escaping the explicitly configured project root."""
    try:
        path.relative_to(root)
        if root.is_symlink() or any(p.is_symlink() for p in (path, *path.parents) if p == root or root in p.parents):
            return False
        return path.resolve().is_relative_to(root.resolve())
    except (ValueError, OSError):
        return False


def catalog(root: Path = ROOT) -> list[CatalogEntry]:
    """List only UUID-named direct children of fixed output directories."""
    roots = [('Ejecución local', root / 'data' / 'processed', root)]
    roots.extend((name, root / 'automation' / name / 'processed_data', root / 'automation' / name) for name in WORKSPACES)
    entries = []
    for label, folder, artifact_root in roots:
        if not folder.is_dir() or not contained(folder, root): continue
        for path in sorted(folder.iterdir(), key=lambda x: x.name):
            try: run_id = str(UUID(path.name))
            except ValueError: continue
            if path.name == run_id and path.is_dir() and contained(path, root):
                entries.append(CatalogEntry(label, path, run_id, artifact_root))
    return entries


def read_entry(entry: CatalogEntry, root: Path = ROOT) -> dict:
    """Validate source and identifier again before displaying any data."""
    if entry not in catalog(root) or not contained(entry.path, root): raise ValueError('Ejecución fuera del catálogo')
    if any(not contained(entry.path / name, root) for name in FILES): raise ValueError('Archivo fuera del catálogo')
    source = load_source(entry.path)
    if source['manifest']['pipeline_run_id'] != entry.run_id: raise ValueError('Identificador de ejecución inconsistente')
    return source


def artifact_folders(entry: CatalogEntry) -> tuple[list[Path], list[Path]]:
    """Return fixed analysis and report roots for the selected execution."""
    root = entry.artifact_root
    if entry.label == 'Ejecución local':
        return [root / 'reports' / 'ai_analysis'], [root / 'reports' / name for name in ('generated', 'ai_enriched', 'visual_final', 'pdf_visual_final')]
    return [root / 'analysis'], [root / 'reports']


def local_analyses(entry: CatalogEntry, source: dict) -> list[tuple[str, dict]]:
    """Accept only locally produced, validated analyses matching the source."""
    roots, _ = artifact_folders(entry); results = []
    for folder in roots:
        if not folder.is_dir() or not contained(folder, entry.artifact_root): continue
        for path in sorted(folder.glob('*.json')):
            if not contained(path, entry.artifact_root): continue
            try:
                raw = path.read_bytes(); data = json.loads(raw)
                if data.get('mode') not in {'local', 'local_fallback'}: continue
                validate_for_reporting(data, source)
                results.append((hashlib.sha256(raw).hexdigest(), data))
            except (OSError, ValueError, KeyError, TypeError): continue
    return results


def provenance(entry: CatalogEntry) -> dict | None:
    """Read optional automation metadata from fixed workspace run journals."""
    if entry.label == 'Ejecución local': return None
    root = entry.artifact_root; folder = root / 'runs'
    if not folder.is_dir() or not contained(folder, root): return None
    records = []
    for path in folder.glob('*.json'):
        if not contained(path, root): continue
        try:
            item = json.loads(path.read_bytes())
            if item.get('status') != 'SUCCESS' or item.get('stages', {}).get('pipeline', {}).get('details', {}).get('run_id') != entry.run_id: continue
            batch_id = item.get('batch_id', '')
            if not isinstance(batch_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', batch_id): continue
            distribution_id = item.get('distribution_id')
            state = 'No disponible'
            if isinstance(distribution_id, str) and re.fullmatch(r'[0-9a-f]{64}', distribution_id):
                draft = root / 'outbox' / (distribution_id + '.json')
                invalid = root / 'outbox' / ('invalidated-' + distribution_id + '.json')
                if invalid.exists(): state = 'Borrador invalidado; requiere revisión'
                elif contained(draft, root) and draft.is_file():
                    saved = json.loads(draft.read_bytes())
                    if saved.get('status') == 'PREPARED' and saved.get('distribution_id') == distribution_id and saved.get('batch_key') == item.get('batch_key'):
                        state = 'PREPARED · borrador local'
            records.append({'batch_id': batch_id, 'automation_id': item.get('automation_id'), 'distribution_status': state})
        except (OSError, ValueError, KeyError, TypeError): continue
    return records[0] if len(records) == 1 else None


def report_inventory(entry: CatalogEntry, source: dict) -> tuple[list[dict], list[dict]]:
    """Classify report generations without changing any historical artifact."""
    _, roots = artifact_folders(entry); valid = []; issues = []
    analysis_hashes = {item[0] for item in local_analyses(entry, source)}
    for folder in roots:
        if not folder.is_dir() or not contained(folder, entry.artifact_root): continue
        for directory in sorted(folder.iterdir(), key=lambda p: p.name):
            if not directory.is_dir() or not re.fullmatch(r'[0-9a-f]{64}', directory.name) or not contained(directory, entry.artifact_root): continue
            generation_id = directory.name; associated = False
            try:
                manifest_path = directory / 'manifest.json'
                if not contained(manifest_path, entry.artifact_root): raise ValueError('Invalid path')
                manifest = json.loads(manifest_path.read_bytes())
                if manifest.get('pipeline_run_id') != entry.run_id: continue
                associated = True
                generation_id = str(manifest.get('generation_id') or directory.name)
                if manifest.get('status') != 'SUCCESS' or manifest.get('source_hashes') != source['hashes'] or manifest.get('request_key') != directory.name: raise ValueError('Inconsistent report manifest')
                if manifest.get('analysis_sha256') is not None and manifest['analysis_sha256'] not in analysis_hashes: raise ValueError('Analysis unavailable or invalid')
                records = manifest.get('files')
                if not isinstance(records, list) or not records or len(records) > 2: raise ValueError('Invalid files')
                payload = []
                expected = {'AutoReport360_Reporte_Comercial_' + source['manifest']['cutoff'][:7] + '.xlsx', 'AutoReport360_Informe_Ejecutivo_' + source['manifest']['cutoff'][:7] + '.pdf'}
                if len({item.get('name') for item in records}) != len(records) or not {item.get('name') for item in records}.issubset(expected): raise ValueError('Invalid names')
                formats = {'both': 2, 'excel': 1, 'pdf': 1}
                if len(records) != formats.get(manifest.get('format')): raise ValueError('Missing format')
                extensions = {'both': {'.xlsx', '.pdf'}, 'excel': {'.xlsx'}, 'pdf': {'.pdf'}}
                if {Path(item['name']).suffix for item in records} != extensions[manifest['format']]: raise ValueError('Invalid report format')
                for item in records:
                    path = directory / item['name']
                    if not contained(path, entry.artifact_root): raise ValueError('Invalid path')
                    raw = path.read_bytes()
                    if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']: raise ValueError('Corrupt report')
                    payload.append({'name': item['name'], 'bytes': raw, 'sha256': item['sha256']})
                valid.append({'id': manifest['generation_id'], 'generated_at': manifest['generated_at'], 'files': payload})
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
                reasons = {'Analysis unavailable or invalid': 'El análisis asociado no está disponible o no supera la validación.', 'Corrupt report': 'El tamaño o la huella de un archivo no coincide.', 'Inconsistent report manifest': 'El manifiesto no coincide con la ejecución o su origen.', 'Invalid path': 'Ruta fuera del catálogo permitido.', 'Invalid files': 'La lista de archivos del manifiesto no es válida.', 'Invalid names': 'Los nombres de los informes no son válidos.', 'Missing format': 'Falta un archivo del formato solicitado.', 'Invalid report format': 'El formato de los archivos no coincide con el manifiesto.'}
                reason = reasons.get(str(exc), 'No fue posible leer o validar el manifiesto y sus archivos.')
                if not associated: reason += ' No se pudo confirmar su asociación con esta ejecución.'
                issues.append({'id': generation_id, 'reason': reason})
    return valid, issues


def verified_reports(entry: CatalogEntry, source: dict) -> tuple[list[dict], int]:
    """Return only complete verified generations and their issue count."""
    valid, issues = report_inventory(entry, source)
    return valid, len(issues)
