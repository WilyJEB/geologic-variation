"""Portable partial navigation-2 evidence. Never launches Minecraft or TD."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import runpy
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'runs/acceptance/td-navigation-2'
STEM = ROOT / 'docs/evidence/td-navigation-supplement'
BASE = runpy.run_path(str(ROOT / 'scripts/export-retained-client.py'))
FORBIDDEN = ('terraindiffusion', 'terrain_diffusion', 'terrain-diffusion',
             'onnxruntime', 'ai.onnx', 'ai/onnx', 'dev.wilyjeb.geology.domain.',
             'dev/wilyjeb/geology/domain/', 'dev.wilyjeb.geology.world.',
             'dev/wilyjeb/geology/world/', 'geologic_variation')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scan(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            assert not any(s in n.lower() for s in FORBIDDEN), n
            if n.endswith('.jar'):
                scan(z.read(n))


def audit(m):
    ledger = json.loads(m['raw/ledger.json'])
    assert len(ledger) == 1
    row = ledger[0]
    assert row['attempt'] == 1 and row['status'] == 'exit-1'
    assert row['automatic_route_check'] == 'FAILED' and row['pid_absent']
    assert 0 < row['elapsed'] <= 1200
    cleanup = json.loads(m['raw/pid-cleanup.json'])
    assert cleanup['checked_pids'] == [2788, 28560]
    assert cleanup['absent'] and not cleanup['present']
    pre = 'raw/attempt-01/'
    console = m[pre+'console.log'].decode(errors='replace')
    loaded = m[pre+'class-load.log'].decode(errors='replace').lower()
    assert not any(s in loaded for s in FORBIDDEN)
    debug = m[pre+'logs/debug.log'].decode(errors='replace')
    for guard in ('SaveBarrier', 'WorldBarrier', 'TitleOnly', 'Hud', 'LanBarrier', 'Keys'):
        assert 'Mixing '+guard+' from retained-navigation.mixins.json' in debug
    for token in ('guard rejected ../continuing', 'guard rejected other-world',
                  'guard fresh save ', 'guard fresh integrated server',
                  'guard local attachment', 'route 0'):
        assert 'RETAINED_NAV '+token in console
    assert 'RETAINED_NAV route 1' not in console
    assert 'Stopping server' not in console
    inv = json.loads(m[pre+'inventory.json'])
    assert all(n.startswith('saves/navigation-only/') for n in inv if n.startswith('saves/'))
    assert 'saves/navigation-only/level.dat' in inv
    assert [n for n in inv if n.startswith('mods/')] == ['mods/retained-navigation-1.jar']
    for n, info in inv.items():
        if pre+n in m:
            assert sha(m[pre+n]) == info['sha256'], n
    frozen = json.loads(m['docs/td-navigation-supplement-hashes.json'])
    for n, h in frozen['reused'].items():
        if n.startswith('src/runtimeProbe/') or (n.startswith('diagnostics/') and n.endswith('.java')):
            h = frozen['planned_changed'].get(n, h)
            assert sha(m[pre+'executed/'+Path(n).name]) == h, n
    # Descriptor/mixin settings aren't Java executed copies; verify current bytes
    # separately below. The exact JAR retains their actual runtime forms.
    with zipfile.ZipFile(io.BytesIO(m[pre+'executed/retained-navigation-1.jar'])) as jar:
        assert sha(jar.read('retained-map.tsv')) == frozen['reused']['src/runtimeProbe/resources/retained-map.tsv']
        assert 'dev/wilyjeb/retainedclient/mixin/Keys.class' in jar.namelist()
    scan(m[pre+'executed/retained-navigation-1.jar'])
    scan(m['raw/final-compile-only.jar'])
    positions = []
    pattern = r'RETAINED_NAV position (\S+) (\S+) scale (\d+) block (-?\d+) (-?\d+) chunk (-?\d+) (-?\d+) support (\w+)'
    for match in re.finditer(pattern, console):
        x, z = map(float, match.group(1, 2))
        scale, bx, bz, cx, cz = map(int, match.group(3, 4, 5, 6, 7))
        assert math.isfinite(x) and math.isfinite(z) and scale == 1
        assert (bx, bz) == (math.floor(x), math.floor(z))
        assert (cx, cz) == (bx//16, bz//16)
        positions.append((x, z))
    start = (2944.5, 13824.5)
    assert start in positions
    movement = positions[positions.index(start):]
    end = movement[-1]
    distance = math.dist(start, end)
    assert 16 <= distance <= 32
    assert len(set(movement)) > 2
    assert end == (2922.054713, 13824.447234)
    samples = [json.loads(s) for s in m[pre+'monitor.jsonl'].decode().splitlines()]
    assert samples and samples[-1]['elapsed'] <= row['elapsed'] < 180
    for s in samples:
        assert s['elapsed'] <= 1200 and s['working_set'] <= 6*1024**3
        assert s['output_bytes'] <= 2*1024**3 and s['free'] >= 4*1024**3
    for n in ('title.jpg', 'entry.jpg', 'scale1-before.jpg'):
        assert m[pre+n].startswith(b'\xff\xd8\xff')
    assert pre+'scale1-after-human.jpg' not in m
    post = json.loads(m['raw/post-checks.json'])
    assert len(post['dependencies']) == 129 and all(post['dependencies'].values())
    assert all(post['retained_inputs'].values())
    actions = json.loads(m['actions.json'])
    assert actions['acceptance'] == 'INCOMPLETE' and actions['attempts_remaining'] == 1
    source = 'diagnostics/retained-navigation/src/main/java/dev/wilyjeb/retainedclient/Navigation.java'
    assert sha(m[source]) == frozen['attempt_2_planned_changed'][source]
    assert b'pos[0]+".0 100.0 "+pos[1]+".0 0 0"' in m[source]
    return dict(contract='navigation-2', acceptance='INCOMPLETE', attempts_used=1,
                attempts_remaining=1, charged_seconds=row['elapsed'],
                human_movement_log_displacement=distance, start=list(start), end=list(end),
                log_coordinate_checks=True, visual_marker_coherence=False,
                graceful_server_shutdown=False, exact_pid_cleanup=True,
                decimal_setup_correction='compile-only', td_executed=False,
                maximum_sampled_working_set=max(s['working_set'] for s in samples))


def collect():
    m = {}
    for p in sorted(RAW.rglob('*')):
        if p.is_file() and 'natives' not in p.relative_to(RAW).parts:
            m['raw/'+p.relative_to(RAW).as_posix()] = p.read_bytes()
    for p in sorted((ROOT/'diagnostics/retained-navigation/src').rglob('*')):
        if p.is_file():
            m[p.relative_to(ROOT).as_posix()] = p.read_bytes()
    for n in ('docs/td-navigation-supplement.md', 'docs/td-navigation-supplement-hashes.json',
              'scripts/launch-retained-navigation-supplement.py',
              'scripts/export-navigation-supplement.py', 'scripts/test-navigation-supplement.py'):
        m[n] = (ROOT/n).read_bytes()
    m['actions.json'] = (ROOT/'docs/evidence/td-navigation-supplement-actions.json').read_bytes()
    return m


def export(strict=False):
    m = collect()
    result = audit(m)
    data = BASE['encode'](m)
    result.update(archive_sha256=sha(data), members={n:sha(b) for n,b in sorted(m.items())})
    for suffix, b in (('.zip', data), ('.json', (json.dumps(result,indent=2,sort_keys=True)+'\n').encode())):
        p = STEM.with_suffix(suffix)
        if strict:
            assert p.read_bytes() == b, p
        else:
            p.write_bytes(b)
    print('PASS portable partial navigation-2 evidence'+(' strict' if strict else ''))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--strict', action='store_true')
    export(p.parse_args().strict)
