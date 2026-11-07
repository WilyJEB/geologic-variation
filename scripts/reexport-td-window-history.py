"""Strict original-source retained exports plus current offline evidence. No TD."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def run(output):
    def module(name):
        return runpy.run_path(str(ROOT/'scripts'/name))
    def expected(name):
        return json.loads((ROOT/'docs/evidence'/name).read_text())
    def equal(name, actual):
        assert json.loads(json.dumps(actual))==expected(name),name
        print('PASS strict re-export',name,flush=True)
    module('reexport-td-bounded.py')['run'](output)
    equal('td-axis-summary.json',module('export-td-axis.py')['export']())
    equal('td-identical.json',module('export-td-identical.py')['export'](
        ROOT/'runs/acceptance/td-identical-2026-11-04-01', output/'reexport-identical.zip'))
    for script,stem in (('audit-td-history.py','td-observation-history'),
                        ('model-td-window-history.py','td-window-history')):
        before=expected(stem+'.json')
        digest=hashlib.sha256((ROOT/'docs/evidence'/(stem+'.zip')).read_bytes()).hexdigest()
        actual=module(script)['export']()
        assert actual==before,stem
        assert hashlib.sha256((ROOT/'docs/evidence'/(stem+'.zip')).read_bytes()).hexdigest()==digest,stem
        print('PASS strict re-export',stem,flush=True)
    (output/'current-strict-reexport.json').write_text(json.dumps(dict(
        offline_only=True, unchanged_assertions=True, retained_and_new_exports_match=True),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path)
    run(p.parse_args().output)
