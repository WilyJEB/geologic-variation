"""Separate deterministic negative preparation package; offline only."""
import argparse
import io
import json
import unittest
import zipfile
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build():
    old = load('historical_harness_audit', 'scripts/audit-windows-harness-preparation.py')
    summary, archive = old.build()
    for suffix, content in (('.json', summary), ('.zip', archive)):
        assert (ROOT / ('docs/evidence/windows-validation-harness-preparation' + suffix)).read_bytes() == content
    tests = load('boundary_tests', 'scripts/test-bootstrap-cleanup-boundary.py')
    result = unittest.TextTestRunner(stream=io.StringIO()).run(
        unittest.defaultTestLoader.loadTestsFromModule(tests))
    assert result.wasSuccessful(), result.errors + result.failures
    files = ['scripts/bootstrap_cleanup_boundary.py', 'scripts/test-bootstrap-cleanup-boundary.py',
             'scripts/audit-bootstrap-boundary-preparation.py',
             'docs/windows-bootstrap-boundary-preparation.md']
    data = {name: (ROOT / name).read_bytes() for name in files}
    summary = dict(kind='offline-bootstrap-boundary-negative-preparation',
                   basis_commit='48b0f7a34e88f19a25c9bc51dd707a2d78de6cb3',
                   native_execution=False, allocated_slots=0, mock_tests=result.testsRun,
                   model_closed_design_gaps=False, decision='stop-before-containment-expansion',
                   counterexamples=[failure for role in ('watchdog', 'sampler')
                                    for failure in tests.uncovered_prefixes(role)],
                   source_sha256={name: old.digest(content) for name, content in data.items()},
                   historical_harness_zip_sha256=old.digest(archive),
                   retained_acceptance='INCOMPLETE', navigation_3_attempts_remaining=0)
    encoded = (json.dumps(summary, sort_keys=True, indent=2) + '\n').encode()
    data['summary.json'] = encoded
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, content in sorted(data.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 12, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return encoded, output.getvalue()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check-runtime-root', action='store_true')
    args = parser.parse_args()
    for suffix, content in zip(('.json', '.zip'), build()):
        path = ROOT / ('docs/evidence/windows-bootstrap-boundary-preparation' + suffix)
        if args.write:
            path.write_bytes(content)
        else:
            assert path.read_bytes() == content, str(path)
    if args.check_runtime_root:
        old = load('root_preservation_audit', 'scripts/audit-process-monitor-preparation.py')
        print('Retained complete runtime root identical:', old.check_runtime_root())
    print('Offline negative preparation reproduced; native design remains stopped.')
