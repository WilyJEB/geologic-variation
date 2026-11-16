"""Offline-only deterministic packaging and mock tests; never constructs WindowsAPI."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['scripts/windows_process_monitor.py', 'scripts/test-windows-process-monitor.py',
         'scripts/audit-process-monitor-preparation.py', 'docs/windows-process-monitor-preparation.md']
OUTPUT = ROOT / 'docs/evidence/windows-process-monitor-preparation'


def digest(data): return hashlib.sha256(data).hexdigest()


def build():
    spec = importlib.util.spec_from_file_location('offline_monitor_tests', ROOT / FILES[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    if not result.wasSuccessful():
        raise AssertionError(result.errors + result.failures)
    data = {name: (ROOT / name).read_bytes() for name in FILES}
    runtime = (ROOT / 'docs/evidence/td-navigation-3-runtime.zip').read_bytes()
    assert digest(runtime) == '52319ac3ab554e9d183b004792cc1d5b7a0328f7a1666ab8a50651a033f465a5'
    manifest = json.loads((ROOT / 'docs/td-navigation-3-hashes.json').read_bytes())
    external = {'docs/td-region-viewer.html', 'scripts/build-td-region-preview.py'}
    with zipfile.ZipFile(io.BytesIO(runtime)) as executed:
        with zipfile.ZipFile(ROOT / 'docs/evidence/td-navigation-3-preparation.zip') as prepared:
            for name, expected in manifest['files'].items():
                content = executed.read('executed/' + name)
                assert digest(content) == expected
                assert prepared.read(name) == content
                if name not in external or (ROOT / name).exists():
                    assert (ROOT / name).read_bytes() == content
    summary = dict(kind='offline-preparation-only', native_execution=False, allocated_slots=0,
                   mock_tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                   skipped=len(result.skipped), source_sha256={n: digest(b) for n, b in data.items()},
                   retained_runtime_sha256=digest(runtime), retained_acceptance='INCOMPLETE',
                   navigation_3_attempts_remaining=0, frozen_files_verified=len(manifest['files']))
    encoded = (json.dumps(summary, indent=2, sort_keys=True) + '\n').encode()
    data['summary.json'] = encoded
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, content in sorted(data.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 12, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return encoded, buffer.getvalue()


def check_runtime_root():
    # Read bytes only. Never import the frozen helper or inspect running processes.
    root = ROOT / 'runs/acceptance/td-navigation-3'
    if not root.exists():
        raise AssertionError('retained runtime root absent; local preservation check unavailable')
    with zipfile.ZipFile(ROOT / 'docs/evidence/td-navigation-3-runtime.zip') as archive:
        actual = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        expected = {name: archive.read(name) for name in archive.namelist()}
        assert actual == expected, 'retained complete partial root differs from portable archive'
    return len(actual)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check-runtime-root', action='store_true')
    args = parser.parse_args()
    summary, archive = build()
    for suffix, content in [('.json', summary), ('.zip', archive)]:
        path = OUTPUT.with_suffix(suffix)
        if args.write:
            path.write_bytes(content)
        else:
            assert path.read_bytes() == content, f'preparation package differs: {path}'
    if args.check_runtime_root:
        print(f'Retained complete runtime root identical: {check_runtime_root()} files')
    print(summary.decode(), end='')
    print('Portable preparation ZIP SHA256:', digest(archive))
