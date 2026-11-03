"""Bounded diagnostic collection; frozen selector, NEW CPU fixtures, no output changes."""
import argparse
import gzip
import json
from pathlib import Path
import re
import runpy
import shutil
import time
import zipfile

s=runpy.run_path(str(Path(__file__).with_name('td-landform-selector.py')))
d=runpy.run_path(str(Path(__file__).with_name('verify-sampling-support.py')))
r=d['r']; h=d['h']; base=d['base']; require=d['require']; ROOT=r['ROOT']


def fixed_selection(scan, seed, scale):
    points=[dict(scan[i],selection='coverage') for i in (0,20,40,60,80)]
    groups={key:[p for p in scan if d['d']['tendency'](p['evidence'])==key] for key in ('ocean','coast','land')}
    if groups['ocean']: points.append(dict(min(groups['ocean'],key=lambda p:p['evidence']['mean_metres']),selection='ocean'))
    if groups['coast']: points.append(dict(min(groups['coast'],key=lambda p:abs(p['evidence']['mean_metres'])),selection='coast'))
    land=sorted(groups['land'],key=lambda p:(p['evidence']['mean_metres'],p['z'],p['x']))
    if land:
        points += [dict(land[i],selection=label) for i,label in [(0,'lowland'),(-1,'mountain'),(len(land)//2,'intermediate')]]
    points += d['boundary_points'](seed,scale)
    return points


def locations(case):
    stride=256*case['scale']
    points=fixed_selection(case['scan'],case['seed'],case['scale'])
    for i,c in enumerate(s['choose'](case['attempts'])):
        points += [dict(x=col*stride+stride//2,z=row*stride+stride//2,selection=f'feature_{i}_{j}')
                   for j,(row,col) in enumerate(s['profile'](c))]
    unique={}
    for p in points:
        key=p['x'],p['z']
        if key not in unique: unique[key]={'x':p['x'],'z':p['z'],'groups':[]}
        unique[key]['groups'].append(p['selection'])
    return list(unique.values())


def run(args):
    require(r['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8','CPU pin')
    with zipfile.ZipFile(args.baseline) as old,zipfile.ZipFile(args.addon) as new:
        require(old.namelist()==new.namelist() and all(old.read(n)==new.read(n) for n in old.namelist()),'Production changed')
    args.output.mkdir(parents=True,exist_ok=False)
    models=base['manifest'](args.models);template=base['manifest'](args.template)
    sources=[Path(__file__),Path(__file__).with_name('td-landform-selector.py'),
             Path(__file__).with_name('summarize-td-landforms.py'),ROOT/'docs/td-landform-protocol-2026-11-03.md']
    sources += [ROOT/name for name in json.loads((ROOT/'docs/evidence/sampling-support-2026-11-03.json').read_text())['sources']]
    data={'main_commit':'ce91c6abdc9793bf14014fd6bf4c6ac689acd934','protocol_commit':args.protocol_commit,
          'sources':{p.relative_to(ROOT).as_posix():r['sha'](p) for p in sources},
          'production_sha256':r['sha'](args.addon),'baseline_sha256':r['sha'](args.baseline),
          'probe_sha256':r['sha'](args.probe),'models':models,'cases':[]}
    total_start=time.monotonic()
    for seed,split in s['SEEDS']:
        for scale in (1,6):
            require(shutil.disk_usage(args.output).free>=1024**3,'Need 1 GiB reserve')
            server=r['Server'](args,f'seed{seed}-s{scale}',scale=scale,link_td=True)
            world=server.path/'world'; path=world/'level.dat';tag=r['nbt_read'](gzip.decompress(path.read_bytes()))
            tag[2]['Data'][1]['WorldGenSettings'][1]['seed']=(4,seed)
            path.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
            path=world/h['SNAPSHOT'];path.write_text(re.sub(r'^seed=-?\d+$',f'seed={seed}',path.read_text(),flags=re.M))
            snapshot=path.read_bytes()
            case={'name':server.path.name,'seed':seed,'split':split,'scale':scale,'scan':[],'attempts':[],'observations':[],'events':[]}
            start=time.monotonic()
            def command(cmd):
                require(time.monotonic()-start<2700 and time.monotonic()-total_start<14400,'Time budget')
                require(shutil.disk_usage(args.output).free>=512*1024**2,'Disk reserve')
                value=server.command(cmd);case['events'].append({'command':cmd,'result':value})
                if isinstance(value,dict) and 'computed_windows' in value:
                    require(value['computed_windows']-case['initial_metrics']['computed_windows']<=12000,'Window budget')
                return value
            try:
                server.start();case['initial_metrics']=server.command('acceptance metrics')
                case['settings']=command('acceptance settings')
                require('CPU/' in case['settings']['context'] and f'seed={seed}' in case['settings']['context'],'Context')
                for row in range(-64,65,16):
                    for col in range(-64,65,16):
                        x,z=col*256*scale,row*256*scale
                        case['scan'].append(dict(x=x,z=z,evidence=command(f'acceptance coarse {x} {z}')))
                for c in s['candidates'](case['scan']):
                    evidence=[command(f'acceptance coarse {col*256*scale} {row*256*scale}') for row,col in s['stations'](c)]
                    case['attempts'].append(dict(c,stations=evidence,evaluation=s['evaluate'](c,evidence)))
                case['selection']=locations(case);require(len(case['selection'])<=52,'Fine collection limit')
                command('acceptance sampling-clear');case['before']=command('acceptance metrics')
                for p in case['selection']:
                    row=command(f"acceptance sampling-compare {p['x']} {p['z']}")
                    case['observations'].append(dict(row,groups=p['groups']))
                    (args.output/'progress.json').write_text(json.dumps(case,indent=2)+'\n')
                    command('acceptance metrics')
                case['after']=command('acceptance metrics')
                command('acceptance sampling-clear')
                case['reverse']=[command(f"acceptance sampling-compare {p['x']} {p['z']}") for p in reversed(case['selection'])]
                require([{k:v for k,v in d['canonical'](a).items() if k!='groups'} for a in case['observations']]==
                        [d['canonical'](a) for a in reversed(case['reverse'])],'Traversal changed')
                case['suite']=command('acceptance coarse-suite');case['oracle']=command('acceptance coarse-check')
                case['final_metrics']=command('acceptance metrics')
                server.stop();h['storage_ok'](server)
                require(snapshot==path.read_bytes(),'Snapshot bytes changed')
                case.update(snapshot_sha256=r['sha'](path),snapshot_unchanged=True,exit_code=server.process.returncode)
                case['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                data['cases'].append(case)
                (args.output/'results.json').write_text(json.dumps(data,indent=2)+'\n')
                print('PASS',case['name'],flush=True)
            finally:
                h['close'](server);h['cleanup_cache'](server)
    require(models==base['manifest'](args.models) and template==base['manifest'](args.template),'Shared inputs changed')
    data['shared_inputs_unchanged']=True
    (args.output/'results.json').write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','output','baseline'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--protocol-commit',required=True)
    for name,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                       'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                       'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():p.add_argument('--'+name,type=Path,default=ROOT/value)
    args=p.parse_args()
    for name,value in vars(args).items():
        if isinstance(value,Path):setattr(args,name,value.resolve())
    run(args)
