"""Copy a JDK and use existing Windows VC runtimes locally; no install or PATH edit."""
import argparse
import json
from pathlib import Path
import runpy
import shutil

h = runpy.run_path(str(Path(__file__).with_name('inspect-backend-feasibility.py')))
NAMES = ('msvcp140.dll', 'msvcp140_1.dll', 'vcruntime140.dll', 'vcruntime140_1.dll')


def prepare(source, output):
    source, output = source.resolve(), output.resolve()
    h['require'](not output.exists(), 'Use a NEW isolated directory')
    h['require'](not output.is_relative_to(source), 'Do not copy a JDK inside itself')
    original = h['files'](source)
    size = sum(p.stat().st_size for p in source.rglob('*') if p.is_file())
    h['require'](shutil.disk_usage(output.parent).free >= size + 2*1024**3,
                 'Need copy size plus 2 GiB launch reserve')
    system = Path('C:/Windows/System32')
    # Ordinary copies, never writable hardlinks to the installed JDK or Windows.
    shutil.copytree(source, output)
    for name in NAMES:
        shutil.copy2(system/name, output/'bin'/name)
    actual = h['files'](output)
    allowed = {'bin/'+n for n in NAMES}
    h['require']({k:v for k,v in original.items() if k not in allowed} ==
                 {k:v for k,v in actual.items() if k not in allowed}, 'Other JDK files changed')
    h['require'](h['files'](source) == original, 'Installed JDK changed')
    record = {'source_manifest_sha256':h['digest'](original),
              'isolated_manifest_sha256':h['digest'](actual), 'copy_bytes':size,
              'installed_jdk_unchanged':True,
              'runtime_sha256':{n:h['sha'](system/n) for n in NAMES},
              'original_runtime_sha256':{n:original.get('bin/'+n) for n in NAMES}}
    output.with_suffix('.json').write_text(json.dumps(record, indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    prepare(a.source, a.output)
