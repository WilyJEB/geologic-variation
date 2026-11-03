"""NEW multi-seed coarse/fine diagnostic fixtures; never changes worldgen.

Strata select contrasting inputs, not geological truth or calibrated thresholds.
No p5, lithology assignment, benchmark or production classifier is introduced.
"""
import argparse
import gzip
import json
from pathlib import Path
import re
import runpy
import shutil
import time
import zipfile

base = runpy.run_path(str(Path(__file__).with_name('verify-coarse-prototype.py')))
live = base['live']; h = base['h']; r = base['r']; require = base['require']


def tendency(evidence):
    values = evidence['elevations']
    require(len(values) == 9 and not evidence['p5_used'], 'Invalid evidence')
    # Zero is the physical elevation datum, not a fitted relief threshold.
    if max(values) < 0: return 'ocean'
    if min(values) < 0: return 'coast'
    return 'land'


def select(scan):
    groups = {key: [] for key in ('ocean', 'coast', 'land')}
    for row in scan: groups[tendency(row['evidence'])].append(row)
    require(all(groups.values()), 'Survey lacks a required terrain stratum')
    land = sorted(groups['land'], key=lambda v: v['evidence']['mean_metres'])
    # Lower/upper land extremes are sampling strata, not validated biome labels.
    return {'ocean': min(groups['ocean'], key=lambda v:v['evidence']['mean_metres']),
            'coast': min(groups['coast'], key=lambda v:abs(v['evidence']['mean_metres'])),
            'lowland': land[0], 'mountain': land[-1]}


def run(args):
    require(r['sha'](args.td) == '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8', 'CPU pin')
    args.output.mkdir(parents=True, exist_ok=False)
    models = base['manifest'](args.models); template = base['manifest'](args.template)
    with zipfile.ZipFile(args.baseline) as old, zipfile.ZipFile(args.addon) as new:
        require(old.namelist() == new.namelist() and all(old.read(n) == new.read(n) for n in old.namelist()),
                'Production artifact differs from main')
    result = {'main_commit':'d6d59cae4e46dd7a09ff6c27f77645cfb03a736b',
              'production_sha256':r['sha'](args.addon), 'baseline_sha256':r['sha'](args.baseline),
              'probe_sha256':r['sha'](args.probe), 'sources':{}, 'models':models, 'cases':[]}
    for name in ('verify-terrain-diagnostics.py','verify-coarse-prototype.py','verify-live-context.py',
                 'verify-context-startup.py','runtime-acceptance.py','compare-runtime-chunks.py'):
        result['sources'][name] = r['sha'](Path(__file__).with_name(name))
    for seed in (-1550453200536840819, 8675309):
        for scale in (1, 6):
            require(shutil.disk_usage(args.output).free > 2*1024**3, 'Need 2 GiB free')
            server = r['Server'](args, f'seed{seed}-s{scale}', scale=scale, link_td=True)
            world = server.path/'world'
            # Only NEW metadata without terrain: establish a seed before first launch.
            path = world/'level.dat'; tag = r['nbt_read'](gzip.decompress(path.read_bytes()))
            tag[2]['Data'][1]['WorldGenSettings'][1]['seed'] = (4, seed)
            path.write_bytes(gzip.compress(r['nbt_write'](tag), mtime=0))
            path = world/h['SNAPSHOT']
            path.write_text(re.sub(r'^seed=-?\d+$', f'seed={seed}', path.read_text(), flags=re.M))
            case = {'name':server.path.name, 'seed':seed, 'scale':scale, 'scan':[], 'comparisons':[]}
            try:
                start = time.monotonic(); server.start(); case['startup_seconds'] = time.monotonic()-start
                case['settings'] = server.command('acceptance settings')
                require('CPU/' in case['settings']['context'] and f'seed={seed}' in case['settings']['context'], 'Context mismatch')
                # Fixed signed global lattice: 81 3x3 neighborhoods, not an unbounded search.
                for row in range(-64, 65, 16):
                    for col in range(-64, 65, 16):
                        x, z = col*256*scale, row*256*scale
                        case['scan'].append({'x':x,'z':z,'evidence':server.command(f'acceptance coarse {x} {z}')})
                case['selected'] = select(case['scan'])
                for label, point in case['selected'].items():
                    comparison = server.command(f"acceptance terrain-compare {point['x']} {point['z']}")
                    comparison['stratum'] = label
                    case['comparisons'].append(comparison)
                # Both sides of real province boundary, plus coarse and negative-axis boundaries.
                plan = r['targets'](seed, scale)
                case['boundary_plan'] = plan
                points = [(-256*scale-1, 256*scale),(-256*scale,256*scale),(-1,0),(0,-1)]
                # Python oracle finds a nearest-site contact independently of the Java probe.
                old = r['province'](seed,scale,-4096*scale,0)[:2]
                for x in range(-4096*scale+1,4096*scale):
                    if r['province'](seed,scale,x,0)[:2] != old:
                        points.extend([(x-1,0),(x,0)]); break
                case['boundaries'] = [server.command(f'acceptance terrain-compare {x} {z}') for x,z in points]
                server.command('acceptance coarse-clear')
                reverse = [server.command(f'acceptance terrain-compare {x} {z}') for x,z in reversed(points)]
                require(case['boundaries'] == list(reversed(reverse)), 'Comparison traversal mismatch')
                require(case['boundaries'][-2]['province'] != case['boundaries'][-1]['province'], 'No province boundary')
                case['suite'] = server.command('acceptance coarse-suite')
                case['oracle'] = server.command('acceptance coarse-check')
                case['sample'] = server.command('acceptance chunk overworld -32 -65')
                server.stop(); h['storage_ok'](server)
                snapshot = (world/h['SNAPSHOT']).read_bytes(); terrain = live['terrain'](world)
                require(terrain, 'No persisted terrain')
                h['cleanup_cache'](server); server.start()
                case['reopened'] = server.command('acceptance chunk overworld -32 -65')
                server.stop(); h['storage_ok'](server)
                require(case['sample']['blocks_sha256'] == case['reopened']['blocks_sha256'], 'Complete blocks changed')
                require(snapshot == (world/h['SNAPSHOT']).read_bytes() and terrain == live['terrain'](world), 'Snapshot/terrain changed')
                case.update(snapshot_sha256=r['sha'](world/h['SNAPSHOT']), persisted_records=len(terrain),
                            terrain_snapshot_unchanged=True, traversal_equal=True, exit_code=server.process.returncode)
                case['logs'] = {p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                result['cases'].append(case)
                (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
                print('PASS',case['name'],flush=True)
            finally:
                h['close'](server); h['cleanup_cache'](server)
    require(models == base['manifest'](args.models) and template == base['manifest'](args.template), 'Shared inputs changed')
    result['shared_inputs_unchanged'] = True
    (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','output','baseline'): p.add_argument('--'+name,type=Path,required=True)
    for name,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                       'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                       'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():
        p.add_argument('--'+name,type=Path,default=r['ROOT']/value)
    args=p.parse_args()
    for name,value in vars(args).items(): setattr(args,name,value.resolve())
    run(args)
