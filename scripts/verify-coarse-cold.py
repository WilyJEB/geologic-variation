"""Independent far-away cold-tensor pairs after the near/startup-warm matrix.

Uses NEW fixtures and does not overlap any other inference or compilation.
"""
import argparse
import json
from pathlib import Path
import runpy
import shutil

base=runpy.run_path(str(Path(__file__).with_name('verify-coarse-prototype.py')))
r=base['r'];h=base['h'];require=base['require'];manifest=base['manifest']


def run(args):
    require(r['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8','CPU pin')
    args.output.mkdir(parents=True,exist_ok=False)
    models=manifest(args.models);template=manifest(args.template)
    result={'cases':[], 'sources':{p.name:r['sha'](p) for p in [Path(__file__),Path(__file__).with_name('verify-coarse-prototype.py'),Path(__file__).with_name('runtime-acceptance.py')]}}
    for trial in range(3):
        for arm in (['current','coarse'] if trial%2==0 else ['coarse','current']):
            require(shutil.disk_usage(args.output).free>=2*1024**3,'Need 2 GiB free')
            server=r['Server'](args,f't{trial}-{arm}',link_td=True)
            item={'name':server.path.name,'arm':arm,'trial':trial}
            try:
                print('START',item['name'],flush=True);server.start()
                item['settings']=server.command('acceptance settings')
                require('CPU/' in item['settings']['context'],'CPU required')
                item['cold']=server.command(f'acceptance coarse-measure {arm} 65536 65536')
                require(item['cold']['delta']['computed_windows']>0,'Not cold TD tensor work')
                item['warm']=[server.command(f'acceptance coarse-measure {arm} 65536 65536') for _ in range(5)]
                item['environment']=server.command('acceptance prepare')
                server.stop();h['storage_ok'](server)
                item['artifacts']={p.name:r['sha'](p) for p in (server.path/'mods').glob('*.jar')}
                item['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                item['exit_code']=server.process.returncode
                result['cases'].append(item)
                (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
                print('PASS',item['name'],item['cold'],flush=True)
            finally:
                h['close'](server);h['cleanup_cache'](server)
    require(models==manifest(args.models) and template==manifest(args.template),'Shared inputs changed')
    result['shared_inputs_unchanged']=True
    (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','output'):p.add_argument('--'+name,type=Path,required=True)
    for name,value in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                       'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                       'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():
        p.add_argument('--'+name,type=Path,default=r['ROOT']/value)
    args=p.parse_args()
    for name,value in vars(args).items():setattr(args,name,value.resolve())
    run(args)
