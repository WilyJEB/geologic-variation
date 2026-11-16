"""Record one explicit non-client --check-only invocation; never retries."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import time

ROOT = Path(__file__).resolve().parents[1]


def snapshot():
    result = {}
    for name in ('td-navigation-1', 'td-navigation-2'):
        root = ROOT/'runs/acceptance'/name
        result[name] = dict(directories=sorted(p.name for p in root.glob('attempt-*') if p.is_dir()),
                           ledger_sha256=hashlib.sha256((root/'ledger.json').read_bytes()).hexdigest())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('context', choices=('restricted', 'approved'))
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    assert not args.output.exists(), 'Never overwrite an observation'
    launcher = ROOT/'scripts/launch-retained-navigation-supplement.py'
    before = snapshot()
    stream = io.StringIO()
    start = time.monotonic()
    error = None
    try:
        with contextlib.redirect_stdout(stream):
            runpy.run_path(str(launcher))['main'](check=True)
    except Exception as exception:
        error = type(exception).__name__+': '+str(exception)
    after = snapshot()
    record = dict(context=args.context, mode='check-only', client_launched=False,
                  launcher_sha256=hashlib.sha256(launcher.read_bytes()).hexdigest(),
                  elapsed=time.monotonic()-start, stdout=stream.getvalue(), error=error,
                  before=before, after=after, allocation_unchanged=before == after)
    args.output.write_bytes((json.dumps(record, indent=2, sort_keys=True)+'\n').encode())
    print(json.dumps(record, indent=2))
    assert before == after


if __name__ == '__main__':
    main()
