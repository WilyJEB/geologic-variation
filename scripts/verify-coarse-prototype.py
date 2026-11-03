"""NEW CPU paired evidence-only sampler fixtures and generator-only artifact guard.

Production remains geology-1. The alternate artifact changes only the class-file
UTF8 generator constant, exercising a real runtime/saved identity mismatch without
claiming an implemented alternate world generator.
"""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import zipfile

live = runpy.run_path(str(Path(__file__).with_name('verify-live-context.py')))
h = live['helpers']; r = h['runtime']; require = h['require']


def manifest(path):
    return {p.relative_to(path).as_posix(): r['sha'](p) for p in path.rglob('*') if p.is_file()}


def alternate(source, target):
    old = b'\x01\x00\x09geology-1'
    new = b'\x01\x00\x11coarse-evidence-1'  # corrected below from actual UTF8 size
    identity = b'coarse-evidence-1'
    new = b'\x01' + len(identity).to_bytes(2, 'big') + identity
    changed = []
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.endswith('.class') and old in data:
                data = data.replace(old, new); changed.append(info.filename)
            dst.writestr(info, data)
    require(changed, 'No generator constant changed')
    return {'generator': identity.decode(), 'changed_classes': changed, 'sha256': r['sha'](target)}


def run(args):
    require(r['sha'](args.td) == '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8', 'CPU pin')
    args.output.mkdir(parents=True, exist_ok=False)
    models = manifest(args.models); template = manifest(args.template)
    result = {'sources': {p.name:r['sha'](p) for p in [Path(__file__),Path(__file__).with_name('runtime-acceptance.py')]},
              'models':models, 'cases':[], 'production_generator':'geology-1', 'prototype':'coarse-evidence-1'}
    original = args.addon
    fixture = None
    for scale, trial in [(1,0),(1,1),(1,2),(6,0)]:
        arms = ['current','coarse'] if trial % 2 == 0 else ['coarse','current']
        for arm in arms:
            require(shutil.disk_usage(args.output).free >= 2*1024**3, 'Need 2 GiB free')
            server = r['Server'](args, f's{scale}-t{trial}-{arm}', scale=scale, link_td=True)
            item = {'name':server.path.name, 'scale':scale, 'trial':trial, 'arm':arm}
            try:
                print('START',item['name'],flush=True)
                server.start()
                item['settings'] = server.command('acceptance settings')
                require('CPU/' in item['settings']['context'], 'CPU required')
                item['cold'] = server.command(f'acceptance coarse-measure {arm} {8192*scale} {8192*scale}')
                item['warm'] = [server.command(f'acceptance coarse-measure {arm} {8192*scale} {8192*scale}') for _ in range(5)]
                item['second_cold'] = server.command(f'acceptance coarse-measure {arm} {4096*scale} {4096*scale}')
                if arm == 'coarse' and trial == 0:
                    item['contract'] = server.command('acceptance coarse-check')
                    item['suite'] = server.command('acceptance coarse-suite')
                # Worldgen still uses production geology-1; timed diagnostic never replaces it.
                item['sample'] = server.command(f'acceptance chunk overworld {-32*scale} {-65*scale}')
                server.stop();h['storage_ok'](server)
                world=server.path/'world'; snapshot=world/h['SNAPSHOT']
                before=live['terrain'](world);snap=snapshot.read_bytes()
                h['cleanup_cache'](server)
                server.start()
                item['reopened'] = server.command(f'acceptance chunk overworld {-32*scale} {-65*scale}')
                server.stop();h['storage_ok'](server)
                require(item['sample']['blocks_sha256']==item['reopened']['blocks_sha256'],'Reopen complete blocks changed')
                require(before==live['terrain'](world) and before,'Reopen persisted terrain changed')
                require(snap==snapshot.read_bytes(),'Reopen snapshot changed')
                item['persisted_records']=len(before);item['snapshot_sha256']=r['sha'](snapshot)
                item['terrain_unchanged']=True
                if fixture is None: fixture=world
                item['artifacts']={p.name:r['sha'](p) for p in (server.path/'mods').glob('*.jar')}
                item['logs']={p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                item['exit_code']=server.process.returncode
                result['cases'].append(item)
                (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
                print('PASS',item['name'], 'cold_ms',item['cold']['ms'], 'delta',item['cold']['delta'],flush=True)
            finally:
                h['close'](server);h['cleanup_cache'](server)
    alternate_jar=args.output/'generator-boundary.jar'
    result['alternate']=alternate(original,alternate_jar)
    args.addon=alternate_jar
    server=r['Server'](args,'generator-boundary',link_td=True)
    world=server.path/'world'
    shutil.copytree(fixture,world,dirs_exist_ok=True)
    before=live['terrain'](world);snap=(world/h['SNAPSHOT']).read_bytes()
    try:
        result['generator_rejection']=h['rejected'](server,'Incompatible geology generation context','generator')
        require(before==live['terrain'](world),'Rejection changed terrain')
        require(snap==(world/h['SNAPSHOT']).read_bytes(),'Rejection changed snapshot')
        for jar in (server.path/'mods').glob('*.jar'):
            if jar.name==alternate_jar.name: jar.unlink()
        shutil.copy2(original,server.path/'mods'/original.name)
        h['cleanup_cache'](server)
        server.start(); restored=h['observe'](server); server.stop();h['storage_ok'](server)
        require(restored['chunk']['blocks_sha256']==result['cases'][0]['sample']['blocks_sha256'],'Restored sample changed')
        require(before==live['terrain'](world),'Restored terrain changed')
        require(snap==(world/h['SNAPSHOT']).read_bytes(),'Restored snapshot changed')
        result['generator_restoration']={'restored':restored,'persisted_records':len(before),'terrain_snapshot_unchanged':True,
            'logs':{p.name:r['sha'](p) for p in server.path.glob('console-*.log')}}
    finally:
        h['close'](server);h['cleanup_cache'](server)
    require(models==manifest(args.models) and template==manifest(args.template),'Shared input changed')
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
