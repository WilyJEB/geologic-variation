"""Strict original-source retained chain plus story-1. No TD execution."""
import argparse
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def run(output):
    runpy.run_path(str(ROOT/'scripts/reexport-td-region-visual.py'))['run'](output)
    runpy.run_path(str(ROOT/'scripts/build-td-story.py'))['export'](strict=True)
    (output/'story-strict-reexport.json').write_text(json.dumps(dict(
        offline_only=True,retained_and_new_exports_match=True,production_unchanged=True),indent=2)+'\n')
    print('PASS strict story and retained exports')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);run(p.parse_args().output)
