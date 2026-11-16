"""Portable offline decision/provenance audit; no native adapters or execution."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['docs/windows-staged-helper-native-decision.md',
         'scripts/audit-staged-helper-native-decision.py']
BASIS = ['docs/windows-staged-helper-interface-preparation.md',
         'scripts/staged_helper_interfaces.py',
         'scripts/test-staged-helper-interfaces.py',
         'docs/windows-bootstrap-containment-review.md',
         'docs/windows-bootstrap-boundary-preparation.md',
         'docs/windows-bootstrap-design-review.md',
         'docs/windows-process-monitor-preparation.md',
         'docs/windows-validation-harness-preparation.md',
         'docs/td-navigation-3-outcome.md',
         'docs/td-navigation-process-review.md']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build():
    old = load('staged_preparation_audit', 'scripts/audit-staged-helper-preparation.py')
    previous = old.build()
    for suffix, content in zip(('.json', '.zip'), previous):
        assert (ROOT / ('docs/evidence/windows-staged-helper-interface-preparation' + suffix)).read_bytes() == content
    # Arithmetic witnesses against the advertised envelope, not an actual native trace.
    action_calls = 2 + 2 + 4 + 4 + 20
    advertised_error_calls = 8
    assert action_calls + advertised_error_calls == 40
    assert action_calls * 2 == 64 > 40
    assert 20 * 2 == 40
    assert 64 * 10 == 640 > 400
    digest = lambda b: hashlib.sha256(b).hexdigest()
    data = {name: (ROOT / name).read_bytes() for name in FILES + BASIS}
    summary = dict(
        kind='offline-staged-helper-native-implementation-preparation-decision',
        decision=2, basis_commit='a5161ec851e82959fd1fb6ab780ecd580d5298b8',
        main_commit='513c4ca1e950969453faf52723f7ee68c7d6c329',
        native_implementation=False, native_execution=False, allocated_slots=0,
        caps_changed=False, retained_acceptance='INCOMPLETE',
        navigation_3_attempts_remaining=0,
        inherited_staged_zip_sha256=digest(previous[1]),
        source_sha256={name: digest(content) for name, content in data.items()},
        arithmetic_witnesses=dict(advertised_action_calls=action_calls,
                                  advertised_error_calls=advertised_error_calls,
                                  all_action_failures_with_error_retrieval=64,
                                  twenty_failed_closes_with_error_retrieval=40,
                                  existing_two_target_sampler_64_samples=640),
        limitations=['witnesses audit advertised maxima, not an exact native inventory',
                     'no timing, memory, durability or cleanup acceptance proof',
                     'all-runtime issuance accounting and control schedule unresolved'])
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
        path = ROOT / ('docs/evidence/windows-staged-helper-native-decision' + suffix)
        if args.write:
            path.write_bytes(content)
        else:
            assert path.read_bytes() == content, str(path)
    if args.check_runtime_root:
        old = load('native_decision_root_audit', 'scripts/audit-process-monitor-preparation.py')
        print('Retained complete runtime root identical:', old.check_runtime_root())
    print('Native preparation decision reproduced: STOP; 65 inherited fake tests; no native proof.')
