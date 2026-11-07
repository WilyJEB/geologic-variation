"""One frozen offline comparison. Standard library only; no terrain runtime."""
import hashlib
import json
import math
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STEM = ROOT / 'docs/evidence/td-region-visual'
INPUT_SHA = '8dc1e0a9f98edd1dc6b2ce74cc1d795c117c15feb9503b0260a5c5ef23a701d6'
DOMAIN = 'region-visual-1|8675309|'
SIDE = 2048


def sha(b):
    return hashlib.sha256(b).hexdigest()


def encoded(d):
    return (json.dumps(d, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def digest(s):
    return hashlib.sha256((DOMAIN+s).encode()).hexdigest()


def phases():
    return tuple(int(digest('phase-'+axis)[:8], 16) % SIDE for axis in ('x', 'z'))


def history(i, j):
    d = digest(f'history|{i}|{j}')
    return dict(id=[i, j], token=d, inherited='H'+str(int(d[:2], 16) % 2),
                overprint='O'+str(int(d[2:4], 16) % 2))


def region(x, z, displacement=0):
    px, pz = phases()
    return (math.floor((x-displacement-px)/SIDE), math.floor((z-pz)/SIDE))


def neighborhood(i, j):
    return [(i+dx, j+dz) for dz in (-1, 0, 1) for dx in (-1, 0, 1)]


def load(raw):
    assert sha(raw) == INPUT_SHA, 'Immutable PR57 input hash mismatch'
    d = json.loads(raw)
    assert d['seed'] == 8675309 and d['query_bounds_half_open'] == [10880, 2688, 13953, 5761]
    h = d['elevations']
    assert len(h) == 49 and all(len(row) == 49 for row in h)
    assert all(math.isfinite(v) for row in h for v in row)
    assert d['spacing_native'] == 64 and d['retained_point_values'] == 2401
    return d


def warp(z, rows, z0=10880):
    q = (z-z0)/64
    if q < 0 or q > 48:
        return 0
    r = min(47, math.floor(q))
    return rows[r]['displacement']*(1-(q-r))+rows[r+1]['displacement']*(q-r)


def topology(grid):
    seen = set()
    parts = {}
    counts = {}
    transitions = 0
    for r in range(49):
        for c in range(49):
            key = ','.join(map(str, grid[r][c]))
            counts[key] = counts.get(key, 0)+1
            transitions += sum(grid[r][c] != grid[rr][cc] for rr, cc in
                               ((r+1, c), (r, c+1)) if rr < 49 and cc < 49)
            if (r, c) in seen:
                continue
            parts[key] = parts.get(key, 0)+1
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                rr, cc = stack.pop()
                for nr, nc in ((rr-1, cc), (rr+1, cc), (rr, cc-1), (rr, cc+1)):
                    if 0 <= nr < 49 and 0 <= nc < 49 and (nr, nc) not in seen and grid[nr][nc] == grid[r][c]:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
    return dict(site_counts=counts, sample_components=parts, adjacent_id_transitions=transitions)


def evaluate(raw):
    d = load(raw)
    h = d['elevations']
    rows = []
    for r, values in enumerate(h):
        weights = [v-min(values) for v in values]
        total = sum(weights)
        centroid = sum((2688+c*64)*w for c, w in enumerate(weights))/total if total else None
        displacement = max(-256, min(256, (centroid-4224)/2))*min(r, 48-r, 4)/4 if total else 0
        rows.append(dict(z=10880+r*64, centroid_x=centroid,
                         displacement=displacement, descriptive_abstention=not bool(total)))
    grids = []
    for terrain in (False, True):
        grids.append([[list(region(2688+c*64, 10880+r*64, rows[r]['displacement'] if terrain else 0))
                       for c in range(49)] for r in range(49)])
    ids = sorted({tuple(cell) for grid in grids for row in grid for cell in row})
    histories = [history(*cell) for cell in ids]
    difference = [[None]*49 for _ in range(49)]
    for r in range(1, 48):
        for c in range(1, 48):
            difference[r][c] = max(abs(h[r][c]-h[nr][nc]) for nr, nc in
                                   ((r-1, c), (r+1, c), (r, c-1), (r, c+1)))
    assert difference == d['max_four_neighbor_difference_metres']
    return dict(contract='region-visual-1', input_sha256=sha(raw), seed=d['seed'],
                phases=list(phases()), side=SIDE, query_bounds_half_open=d['query_bounds_half_open'],
                retained_points=2401, missing_query_values=9443329-2401,
                observation_error=None, confirmed_geometry=False, geological_interpretation='abstain everywhere',
                stencil_missing_sites=192, rows=rows, histories=histories,
                seed_only_ids=grids[0], terrain_illustration_ids=grids[1],
                topology=[topology(g) for g in grids],
                changed_sites=sum(a != b for ra, rb in zip(*grids) for a, b in zip(ra, rb)),
                max_abs_displacement=max(abs(row['displacement']) for row in rows),
                support=dict(warp_max_rows=2, warp_max_heights=98, difference_max_heights=5,
                             regional_neighborhood_ids=9, point_arrays=2, sites_per_array=2401),
                computed_descriptors=dict(elevations=h, max_four_neighbor_difference_metres=difference),
                authored=['lattice scale and phases', 'history labels', 'centroid contact gain/cap/taper',
                          'piecewise-linear contact geometry', 'colour key'],
                production_selector=False, gameplay_acceptance=False)


def viewer(result):
    # Fully embedded data, no network, no JS classification or hidden recomputation.
    template = (ROOT/'scripts/td-region-viewer.html').read_text(encoding='utf-8')
    return template.replace('__RESULT__', json.dumps(result, sort_keys=True, allow_nan=False)).encode()


def export():
    with zipfile.ZipFile(ROOT/'docs/evidence/td-pressure-visual.zip') as old:
        raw = old.read('visual-data.json')
    result = evaluate(raw)
    members = {'input/visual-data.json': raw, 'result.json': encoded(result), 'viewer.html': viewer(result)}
    for name in ('scripts/build-td-region-visual.py', 'scripts/td-region-viewer.html',
                 'scripts/test-td-region-visual.py', 'scripts/reexport-td-region-visual.py',
                 'scripts/render-td-region-visual.py', 'scripts/test-td-region-viewer.cjs',
                 'docs/td-region-visual-protocol.md'):
        members['sources/'+name] = (ROOT/name).read_bytes()
    for name in ('td-region-visual.png', 'td-region-visual-image.json'):
        members['visual/'+name] = (ROOT/'docs/evidence'/name).read_bytes()
    image = json.loads(members['visual/td-region-visual-image.json'])
    assert image['png_sha256'] == sha(members['visual/td-region-visual.png'])
    assert image['result_sha256'] == sha(members['result.json'])
    assert image['renderer_sha256'] == sha(members['sources/scripts/render-td-region-visual.py'])
    # Include only the pinned API evidence used here, not another terrain field.
    with zipfile.ZipFile(ROOT/'docs/evidence/td-window-history.zip') as old:
        for name in ('pinned-provider-javap.txt', 'upstream-source/pipeline/LocalTerrainProvider.java',
                     'upstream-source/pipeline/WorldPipeline.java'):
            members['api/'+name] = old.read(name)
    with zipfile.ZipFile(STEM.with_suffix('.zip'), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    STEM.with_suffix('.html').write_bytes(members['viewer.html'])
    summary = dict(archive_sha256=sha(STEM.with_suffix('.zip').read_bytes()),
                   members={n: sha(b) for n, b in sorted(members.items())},
                   result={k: result[k] for k in ('changed_sites', 'topology', 'max_abs_displacement',
                                                'missing_query_values', 'observation_error', 'support')})
    STEM.with_suffix('.json').write_bytes(encoded(summary))
    return summary


if __name__ == '__main__':
    print(json.dumps(export(), indent=2))
