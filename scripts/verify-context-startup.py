"""Independent #9 dedicated startup rejection/restoration in NEW disposable worlds.

Only metadata/snapshots inside newly created test cases are mutated. The original
template, verified baseline, installed inputs and all user saves remain untouched.
"""
import argparse
import gzip
import json
from pathlib import Path
import re
import runpy
import shutil

runtime=runpy.run_path(str(Path(__file__).with_name('runtime-acceptance.py')))
ROOT=runtime['ROOT']
SNAPSHOT=Path('data/geologic_variation-geology.properties')
SAMPLE=(-32,-65)
POINT=(-508,-1027)


def require(value,message):
    if not value:
        raise RuntimeError(message)


def preserve(world):
    snapshot=world/SNAPSHOT
    return {'snapshot':runtime['sha'](snapshot) if snapshot.exists() else None,
            'regions':{p.relative_to(world).as_posix():runtime['sha'](p) for p in sorted(world.rglob('*.mca'))}}


def log(server):
    return server.path/f'console-{server.start_count}.log'


def storage_ok(server):
    text=log(server).read_text(errors='replace')
    require(not any(s in text for s in ('No space left on device','There is not enough space on the disk',
                                      'Failed to save chunk','Failed to store chunk')),'Storage error invalidates this test')


def close(server):
    if hasattr(server,'process') and server.process.poll() is None:
        server.stop()
    if hasattr(server,'console') and not server.console.closed:
        server.console.close()


def cleanup_cache(server):
    require(not hasattr(server,'process') or server.process.poll() is not None,'Cannot remove a live process cache')
    cache=(server.path/'terrain-diffusion-models/onnx-cache').resolve()
    require(cache.is_relative_to(server.path.resolve()),'Cache outside newly created test case')
    if cache.exists():
        shutil.rmtree(cache)


def observe(server):
    settings=server.command('acceptance settings')
    require(settings['owner_matches'],'Active settings belong to another server')
    return {'settings':settings,
            'chunk':server.command(f'acceptance chunk overworld {SAMPLE[0]} {SAMPLE[1]}'),
            'region':server.command(f'acceptance region {POINT[0]} {POINT[1]}')['region']}


def edited_config(server):
    (server.path/'config/geologic_variation-common.toml').write_text(
        '[geology]\nprovinceSpacingBlocks = 4096\noceanCeilingMetres = -300.0\n'
        'lowlandCeilingMetres = 700.0\nmountainFloorMetres = 1900.0\n'
        'gentleReliefMetres = 350.0\nruggedReliefMetres = 650.0\n')


def mutate(server,case):
    world=server.path/'world'
    if case=='seed':
        path=world/'level.dat';original=path.read_bytes()
        tag=runtime['nbt_read'](gzip.decompress(original))
        seed=tag[2]['Data'][1]['WorldGenSettings'][1]['seed'][1]
        tag[2]['Data'][1]['WorldGenSettings'][1]['seed']=(4,seed+1)
        path.write_bytes(gzip.compress(runtime['nbt_write'](tag),mtime=0))
    elif case=='scale':
        path=world/'data/terrain_diffusion_world_settings.dat';original=path.read_bytes()
        tag=runtime['nbt_read'](gzip.decompress(original))
        tag[2]['data'][1]['scale']=(3,6)
        path.write_bytes(gzip.compress(runtime['nbt_write'](tag),mtime=0))
    else:
        path=world/SNAPSHOT;original=path.read_bytes()
        if case=='schema1':
            text=original.decode().replace('\r\n','\n')
            text=re.sub(r'^(generator|seed|scale|tileSize|dependency|models|backend)=.*\n?','',text,flags=re.M)
            path.write_text(re.sub(r'^schema=2$', 'schema=1',text,flags=re.M))
        elif case=='missing':
            require(path.resolve().is_relative_to(server.path.resolve()),'Snapshot outside disposable case')
            path.unlink()
        elif case=='malformed':
            path.write_text(original.decode().replace('provinceSpacingBlocks=2048','provinceSpacingBlocks=invalid'))
        else:
            raise ValueError(case)
    return path,original


