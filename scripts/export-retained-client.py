"""Portable exact client-map-1 evidence. Replays records/logs, never launches Java."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import runpy
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'runs/acceptance/td-client-map-1'
STEM = ROOT/'docs/evidence/td-client-map'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def audit(m):
    ledger = json.loads(m['raw/ledger.json'])
    assert len(ledger) == 3 and all(v['status'] == 'exit-0' for v in ledger)
    assert all(0 < v['elapsed'] < 900 for v in ledger)
    assert sum(v['elapsed'] for v in ledger) < 2700
    forbidden = ('terrain_diffusion', 'terraindiffusion', 'terrain-diffusion', 'onnxruntime', 'ai.onnx',
                 'dev.wilyjeb.geology.domain.', 'dev.wilyjeb.geology.world.')
    resource = m['raw/attempt-02/executed/retained-map.tsv']
    assert sha(resource) == 'ab7168c07af32e981601d2e2fecb7a8457ec3607e68e2dec0731a6c86a67b872'
    original = json.loads(m['input/td-retained-map.json'])
    assert sha(m['input/td-retained-map.zip']) == original['archive_sha256']
    for filename in ('RetainedMap.java', 'RetainedMapScreen.java'):
        key = 'src/runtimeProbe/java/dev/wilyjeb/geology/probe/'+filename
        assert sha(m['raw/attempt-02/executed/'+filename]) == original['members'][key]
    max_working = 0
    outcomes = []
    for i in range(1,4):
        prefix = f'raw/attempt-{i:02}/'
        loaded = m[prefix+'class-load.log'].decode(errors='replace').lower()
        assert not any(v in loaded for v in forbidden), 'Forbidden loaded class'
        inv = json.loads(m[prefix+'inventory.json'])
        assert not any(n.startswith('saves/') or n.endswith(('.mca', 'level.dat', 'session.lock')) for n in inv)
        assert [n for n in inv if n.startswith('mods/')] == ['mods/retained-client-1.jar']
        console = m[prefix+'console.log'].decode(errors='replace')
        if i == 1:
            assert 'IllegalClassLoadError' in console and 'RETAINED_CLIENT enter panel' not in console
            outcomes.append('failed: reserved mixin package collision (exit code was zero)')
        else:
            assert 'RETAINED_CLIENT enter panel' in console and 'FATAL' not in console
            debug = m[prefix+'logs/debug.log'].decode(errors='replace')
            for mixin in ('WorldBarrier', 'SaveBarrier', 'TitleOnly'):
                assert 'Mixing '+mixin+' from retained-client.mixins.json' in debug
            assert m[prefix+'executed/retained-map.tsv'] == resource
            for filename in ('RetainedMap.java', 'RetainedMapScreen.java'):
                assert m[prefix+'executed/'+filename] == m['raw/attempt-02/executed/'+filename]
            for shot in ('title.png', 'entry-scale1.png', 'exposure-scale1.png',
                         'exposure-scale6.png', 'pr58-same-exposure-scale6.png', 'gap.png', 'escape-title.png'):
                # Computer Use returns JPEG bytes; original capture filenames
                # used .png. Preserve bytes/raw names; public copies use .jpg.
                assert m[prefix+shot].startswith((b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff'))
            outcomes.append('completed: actual panel inspected and quit')
        samples = [json.loads(s) for s in m[prefix+'monitor.jsonl'].decode().splitlines()]
        assert samples
        for s in samples:
            assert s['elapsed'] <= 900 and s['working_set'] <= 6*1024**3
            assert s['output_bytes'] <= 2*1024**3 and s['free'] >= 4*1024**3
            max_working = max(max_working,s['working_set'])
        with zipfile.ZipFile(io.BytesIO(m[prefix+'executed/retained-client-1.jar'])) as jar:
            assert jar.read('retained-map.tsv') == resource
            assert b'retained_client' in jar.read('META-INF/neoforge.mods.toml')
            assert not any(any(v.replace('.', '/') in n.lower() for v in forbidden) for n in jar.namelist())
        cmd = json.loads(m[prefix+'command.json'])
        assert '-Xmx2g' in cmd and not any('quickPlay' in v for v in cmd)
    actions = json.loads(m['actions.json'])
    assert actions['source'] == 'actual Minecraft window screenshots and UI actions'
    return dict(contract='client-map-1', attempts=3, outcomes=outcomes,
                elapsed_seconds=sum(v['elapsed'] for v in ledger), maximum_sampled_working_set=max_working,
                immutable_display_sources=True, td_executed=False, save_files=0,
                world_created=False, runtime_mixin_application_confirmed=True,
                actual_client_configurations=[[1600,1000,2],[1200,900,1]],
                computed_checks='retained records/logs/hashes only; no new terrain data',
                judgment='legible diagnostic; small text; no geological/gameplay acceptance')


def collect():
    m = {}
    for p in sorted(RAW.rglob('*')):
        if p.is_file() and 'natives' not in p.relative_to(RAW).parts:
            m['raw/'+p.relative_to(RAW).as_posix()] = p.read_bytes()
    for p in sorted((ROOT/'diagnostics/retained-client').rglob('*')):
        if p.is_file() and not any(v in p.parts for v in ('build','.gradle')):
            m[p.relative_to(ROOT).as_posix()] = p.read_bytes()
    for name in ('scripts/launch-retained-client.py','scripts/export-retained-client.py',
                 'scripts/test-retained-client.py','scripts/reexport-retained-client.py',
                 'docs/td-client-map-protocol.md'):
        m[name] = (ROOT/name).read_bytes()
    for suffix in ('.json','.zip'):
        m['input/td-retained-map'+suffix] = (ROOT/('docs/evidence/td-retained-map'+suffix)).read_bytes()
    m['actions.json'] = (ROOT/'docs/evidence/td-client-map-actions.json').read_bytes()
    return m


def encode(m):
    out = io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(m.items()):
            info=zipfile.ZipInfo(n,(2026,11,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,b)
    return out.getvalue()


def export(strict=False):
    m = collect()
    result = audit(m)
    data = encode(m)
    result.update(archive_sha256=sha(data),members={n:sha(b) for n,b in sorted(m.items())})
    summary = (json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    for suffix,b in (('.zip',data),('.json',summary)):
        p = STEM.with_suffix(suffix)
        if strict:
            assert p.read_bytes() == b, p
        else:
            p.write_bytes(b)
    for name, raw in (('exposure','attempt-02/exposure-scale6.png'),
                      ('pr58','attempt-02/pr58-same-exposure-scale6.png'),
                      ('small','attempt-03/exposure-scale6.png'),
                      ('gap','attempt-02/gap.png')):
        p=ROOT/('docs/evidence/td-client-map-'+name+'.jpg')
        b=m['raw/'+raw]
        if strict: assert p.read_bytes()==b,p
        else:p.write_bytes(b)
    print('PASS client-map strict replay' if strict else 'PASS client-map portable export')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--strict',action='store_true');export(p.parse_args().strict)
