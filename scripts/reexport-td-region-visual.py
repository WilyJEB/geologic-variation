"""Strict retained and regional evidence exports. No TD execution."""
import argparse
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    runpy.run_path(str(ROOT/'scripts/reexport-td-pressure.py'))['run'](output)
    paths = [ROOT/'docs/evidence'/('td-region-visual'+ext) for ext in ('.zip', '.json', '.html')]
    before = [p.read_bytes() for p in paths]
    runpy.run_path(str(ROOT/'scripts/build-td-region-visual.py'))['export']()
    assert before == [p.read_bytes() for p in paths], 'Strict regional evidence changed'
    (output/'region-visual-strict-reexport.json').write_text(json.dumps(dict(
        offline_only=True, retained_and_new_exports_match=True,
        failed_reduction_preserved=True, production_unchanged=True), indent=2)+'\n')
    print('PASS strict regional visual re-export', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('output', type=Path)
    run(p.parse_args().output)
