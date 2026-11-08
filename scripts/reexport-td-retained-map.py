"""Strict original-source retained chain plus retained-map-1, offline only."""
import argparse
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def run(output):
    runpy.run_path(str(ROOT/'scripts/reexport-td-story.py'))['run'](output)
    runpy.run_path(str(ROOT/'scripts/build-td-retained-map.py'))['export'](strict=True)
    (output/'retained-map-strict-reexport.txt').write_text('PASS retained and new evidence; no TD execution\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);run(p.parse_args().output)
