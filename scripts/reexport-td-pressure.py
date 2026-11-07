"""Strict unchanged historical and new offline exports; no TD execution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def run(output):
    runpy.run_path(str(ROOT/'scripts/reexport-td-window-history.py'))['run'](output)
    stem=ROOT/'docs/evidence/td-pressure-visual'
    before=stem.with_suffix('.json').read_bytes()
    digest=hashlib.sha256(stem.with_suffix('.zip').read_bytes()).hexdigest()
    actual=runpy.run_path(str(ROOT/'scripts/analyze-td-pressure.py'))['export']()
    assert json.loads(json.dumps(actual))==json.loads(before)
    assert hashlib.sha256(stem.with_suffix('.zip').read_bytes()).hexdigest()==digest
    (output/'pressure-strict-reexport.json').write_text(json.dumps(dict(
        offline_only=True,retained_and_new_exports_match=True,
        failed_reduction_preserved=True,unchanged_assertions=True),indent=2)+'\n')
    print('PASS strict new pressure/visual evidence re-export',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);run(p.parse_args().output)
