"""Portable offline harness preparation; no runtime directory or allocation."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['scripts/windows_validation_harness.py', 'scripts/test-windows-validation-harness.py',
         'scripts/audit-windows-harness-preparation.py', 'docs/windows-validation-harness-preparation.md',
         'docs/windows-validation-harness-schema.json']
OUTPUT = ROOT / 'docs/evidence/windows-validation-harness-preparation'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build():
    previous = load('previous_preparation', 'scripts/audit-process-monitor-preparation.py')
    old_summary, old_zip = previous.build()
    assert (ROOT / 'docs/evidence/windows-process-monitor-preparation.json').read_bytes() == old_summary
    assert (ROOT / 'docs/evidence/windows-process-monitor-preparation.zip').read_bytes() == old_zip
    suite = unittest.defaultTestLoader.loadTestsFromModule(load('harness_tests', FILES[1]))
    result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    if not result.wasSuccessful():
        raise AssertionError(result.errors + result.failures)
    data = {name: (ROOT / name).read_bytes() for name in FILES}
    json.loads(data[FILES[-1]])
    summary = dict(kind='offline-partial-harness-preparation', native_execution=False,
                   allocated_slots=0, mock_tests=result.testsRun, previous_mock_tests=23,
                   failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                   native_bootstrap_implemented=False, native_case_runner_implemented=False,
                   source_sha256={n: digest(b) for n, b in data.items()},
                   previous_portable_zip_sha256=digest(old_zip),
                   frozen_files_verified=39, retained_acceptance='INCOMPLETE',
                   navigation_3_attempts_remaining=0)
    encoded = (json.dumps(summary, indent=2, sort_keys=True) + '\n').encode()
    data['summary.json'] = encoded
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, content in sorted(data.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 12, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return encoded, buffer.getvalue()


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
        old = load('retained_root_check', 'scripts/audit-process-monitor-preparation.py')
        print(f'Retained complete runtime root identical: {old.check_runtime_root()} files')
    print(summary.decode(), end='')
    print('Portable preparation ZIP SHA256:', digest(archive))
