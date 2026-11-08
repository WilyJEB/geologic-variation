"""Strict old/new retained evidence after final Windows checkout. No client or TD."""
import argparse
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def run(output):
    runpy.run_path(str(ROOT/'scripts/reexport-td-retained-map.py'))['run'](output)
    runpy.run_path(str(ROOT/'scripts/export-retained-client.py'))['export'](strict=True)
    (output/'client-map-strict.txt').write_text('PASS original retained chain and actual-client evidence; no launch\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);run(p.parse_args().output)
