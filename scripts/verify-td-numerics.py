"""Bounded exact-support CPU intervention matrix. Run once per frozen budget."""
import argparse
import gzip
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import time

v=runpy.run_path(str(Path(__file__).with_name('verify-td-landforms.py')))
r,h,base,ROOT=v['r'],v['h'],v['base'],v['ROOT']


def run(args):
    assert r['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8'
    args.output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();requests=0
    sources=['scripts/verify-td-numerics.py','scripts/td-geometry-arc.py','scripts/calibrate-td-geometry.py',
             'src/runtimeProbe/java/dev/wilyjeb/geology/probe/NumericalSupport.java','docs/td-geometry-numerics-protocol.md']
    data=dict(protocol_commit='fff65b4',base='6c5f105',sources={n:r['sha'](ROOT/n) for n in sources},
        artifacts={str(p.relative_to(ROOT)):r['sha'](p) for p in (args.td,args.addon,args.probe)},
        models=base['manifest'](args.models),template=base['manifest'](args.template),cases=[],requests=0)
    def save():
        data['elapsed_seconds']=time.monotonic()-start;data['requests']=requests
        (args.output/'results.json').write_text(json.dumps(data,indent=2)+'\n')
    for index,seed in enumerate((-2026110411,-2026110411,2026110407)):
        assert time.monotonic()-start<2400 and shutil.disk_usage(args.output).free>=4*1024**3
        case=dict(index=index,seed=seed,scale=1,role='development',events=[]);data['cases'].append(case);save()
        server=r['Server'](args,f'cpu-{index}',scale=1,link_td=True)
        path=server.path/'world/level.dat';tag=r['nbt_read'](gzip.decompress(path.read_bytes()))
        tag[2]['Data'][1]['WorldGenSettings'][1]['seed']=(4,seed)
        path.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
        snapshot=server.path/'world'/h['SNAPSHOT']
        snapshot.write_text(re.sub(r'^seed=-?\d+$',f'seed={seed}',snapshot.read_text(),flags=re.M))
        before=snapshot.read_bytes();case['config']=base['manifest'](server.path/'config')
        def command(cmd):
            nonlocal requests
            assert time.monotonic()-start<2400 and shutil.disk_usage(args.output).free>=4*1024**3
            # PowerShell sampling does not claim an instantaneous memory peak.
            memory=int(subprocess.check_output(['powershell','-NoProfile','-Command',
                f'(Get-Process -Id {server.process.pid}).WorkingSet64'],text=True).strip())
            assert memory<=16*1024**3
            if cmd.startswith('acceptance numeric'):
                requests+=2 if cmd.endswith(' 2') else 1
                assert requests<=32
            result=server.command(cmd);case['events'].append(dict(command=cmd,result=result,working_set_bytes=memory))
            if 'file' in result:
                file=server.path/'numerical-bits'/result['file'];result['sha256']=r['sha'](file)
            save();return result
        try:
            server.start();case['initial_metrics']=command('acceptance metrics')
            assert case['initial_metrics']['computed_windows']<=1500
            case['settings']=command('acceptance settings');assert 'CPU/' in case['settings']['context']
            cols=[-6,6] if index==0 else [6,-6]
            sequence=[(c,-14,m) for m in (0,0,1,2) for c in cols] if index<2 else [(65,12,m) for m in (0,1,3,0)]
            for c,row,m in sequence:
                command(f'acceptance numeric {c} {row} {m}')
                metrics=command('acceptance metrics');assert metrics['computed_windows']<=1500
            if index<2:
                command('acceptance sampling-clear')
                for c in reversed(cols):
                    command(f'acceptance numeric {c} -14 0')
                    metrics=command('acceptance metrics');assert metrics['computed_windows']<=1500
            case['final_metrics']=command('acceptance metrics')
            server.stop();h['storage_ok'](server)
            case.update(exit_code=server.process.returncode,snapshot_unchanged=before==snapshot.read_bytes())
            assert case['snapshot_unchanged']
        except Exception as e:
            case['failure']=repr(e);save();raise
        finally:
            h['close'](server)
            case['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
            h['cleanup_cache'](server);save()
    data['shared_inputs_unchanged']=data['models']==base['manifest'](args.models) and data['template']==base['manifest'](args.template)
    assert data['shared_inputs_unchanged'];save()


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('java','td','output'):p.add_argument('--'+name,type=Path,required=True)
    for name,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models','template':'runs/server/world',
        'addon':'build/libs/geologic-variation-0.2.2-dev.jar','probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():p.add_argument('--'+name,type=Path,default=ROOT/value)
    a=p.parse_args()
    for k,value in vars(a).items():
        if isinstance(value,Path):setattr(a,k,value.resolve())
    run(a)
