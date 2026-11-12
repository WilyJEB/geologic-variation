"""Offline preparation packaging, never installed preflight, Java or allocation.

--freeze is preparation authoring only; changing a pushed freeze invalidates
any later execution approval. Default strictly reproduces existing bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def package(freeze=False):
    require=lambda ok: None if ok else (_ for _ in ()).throw(ValueError('navigation-3 root must remain absent'))
    require(not (ROOT/'runs/acceptance/td-navigation-3').exists())
    files = ['scripts/'+n for n in ('launch-navigation-3.py','navigation-process.py',
             'replay-navigation-3.py','test-navigation-3.py','package-navigation-3.py','record-navigation-3.py',
             'launch-retained-navigation-supplement.py','launch-acceptance-client.py')]
    files += ['docs/'+n for n in ('td-navigation-3-protocol.md','td-navigation-3-schema.json','td-navigation-3-installed-inputs.json',
              'td-navigation-protocol.md','td-navigation-supplement.md','td-navigation-supplement-hashes.json',
              'td-region-viewer.html')]
    files += ['scripts/build-td-region-preview.py', 'src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMap.java',
              'src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMapScreen.java',
              'src/runtimeProbe/resources/retained-map.tsv']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'diagnostics/retained-navigation').rglob('*')
              if p.is_file() and ('src' in p.relative_to(ROOT/'diagnostics/retained-navigation').parts
                                  or p.name in ('build.gradle','settings.gradle'))]
    files += ['docs/evidence/'+n for n in ('td-navigation.zip','td-navigation-supplement.zip',
              'td-navigation-readiness.zip','td-retained-map.zip','td-story.zip')]
    data={n:(ROOT/n).read_bytes() for n in sorted(set(files))}
    with zipfile.ZipFile(ROOT/'docs/evidence/td-navigation-supplement.zip') as z:
        jar=z.read('raw/final-compile-only.jar')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    record=dict(contract='navigation-3',base='c91c76b8ebad7d03ae8852102b33bd06d62cea0a',
                execution_authorized=False,runtime_root_created=False,
                artifact_origin='td-navigation-supplement.zip:raw/final-compile-only.jar',
                artifact_sha256=sha(jar),files={n:sha(b) for n,b in data.items()},
                configurations=[[1600,1000,2],[1200,900,1]],
                route=[[2944,13824],[2688,10880],[5760,10880],[2720,10912],
                       [5760,13952],[5761,13953],[17664,82944]],
                heap='2GiB',attempts_including_failure=1,seed=8675309,
                startup_seconds=180,wall_seconds=1200,td_requests=0,model_calls=0,
                provider_initializations=0,windows=0)
    manifest=(json.dumps(record,indent=2,sort_keys=True)+'\n').encode()
    target=ROOT/'docs/td-navigation-3-hashes.json'
    if freeze:
        target.write_bytes(manifest)
    else:
        assert target.read_bytes()==manifest,'Frozen manifest differs'
    data['docs/td-navigation-3-hashes.json']=manifest
    data['artifact/retained-navigation-1.jar']=jar
    encoded=runpy.run_path(str(ROOT/'scripts/export-retained-client.py'))['encode'](data)
    target=ROOT/'docs/evidence/td-navigation-3-preparation.zip'
    if freeze:
        target.write_bytes(encoded)
    else:
        assert target.read_bytes()==encoded,'Strict preparation archive differs'
    print(json.dumps(dict(preparation=True,strict=not freeze,manifest_sha256=sha(manifest),
                          artifact_sha256=sha(jar),archive_sha256=sha(encoded)),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true')
    package(parser.parse_args().freeze)
