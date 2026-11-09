"""Portable non-client preflight evidence, separate from frozen client outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def export(strict=False):
    members = {}
    names = ['scripts/'+name for name in (
        'launch-retained-navigation-supplement.py', 'record-navigation-readiness.py',
        'test-navigation-readiness.py', 'export-navigation-readiness.py')]
    names += ['docs/evidence/td-navigation-readiness-'+name+'.json' for name in ('restricted', 'approved')]
    for name in names:
        members[name] = (ROOT/name).read_bytes()
    digest = hashlib.sha256(members[names[0]]).hexdigest()
    records = [json.loads(members[name]) for name in names[-2:]]
    for record in records:
        assert record['launcher_sha256'] == digest
        assert record['allocation_unchanged'] and record['before'] == record['after']
        assert record['mode'] == 'check-only' and not record['client_launched']
        assert all(v['directories'] == ['attempt-01', 'attempt-02'] for v in record['before'].values())
    assert records[0]['context'] == 'restricted' and '10013' in records[0]['error']
    assert records[1]['context'] == 'approved' and records[1]['error'] is None
    assert 'PASS scanned installed libraries' in records[1]['stdout']
    data = runpy.run_path(str(ROOT/'scripts/export-retained-client.py'))['encode'](members)
    path = ROOT/'docs/evidence/td-navigation-readiness.zip'
    if strict:
        assert path.read_bytes() == data
    else:
        path.write_bytes(data)
    print('PASS strict readiness evidence' if strict else 'PASS readiness evidence')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true')
    export(parser.parse_args().strict)
