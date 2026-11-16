"""Deterministic review package and retained byte checks. Offline only."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['docs/windows-bootstrap-containment-review.md',
         'scripts/bootstrap_containment_model.py', 'scripts/test-bootstrap-containment.py',
         'scripts/audit-bootstrap-containment-review.py']
DOCS = [
    'https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute',
    'https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw',
    'https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information',
    'https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process',
    'https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects',
    'https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build():
    old = load('boundary_audit', 'scripts/audit-bootstrap-boundary-preparation.py')
    previous = old.build()
    for suffix, content in zip(('.json', '.zip'), previous):
        assert (ROOT / ('docs/evidence/windows-bootstrap-boundary-preparation' + suffix)).read_bytes() == content
    tests = load('containment_tests', FILES[2])
    result = unittest.TextTestRunner(stream=io.StringIO()).run(
        unittest.defaultTestLoader.loadTestsFromModule(tests))
    assert result.wasSuccessful(), result.errors + result.failures
    data = {name: (ROOT / name).read_bytes() for name in FILES}
    digest = lambda b: hashlib.sha256(b).hexdigest()
    summary = dict(kind='offline-containment-design-review',
                   basis_commit='6d972703223fe20cf81d181b5322550f11a4aac5',
                   main_commit='513c4ca1e950969453faf52723f7ee68c7d6c329',
                   native_execution=False, allocated_slots=0, decision=1,
                   candidate='D-staged-helper-job-copy', interface_implemented=False,
                   native_acceptance=False, hard_deadlines=False, caps_changed=False,
                   documentation_review_date='2026-11-12', documentation_urls=DOCS,
                   fake_tests=result.testsRun, graph_cases=tests.review_cases(),
                   assumptions=['eventual successful OS termination/handle closure',
                                'independent W control established before H duplication',
                                'explicit W target termination action, not scheduled by model'],
                   source_sha256={name: digest(b) for name, b in data.items()},
                   historical_boundary_zip_sha256=digest(previous[1]),
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
        path = ROOT / ('docs/evidence/windows-bootstrap-containment-review' + suffix)
        if args.write:
            path.write_bytes(content)
        else:
            assert path.read_bytes() == content, str(path)
    if args.check_runtime_root:
        old = load('root_audit', 'scripts/audit-process-monitor-preparation.py')
        print('Retained complete runtime root identical:', old.check_runtime_root())
    print('Containment review reproduced: 8 abstract tests; 49 historical mocks; decision 1 conditional.')
