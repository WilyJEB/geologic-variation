"""Frozen bounded local tracker collection on NEW CPU fixtures; diagnostic only."""
import argparse
import gzip
import json
from pathlib import Path
import re
import runpy
import shutil
import time
import zipfile

v=runpy.run_path(str(Path(__file__).with_name('verify-td-landforms.py')))
s=runpy.run_path(str(Path(__file__).with_name('td-tracking-selector.py')))
r=v['r'];h=v['h'];base=v['base'];require=v['require'];ROOT=v['ROOT']


def locations(case):
    points=v['fixed_selection'](case['scan'],case['seed'],case['scale'])
    for i,a in enumerate(case['attempts']):
        for j,(x,z) in enumerate(s['profile'](a['candidate'],a['diagnosis'])):
            points.append(dict(x=x*case['scale'],z=z*case['scale'],selection=f'feature_{i}_{j}'))
    result={}
    for p in points:
        key=p['x'],p['z']
        if key not in result:result[key]=dict(x=p['x'],z=p['z'],groups=[])
        result[key]['groups'].append(p['selection'])
    return list(result.values())


def run(args):
    require(r['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8','CPU pin')
    with zipfile.ZipFile(args.baseline) as old,zipfile.ZipFile(args.addon) as new:
        require(old.namelist()==new.namelist() and all(old.read(n)==new.read(n) for n in old.namelist()),'Production changed')
    args.output.mkdir(parents=True,exist_ok=False)
    models=base['manifest'](args.models);template=base['manifest'](args.template)
    sources=list(json.loads((ROOT/'docs/evidence/td-landforms-2026-11-03.json').read_text())['sources'])
    sources+=['scripts/'+n for n in ('verify-td-tracking.py','td-tracking-selector.py','summarize-td-tracking.py','test-td-tracking.py')]
    sources+=['src/runtimeProbe/java/dev/wilyjeb/geology/probe/TrackingPatch.java','docs/td-tracking-protocol.md']
    data=dict(main_commit='e3fdbcfba945945a15f7bf65710df69b3fea6b9f',protocol_commit=args.protocol_commit,
        sources={n:r['sha'](ROOT/n) for n in sources},production_sha256=r['sha'](args.addon),
        baseline_sha256=r['sha'](args.baseline),probe_sha256=r['sha'](args.probe),models=models,cases=[])
    total_start=time.monotonic()
    for seed,split in s['SEEDS']:
        for scale in (1,6):
            require(shutil.disk_usage(args.output).free>=1024**3,'Need 1 GiB reserve')
            server=r['Server'](args,f'seed{seed}-s{scale}',scale=scale,link_td=True)
            path=server.path/'world/level.dat';tag=r['nbt_read'](gzip.decompress(path.read_bytes()))
            tag[2]['Data'][1]['WorldGenSettings'][1]['seed']=(4,seed)
            path.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
            path=server.path/'world'/h['SNAPSHOT'];path.write_text(re.sub(r'^seed=-?\d+$',f'seed={seed}',path.read_text(),flags=re.M))
            snapshot=path.read_bytes();start=time.monotonic()
            case=dict(name=server.path.name,seed=seed,scale=scale,split=split,scan=[],attempts=[],events=[],observations=[])
            def command(cmd):
                require(time.monotonic()-start<2700 and time.monotonic()-total_start<14400,'Time budget')
                require(shutil.disk_usage(args.output).free>=512*1024**2,'Disk reserve')
                value=server.command(cmd);case['events'].append(dict(command=cmd,result=value))
                if isinstance(value,dict) and 'computed_windows' in value:
                    require(value['computed_windows']-case['initial_metrics']['computed_windows']<=12000,'Window budget')
                return value
            def patch(c,reverse=False):
                command('acceptance track-clear')
                rows=[command(f"acceptance track-patch {c['col']} {c['row']} {i}") for i in (reversed(range(49)) if reverse else range(49))]
                command('acceptance metrics')
                return list(reversed(rows)) if reverse else rows
            try:
                server.start();case['initial_metrics']=server.command('acceptance metrics')
                case['settings']=command('acceptance settings')
                require('CPU/' in case['settings']['context'] and f'seed={seed}' in case['settings']['context'],'Context')
                for row in range(-64,65,16):
                    for col in range(-64,65,16):
                        x,z=col*256*scale,row*256*scale
                        case['scan'].append(dict(x=x,z=z,evidence=command(f'acceptance coarse {x} {z}')))
                for c in s['seeds'](case['scan']):
                    stations=[command(f'acceptance coarse {col*256*scale} {row*256*scale}') for row,col in s['legacy']['stations'](c)]
                    bands=patch(c)
                    case['attempts'].append(dict(candidate=c,legacy_stations=stations,legacy_evaluation=s['legacy']['evaluate'](c,stations),
                        bands=bands,diagnosis=s['diagnose'](c,bands)))
                case['selection']=locations(case);require(len(case['selection'])<=52,'Fine collection limit')
                command('acceptance sampling-clear');case['before']=command('acceptance metrics')
                for p in case['selection']:
                    row=command(f"acceptance sampling-compare {p['x']} {p['z']}")
                    case['observations'].append(dict(row,groups=p['groups']));command('acceptance metrics')
                    (args.output/'progress.json').write_text(json.dumps(case,indent=2)+'\n')
                case['after']=command('acceptance metrics')
                command('acceptance sampling-clear')
                case['reverse']=[command(f"acceptance sampling-compare {p['x']} {p['z']}") for p in reversed(case['selection'])]
                for a in reversed(case['attempts']):a['reverse_bands']=patch(a['candidate'],True)
                case['suite']=command('acceptance coarse-suite');case['oracle']=command('acceptance coarse-check')
                case['final_metrics']=command('acceptance metrics')
                command('acceptance track-clear')
                server.stop();h['storage_ok'](server)
                require(snapshot==path.read_bytes(),'Snapshot changed')
                case.update(snapshot_unchanged=True,snapshot_sha256=r['sha'](path),exit_code=server.process.returncode)
                case['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                data['cases'].append(case);(args.output/'results.json').write_text(json.dumps(data,indent=2)+'\n')
                print('PASS',case['name'],flush=True)
            finally:h['close'](server);h['cleanup_cache'](server)
    require(models==base['manifest'](args.models) and template==base['manifest'](args.template),'Shared inputs changed')
    data['shared_inputs_unchanged']=True
    (args.output/'results.json').write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','output','baseline'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--protocol-commit',required=True)
    for name,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models','template':'runs/server/world',
        'addon':'build/libs/geologic-variation-0.2.2-dev.jar','probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():p.add_argument('--'+name,type=Path,default=ROOT/value)
    args=p.parse_args()
    for name,value in vars(args).items():
        if isinstance(value,Path):setattr(args,name,value.resolve())
    run(args)
