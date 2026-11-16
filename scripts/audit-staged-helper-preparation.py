"""Separate portable candidate-D interface preparation; offline only."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['docs/windows-staged-helper-interface-preparation.md',
         'scripts/staged_helper_interfaces.py', 'scripts/test-staged-helper-interfaces.py',
         'scripts/audit-staged-helper-preparation.py']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build():
    old = load('containment_audit', 'scripts/audit-bootstrap-containment-review.py')
    previous = old.build()
    for suffix, content in zip(('.json', '.zip'), previous):
        assert (ROOT / ('docs/evidence/windows-bootstrap-containment-review' + suffix)).read_bytes() == content
    tests = load('staged_tests', FILES[2])
    result = unittest.TextTestRunner(stream=io.StringIO()).run(
        unittest.defaultTestLoader.loadTestsFromModule(tests))
    assert result.wasSuccessful(), result.errors + result.failures
    data = {name: (ROOT / name).read_bytes() for name in FILES}
    digest = lambda b: hashlib.sha256(b).hexdigest()
    summary = dict(kind='offline-staged-helper-interface-preparation', decision=1,
                   basis_commit='86e6639d292292966e76e1843c581d6757d0a34d',
                   main_commit='513c4ca1e950969453faf52723f7ee68c7d6c329',
                   native_execution=False, native_implementation=False,
                   allocated_slots=0, caps_changed=False, fake_tests=result.testsRun,
                   calls=tests.CALLS, issued_bytes=tests.BYTES,
                   source_sha256={n: digest(b) for n, b in data.items()},
                   historical_containment_zip_sha256=digest(previous[1]),
                   retained_acceptance='INCOMPLETE', navigation_3_attempts_remaining=0,
                   limitations=['independent control assumed, not scheduled',
                                'OS termination/atomicity assumed, not executed',
                                'no timing, durability, or cleanup acceptance proof'])
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
        path = ROOT / ('docs/evidence/windows-staged-helper-interface-preparation' + suffix)
        if args.write:
            path.write_bytes(content)
        else:
            assert path.read_bytes() == content, str(path)
    if args.check_runtime_root:
        old = load('root_audit', 'scripts/audit-process-monitor-preparation.py')
        print('Retained complete runtime root identical:', old.check_runtime_root())
    print('Staged preparation reproduced: 8 new + 57 historical fake tests; decision 1 conditional.')