def rejected(server,expected,context_field=None):
    try:
        server.start()
    except RuntimeError:
        require(hasattr(server,'process') and server.process.poll() is not None,'Rejected server did not exit')
    else:
        raise RuntimeError('Incompatible world reached Ready')
    close(server);storage_ok(server)
    text=log(server).read_text(errors='replace')
    require('Geologic Variation is aborting this world:' in text and expected in text,'Missing intended guard diagnostic')
    contexts={}
    if context_field:
        match=re.search(r'Saved: GenerationContext\[(.*?)\]; runtime: GenerationContext\[(.*?)\]',text)
        require(match is not None,'Missing saved/runtime context records')
        saved,current=({k:v for k,v in (part.split('=',1) for part in value.split(', '))} for value in match.groups())
        changed=sorted(k for k in saved if saved[k]!=current[k])
        require(changed==[context_field],f'Expected only {context_field} to differ, got {changed}')
        contexts={'saved_context':saved,'runtime_context':current,'changed_context_fields':changed}
    require('Done (' not in text and 'RCON running on' not in text,'Rejection happened after Ready')
    require("Restore this world's original" in text,'Missing restoration guidance')
    return {'expected_diagnostic':expected,'process_exited':True,'exit_code':server.process.returncode,
            'ready':False,'console_sha256':runtime['sha'](log(server)),**contexts}


def run(args):
    args.output.mkdir(parents=True,exist_ok=False)
    require(shutil.disk_usage(args.output).free>=2*1024**3,'Need 2 GiB free for transient model optimization')
    results={'cases':[]}
    baseline=runtime['Server'](args,'baseline',scale=1,link_td=True)
    try:
        baseline.start();before=observe(baseline);baseline.stop();storage_ok(baseline)
        baseline_bytes=(baseline.path/'world'/SNAPSHOT).read_bytes()
        edited_config(baseline)
        baseline.start();after=observe(baseline);baseline.stop();storage_ok(baseline)
        require(before['settings']['active']==after['settings']['active'],'Config edit changed active settings')
        require(before['settings']['requested']!=after['settings']['requested'],'Requested config edit was not observed')
        require(before['settings']['context']==after['settings']['context'],'Context changed on config reload')
        require(before['chunk']['blocks_sha256']==after['chunk']['blocks_sha256'],'Existing blocks changed on reopen')
        require(before['region']==after['region'],'Region changed on config edit')
        require((baseline.path/'world'/SNAPSHOT).read_bytes()==baseline_bytes,'Snapshot rewritten on config edit')
        require("Saved world settings remain active" in log(baseline).read_text(),'Missing config-isolation warning')
        results['baseline']={'before':before,'after_config_edit':after,'snapshot_sha256':runtime['sha'](baseline.path/'world'/SNAPSHOT),
            'artifacts':{p.name:runtime['sha'](p) for p in sorted((baseline.path/'mods').glob('*.jar'))},
            'logs':{p.name:runtime['sha'](p) for p in sorted(baseline.path.glob('console-*.log'))}}
    finally:
        close(baseline);cleanup_cache(baseline)
    for case,expected in [('seed','Incompatible geology generation context'),('scale','Incompatible geology generation context'),('schema1','Unverified legacy geology context'),
                          ('missing','Existing world has no verified geology context'),('malformed','Cannot continue geology')]:
        require(shutil.disk_usage(args.output).free>=2*1024**3,'Need 2 GiB free before another test case')
        server=runtime['Server'](args,case,scale=1,link_td=True)
        # Clone only the verified baseline just created by this run, including its existing chunks.
        shutil.copytree(baseline.path/'world',server.path/'world',dirs_exist_ok=True)
        edited_config(server)
        world=server.path/'world'
        path,original=mutate(server,case)
        item={'name':case,'artifacts':{p.name:runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))},
              'before_rejection':preserve(world)}
        try:
            item['rejection']=rejected(server,expected,case if case in ('seed','scale') else None)
            item['after_rejection']=preserve(world)
            require(item['before_rejection']==item['after_rejection'],'Rejection changed snapshot or existing region bytes')
            # Exact restoration of this fixture's own verified bytes, not migration of an unknown save.
            path.write_bytes(original)
            server.start();item['restored']=observe(server);server.stop();storage_ok(server)
            require(item['restored']['settings']['active']==before['settings']['active'],'Restoration changed saved settings')
            require(item['restored']['settings']['context']==before['settings']['context'],'Restoration context differs')
            require(item['restored']['chunk']['blocks_sha256']==before['chunk']['blocks_sha256'],'Restoration changed existing blocks')
            require(item['restored']['region']==before['region'],'Restoration changed region identity')
            require((world/SNAPSHOT).read_bytes()==baseline_bytes,'Restored snapshot rewritten')
            item['restored_snapshot_sha256']=runtime['sha'](world/SNAPSHOT)
            item['logs']={p.name:runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))}
        finally:
            close(server);cleanup_cache(server)
        results['cases'].append(item)
        (args.output/'context-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASSED startup rejection/restoration and continuing-config isolation',flush=True)


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
