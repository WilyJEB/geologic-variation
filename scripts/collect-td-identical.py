"""Frozen four-process identical-rectangle controls. No replacement launches."""
import argparse
import gzip
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import threading
import time

v=runpy.run_path(str(Path(__file__).with_name('verify-td-landforms.py')))
r,h,base,ROOT=v['r'],v['h'],v['base'],v['ROOT']
SOURCES=('scripts/collect-td-identical.py','scripts/runtime-acceptance.py','scripts/verify-context-startup.py',
 'scripts/verify-td-landforms.py','scripts/verify-sampling-support.py','scripts/verify-td-numerics.py',
 'src/runtimeProbe/java/dev/wilyjeb/geology/probe/NumericalSupport.java',
 'src/runtimeProbe/java/dev/wilyjeb/geology/probe/SamplingDiagnostic.java','docs/td-axis-numerical-protocol.md')
SOURCES=tuple(sorted(set(SOURCES)|{p.relative_to(ROOT).as_posix() for pattern in
    ('scripts/*.py','src/runtimeProbe/**/*.java','src/runtimeProbe/**/*.json') for p in ROOT.glob(pattern)}))


def sequence(index):
    cols=[6,-6] if index==2 else [-6,6]
    reads=[f'acceptance numeric {c} -14 0' for c in cols]
    result=reads*2
    if index==0:
        result+=['acceptance numeric-control prime-left','acceptance numeric-control prime-right',
                 'acceptance numeric-control observe']+reads
        result+=['acceptance numeric-control diagnostic-clear','acceptance numeric-control observe']+reads
        result+=reads+['acceptance numeric-control provider-clear','acceptance numeric-control observe']+reads
    return result


def run(args):
    assert r['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8'
    args.output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();halt=threading.Event();done=threading.Event();active=[None];samples=[]
    data=dict(base='1c31c0f',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        sources={n:r['sha'](ROOT/n) for n in SOURCES},models=base['manifest'](args.models),
        template=base['manifest'](args.template),artifacts={str(p.relative_to(ROOT)):r['sha'](p) for p in (args.td,args.addon,args.probe)},
        java_version=subprocess.check_output([str(args.java),'-version'],stderr=subprocess.STDOUT,text=True),
        java_sha256=r['sha'](args.java),cases=[],launch_attempts=0,direct_request_attempts=0,monitor_failures=[])
    for n in SOURCES:
        p=args.output/'executed-sources'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    # Pin the actual artifact's public cache behavior, independently of source checkout.
    javap=args.java.with_name('javap.exe')
    raw=subprocess.check_output([str(javap),'-classpath',str(args.td),'-c','-p',
        'com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider'],text=True)
    (args.output/'provider-javap.txt').write_text(raw)
    data['provider_javap_sha256']=r['sha'](args.output/'provider-javap.txt')
    def save():
        data['elapsed_seconds']=time.monotonic()-started
        (args.output/'results.json').write_text(json.dumps(data,indent=2)+'\n')
    def monitor():
        while not done.wait(1):
            server=active[0];failure=None;memory=None
            if time.monotonic()-started>=1800:failure='wall time'
            if shutil.disk_usage(args.output).free<4*1024**3:failure='disk reserve'
            if server is not None and hasattr(server,'process') and server.process.poll() is None:
                try:
                    memory=int(subprocess.check_output(['powershell','-NoProfile','-Command',
                        f'(Get-Process -Id {server.process.pid}).WorkingSet64'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip())
                    samples.append(dict(seconds=time.monotonic()-started,pid=server.process.pid,working_set_bytes=memory))
                    if memory>16*1024**3:failure='working set'
                except Exception as e:
                    if server.process.poll() is None:failure='monitor '+repr(e)
            if failure:
                data['monitor_failures'].append(failure);halt.set()
                if server is not None and hasattr(server,'process') and server.process.poll() is None:
                    subprocess.run(['taskkill','/PID',str(server.process.pid),'/T','/F'],capture_output=True)
                return
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    try:
        for index,scale in enumerate((1,1,1,6)):
            assert not halt.is_set() and time.monotonic()-started<1800 and shutil.disk_usage(args.output).free>=4*1024**3
            case=dict(index=index,seed=-2026110411,scale=scale,role='development',events=[],planned_sequence=sequence(index))
            data['cases'].append(case);save()
            server=r['Server'](args,f'cpu-{index}',scale=scale,link_td=True);active[0]=server
            p=server.path/'world/level.dat';tag=r['nbt_read'](gzip.decompress(p.read_bytes()))
            tag[2]['Data'][1]['WorldGenSettings'][1]['seed']=(4,-2026110411)
            p.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
            snapshot=server.path/'world'/h['SNAPSHOT'];snapshot.write_text(re.sub(r'^seed=-?\d+$','seed=-2026110411',snapshot.read_text(),flags=re.M))
            before=snapshot.read_bytes();case['config_before']=base['manifest'](server.path/'config')
            def command(cmd):
                assert not halt.is_set() and time.monotonic()-started<1800
                assert shutil.disk_usage(args.output).free>=4*1024**3
                if cmd.startswith('acceptance numeric ') or 'prime-' in cmd:
                    assert data['direct_request_attempts']<26
                    data['direct_request_attempts']+=1;case['inflight']=cmd;save()
                value=server.command(cmd);case['events'].append(dict(command=cmd,result=value));case.pop('inflight',None)
                if 'file' in value:value['sha256']=r['sha'](server.path/'numerical-bits'/value['file'])
                save();return value
            def metrics():
                m=command('acceptance metrics')
                assert m['computed_windows']<=1500
                others=sum(c.get('final_metrics',{}).get('computed_windows',0) for c in data['cases'] if c is not case)
                assert others+m['computed_windows']<=6000
                return m
            try:
                assert data['launch_attempts']<4
                data['launch_attempts']+=1;save()  # Failure consumes launch budget.
                server.start();case['initial_metrics']=metrics()
                case['settings']=command('acceptance settings')
                assert 'CPU/Windows' in case['settings']['context'] and 'seed=-2026110411' in case['settings']['context']
                command('acceptance numeric-control observe')
                for cmd in sequence(index):
                    command(cmd);metrics()
                case['final_metrics']=metrics();server.stop();h['storage_ok'](server)
                case.update(exit_code=server.process.returncode,snapshot_unchanged=before==snapshot.read_bytes(),
                    config=base['manifest'](server.path/'config'))
                assert case['snapshot_unchanged']
            except BaseException as e:
                case['failure']=repr(e);save();raise
            finally:
                h['close'](server)
                case['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                case['launch_args_sha256']=r['sha'](server.path/'launch-args.txt') if (server.path/'launch-args.txt').exists() else None
                h['cleanup_cache'](server);active[0]=None;save()
        data['shared_inputs_unchanged']=data['models']==base['manifest'](args.models) and data['template']==base['manifest'](args.template)
        assert data['shared_inputs_unchanged'] and not halt.is_set()
    finally:
        done.set();thread.join(timeout=10);data['memory_samples']=samples;save()


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('java','td','output'):p.add_argument('--'+n,type=Path,required=True)
    for n,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models','template':'runs/server/world',
        'addon':'build/libs/geologic-variation-0.2.2-dev.jar','probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():p.add_argument('--'+n,type=Path,default=ROOT/value)
    args=p.parse_args()
    for n,value in vars(args).items():
        if isinstance(value,Path):setattr(args,n,value.resolve())
    run(args)
