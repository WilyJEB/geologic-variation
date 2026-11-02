"""Trace natural scale-6 coal population in four NEW disposable production worlds."""
import argparse
import json
from pathlib import Path
import runpy
import shutil

runtime = runpy.run_path(str(Path(__file__).with_name('runtime-acceptance.py')))
ROOT = runtime['ROOT']


def run(args):
    args.output.mkdir(parents=True,exist_ok=False)
    results=[]
    for addon in (False,True):
        for trial in (0,1):
            name=f'coal-s6-t{trial}-'+('addon' if addon else 'td-only')
            if shutil.disk_usage(args.output).free < 2*1024*1024*1024:
                raise RuntimeError('Less than 2 GiB free for transient ONNX optimization; refusing another world')
            server=runtime['Server'](args,name,addon=addon,scale=6,link_td=True)
            plan=runtime['targets'](server.seed,6)
            order=list(plan['chunks'])
            if trial:
                order.reverse()
            item={'name':name,'addon':addon,'trial':trial,'plan':plan,
                  'artifacts':{p.name:runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))}}
            try:
                server.start()
                server.command('acceptance trace-reset')
                for x,z in plan['chunks']:
                    server.command(f'acceptance trace-watch {x} {z}')
                item['chunks']=[server.command(f'acceptance chunk overworld {x} {z}') for x,z in order]
                item['trace_summary']=server.command('acceptance trace-summary')
                server.stop()
                console=(server.path/'console-1.log').read_text(errors='replace')
                if 'No space left on device' in console or 'There is not enough space on the disk' in console or 'Failed to save chunk' in console:
                    raise RuntimeError('Save/storage failure invalidates the trace case')
                trace=server.path/'coal-write-trace.json'
                raw=json.loads(trace.read_text())
                if raw['overflow'] or raw['unmatched_writes'] or not any(r['event']=='write' for r in raw['records']):
                    raise RuntimeError('Incomplete or empty natural trace')
                item['trace_sha256']=runtime['sha'](trace)
                item['logs']={p.name:runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))}
            finally:
                if hasattr(server,'process') and server.process.poll() is None:
                    server.stop()
                # These are regenerated optimization outputs, not the five pinned model inputs.
                # Never remove a cache while its process is alive or outside this new test case.
                cache=(server.path/'terrain-diffusion-models/onnx-cache').resolve()
                if not cache.is_relative_to(server.path.resolve()):
                    raise RuntimeError('Optimization cache resolved outside the disposable test case')
                if cache.exists() and (not hasattr(server,'process') or server.process.poll() is not None):
                    shutil.rmtree(cache)
                    item['optimized_cache_removed']=True
            results.append(item)
            (args.output/'trace-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--td',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,default=ROOT/'runs/acceptance/runtime')
    parser.add_argument('--models',type=Path,default=ROOT/'runs/server/terrain-diffusion-models')
    parser.add_argument('--template',type=Path,default=ROOT/'runs/server/world')
    parser.add_argument('--addon',type=Path,default=ROOT/'build/libs/geologic-variation-0.2.2-dev.jar')
    parser.add_argument('--probe',type=Path,default=ROOT/'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar')
    args=parser.parse_args()
    for name,value in vars(args).items():
        setattr(args,name,value.resolve())
    run(args)
