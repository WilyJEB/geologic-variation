"""Predefined, bounded sampling-policy experiment; production remains geology-1."""
import argparse
import gzip
import json
from pathlib import Path
import re
import runpy
import shutil
import zipfile

d = runpy.run_path(str(Path(__file__).with_name('verify-terrain-diagnostics.py')))
base=d['base']; r=d['r']; h=d['h']; live=d['live']; require=d['require']
SEEDS = [(-1550453200536840819,'development'),(8675309,'development'),(20261103,'held_out')]


def curvature(point):
    v=point['evidence']['elevations']
    xx=v[3]+v[5]-2*v[4]; zz=v[1]+v[7]-2*v[4]
    return xx,zz


def select(scan):
    # Representative coverage is fixed before seeing terrain, not a probability sample.
    chosen=[dict(scan[i],selection='coverage') for i in (0,20,40,60,80)]
    extremes=d['select'](scan)
    chosen += [dict(p,selection='extreme_'+label) for label,p in extremes.items()]
    land=sorted((p for p in scan if d['tendency'](p['evidence'])=='land'),key=lambda p:(p['evidence']['mean_metres'],p['z'],p['x']))
    chosen.append(dict(land[len(land)//2],selection='intermediate_land'))
    # Strong cross-axis second difference, weak along-axis second difference.
    # These are targeted ridge/basin candidates, not confirmed geological structures.
    for sign,label in ((-1,'ridge_candidate'),(1,'basin_candidate')):
        def score(p):
            xx,zz=curvature(p)
            strong,weak=sorted((xx,zz),key=abs,reverse=True)
            return sign*strong-abs(weak)
        point=max(scan,key=score)
        chosen.append(dict(point,selection=label,curvature=curvature(point),selection_score=score(point)))
    return chosen


def boundary_points(seed,scale):
    result=[]; stride=256*scale
    # Two coarse and two fixed-grid edges, signed and axis varied.
    for axis,edge,other in [('x',-stride,3*stride),('z',2*stride,-3*stride),
                            ('x',-4*stride,-2*stride),('z',4*stride,2*stride)]:
        for offset in (-1,0):
            result.append({'x':edge+offset if axis=='x' else other,
                           'z':other if axis=='x' else edge+offset,'selection':'grid_boundary'})
    # Two distinct nearest-site contacts from independent Python oracle.
    for z in (-1024*scale,1024*scale):
        old=r['province'](seed,scale,-4096*scale,z)[:2]
        for x in range(-4096*scale+16,4096*scale,16):
            new=r['province'](seed,scale,x,z)[:2]
            if new!=old:
                edge=next(q for q in range(x-15,x+1) if r['province'](seed,scale,q,z)[:2]!=old)
                result.extend({'x':q,'z':z,'selection':'province_boundary'} for q in (edge-1,edge))
                break
            old=new
    require(len(result)==12,'Boundary coverage missing')
    return result


def canonical(row):
    return {k:v for k,v in row.items() if k not in ('delta','fine_cache_entries','selection')}


def run(args):
    require(r['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8','CPU pin')
    args.output.mkdir(parents=True,exist_ok=False)
    models=base['manifest'](args.models);template=base['manifest'](args.template)
    with zipfile.ZipFile(args.baseline) as old,zipfile.ZipFile(args.addon) as new:
        require(old.namelist()==new.namelist() and all(old.read(n)==new.read(n) for n in old.namelist()),'Production changed')
    sources=[Path(__file__),*map(lambda n:Path(__file__).with_name(n),
        ['verify-terrain-diagnostics.py','verify-coarse-prototype.py','verify-live-context.py',
         'verify-context-startup.py','runtime-acceptance.py','compare-runtime-chunks.py'])]
    sources+=list((r['ROOT']/'src/runtimeProbe').rglob('*.java'))
    result={'main_commit':'05bd8b9accf80f699eb3bc5589f4b280fe9a5eae','sources':{p.relative_to(r['ROOT']).as_posix():r['sha'](p) for p in sources},
        'production_sha256':r['sha'](args.addon),'baseline_sha256':r['sha'](args.baseline),
        'probe_sha256':r['sha'](args.probe),'models':models,'cases':[]}
    for seed,split in SEEDS:
        for scale in (1,6):
            require(shutil.disk_usage(args.output).free>2*1024**3,'Need 2 GiB free')
            server=r['Server'](args,f'seed{seed}-s{scale}',scale=scale,link_td=True)
            world=server.path/'world'
            path=world/'level.dat';tag=r['nbt_read'](gzip.decompress(path.read_bytes()))
            tag[2]['Data'][1]['WorldGenSettings'][1]['seed']=(4,seed)
            path.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
            path=world/h['SNAPSHOT'];path.write_text(re.sub(r'^seed=-?\d+$',f'seed={seed}',path.read_text(),flags=re.M))
            case={'name':server.path.name,'seed':seed,'split':split,'scale':scale,'scan':[],'observations':[]}
            try:
                server.start();case['settings']=server.command('acceptance settings')
                require('CPU/' in case['settings']['context'] and f'seed={seed}' in case['settings']['context'],'Context')
                for row in range(-64,65,16):
                    for col in range(-64,65,16):
                        x,z=col*256*scale,row*256*scale
                        case['scan'].append({'x':x,'z':z,'evidence':server.command(f'acceptance coarse {x} {z}')})
                case['selection']=select(case['scan'])+boundary_points(seed,scale)
                server.command('acceptance sampling-clear')
                case['before']=server.command('acceptance metrics')
                for point in case['selection']:
                    row=server.command(f"acceptance sampling-compare {point['x']} {point['z']}")
                    row['selection']=point['selection'];case['observations'].append(row)
                    (args.output/'progress.json').write_text(json.dumps(case,indent=2)+'\n')
                case['after']=server.command('acceptance metrics')
                server.command('acceptance sampling-clear')
                reverse=[server.command(f"acceptance sampling-compare {p['x']} {p['z']}") for p in reversed(case['selection'])]
                require([canonical(v) for v in case['observations']]==[canonical(v) for v in reversed(reverse)],'Traversal changed')
                case['reverse_deltas']=[v['delta'] for v in reverse];case['traversal_equal']=True
                case['suite']=server.command('acceptance coarse-suite');case['oracle']=server.command('acceptance coarse-check')
                case['sample']=server.command('acceptance chunk overworld -32 -65')
                server.stop();h['storage_ok'](server)
                snapshot=(world/h['SNAPSHOT']).read_bytes();terrain=live['terrain'](world)
                require(terrain,'No persisted terrain')
                h['cleanup_cache'](server);server.start();case['reopened']=server.command('acceptance chunk overworld -32 -65')
                server.stop();h['storage_ok'](server)
                require(case['sample']['blocks_sha256']==case['reopened']['blocks_sha256'],'Complete sample changed')
                require(snapshot==(world/h['SNAPSHOT']).read_bytes() and terrain==live['terrain'](world),'Snapshot/terrain changed')
                case.update(snapshot_sha256=r['sha'](world/h['SNAPSHOT']),persisted_records=len(terrain),terrain_snapshot_unchanged=True,exit_code=server.process.returncode)
                case['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                result['cases'].append(case)
                (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
                print('PASS',case['name'],flush=True)
            finally:
                h['close'](server);h['cleanup_cache'](server)
    require(models==base['manifest'](args.models) and template==base['manifest'](args.template),'Shared inputs changed')
    result['shared_inputs_unchanged']=True
    (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','output','baseline'):p.add_argument('--'+name,type=Path,required=True)
    for name,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                       'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                       'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():p.add_argument('--'+name,type=Path,default=r['ROOT']/value)
    args=p.parse_args()
    for name,value in vars(args).items():setattr(args,name,value.resolve())
    run(args)
