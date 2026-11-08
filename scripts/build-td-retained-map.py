"""Copy retained records into a bounded probe-only display resource. No TD."""
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT/'src/runtimeProbe/resources/retained-map.tsv'
HASHES = {
    'input/visual-data.json': '8dc1e0a9f98edd1dc6b2ce74cc1d795c117c15feb9503b0260a5c5ef23a701d6',
    'input/pr58-result.json': 'd0853fba10ca350e353d9a2786a6362d99f80363aa7b12a071d470b89e56819c',
    'result.json': '9caff8648cb2165bf0d0ed7c3e9fd70ce6759d28b0c891b9fd36de1551fac650'}
sha = lambda b: hashlib.sha256(b).hexdigest()


def records():
    raw = (ROOT/'docs/evidence/td-story.zip').read_bytes()
    assert sha(raw) == 'fec51d36faeb1d8b99e7624c2daab5cbd2b614227c6df9527dfe0f7c7954da47'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members = {n: z.read(n) for n in HASHES}
    assert all(sha(members[n]) == h for n, h in HASHES.items())
    return tuple(json.loads(members[n]) for n in HASHES)


def resource():
    obs, base, story = records()
    lines = ['# retained-map-1; native coordinates; unknown gaps; no world association']
    for mode, result in enumerate((base, story)):
        for h in result['histories']:
            key = str(h['id']) if mode else ','.join(map(str, h['id']))
            if mode:
                assert h['surface_history'] == h['deep_history'] == h['token']
                seed = 'substrate '+h['substrate']
                measured = f"contrast {h['mean_contrast_metres']:.3f} m; {h['observed_sites']} sites"
                authored = h['authored_event']
            else:
                seed = h['inherited']+' / '+h['overprint']
                measured = 'row sample centroids bend contacts; no history inference'
                authored = 'surface overprint '+h['overprint']+' over deep '+h['inherited']
            lines.append('\t'.join(('H', str(mode), key, h['token'], seed, measured, authored)))
    for r in range(49):
        for c in range(49):
            lines.append('\t'.join(map(str, ('P', 2688+64*c, 10880+64*r,
                obs['elevations'][r][c], ','.join(map(str, base['terrain_illustration_ids'][r][c])), story['ids'][r][c][0]))))
    # Exact PR58 row polyline contacts, including its unchanged horizontal seam.
    for i in range(-1, 5):
        for a, b in zip(base['rows'], base['rows'][1:]):
            lines.append('\t'.join(map(str, ('L', 0, base['phases'][0]+2048*i+a['displacement'], a['z'],
                base['phases'][0]+2048*i+b['displacement'], b['z']))))
    for j in range(3, 9):
        z = base['phases'][1]+2048*j
        lines.append(f'L\t0\t2688\t{z}\t5761\t{z}')
    for i in range(-3, 1):
        lines.append(f"L\t1\t{story['phase']+2048*i-story['a']*10880}\t10880\t{story['phase']+2048*i-story['a']*13953}\t13953")
    return ('\n'.join(lines)+'\n').encode()


def export(strict=False):
    data = resource()
    assert len(data) < 2*1024*1024
    if strict:
        assert RESOURCE.read_bytes() == data
    else:
        RESOURCE.write_bytes(data)
    sources = ['scripts/build-td-retained-map.py', 'scripts/test-td-retained-map.py',
        'docs/td-retained-map-protocol.md',
        'src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMap.java',
        'src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMapScreen.java',
        'src/runtimeProbe/java/dev/wilyjeb/geology/probe/mixin/RetainedMapTitleMixin.java',
        'src/runtimeProbe/resources/geology-runtime-probe.mixins.json',
        'build.gradle', 'scripts/reexport-td-retained-map.py']
    members = {n: (ROOT/n).read_bytes() for n in sources}
    members['retained-map.tsv'] = data
    members['input/td-story.zip'] = (ROOT/'docs/evidence/td-story.zip').read_bytes()
    for p in sorted((ROOT/'docs/evidence').glob('td-retained-map-*.png')):
        members['display/'+p.name] = p.read_bytes()
    members['display/verification.json'] = (ROOT/'docs/evidence/td-retained-map-verification.json').read_bytes()
    executed=(ROOT/'docs/evidence/td-retained-map-desktop-source.java').read_bytes()
    assert sha(executed)=='fabe0ae27789279570b8b3b5d52dffc401da188ad0b019cf64f01db142da43e6'
    members['display/executed-RetainedMap.java']=executed
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for n, b in sorted(members.items()):
            info = zipfile.ZipInfo(n, (2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, b)
    outputs = {'.zip': out.getvalue(), '.json': (json.dumps(dict(
        contract='retained-map-1', resource_sha256=sha(data), archive_sha256=sha(out.getvalue()),
        members={n: sha(b) for n, b in sorted(members.items())},
        sites=2401, history_cards=7, segments=298, minecraft_client_verified=False,
        td_executed=False), sort_keys=True, indent=2)+'\n').encode()}
    for ext, b in outputs.items():
        p = ROOT/('docs/evidence/td-retained-map'+ext)
        if strict:
            assert p.read_bytes() == b, str(p)
        else:
            p.write_bytes(b)
    print('PASS retained map '+('strict replay' if strict else 'export'))


if __name__ == '__main__':
    import sys
    export('--strict' in sys.argv)
