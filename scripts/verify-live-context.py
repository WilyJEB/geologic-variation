"""Bounded #9 live seed/scale rejection: four independent disposable servers."""
import argparse
import json
from pathlib import Path
import re
import runpy
import shutil
import gzip
import zlib
import hashlib

helpers=runpy.run_path(str(Path(__file__).with_name('verify-context-startup.py')))
runtime=helpers['runtime']; ROOT=runtime['ROOT']; require=helpers['require']
plain=runpy.run_path(str(Path(__file__).with_name('compare-runtime-chunks.py')))['plain']


def terrain(world):
    """Hash stored section block-state containers; exclude ticks/light/region timestamps."""
    result={}
    for path in sorted((world/'region').glob('*.mca')):
        raw=path.read_bytes()
        for slot in range(1024):
            offset=int.from_bytes(raw[slot*4:slot*4+3],'big')*4096
            if not offset:continue
            size=int.from_bytes(raw[offset:offset+4],'big');codec=raw[offset+4]
            decoded={1:gzip.decompress,2:zlib.decompress,3:lambda b:b}[codec](raw[offset+5:offset+4+size])
            kind,_,value=runtime['nbt_read'](decoded);chunk=plain(kind,value)
            states=[{'Y':s['Y'],'block_states':s.get('block_states')} for s in chunk['sections']]
            result[f'{path.name}:{slot}']={'status':chunk['Status'],'blocks':hashlib.sha256(json.dumps(states,sort_keys=True).encode()).hexdigest()}
    return result


def run(args):
    require(runtime['sha'](args.td)=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8','Expected pinned standalone CPU TD')
    require(runtime['sha'](args.addon)==args.expected_addon_sha256,'Unexpected production addon')
    args.output.mkdir(parents=True,exist_ok=False)
    fixture_manifest={p.relative_to(args.fixture).as_posix():runtime['sha'](p) for p in args.fixture.rglob('*') if p.is_file()}
    model_manifest={p.name:runtime['sha'](p) for p in args.models.iterdir() if p.is_file()}
    results={'cases':[]}
    for field in ('seed','scale'):
        for route in ('cached','uncached'):
            require(shutil.disk_usage(args.output).free>=2*1024**3,'Need 2 GiB free')
            server=runtime['Server'](args,f'{field}-{route}',scale=1,link_td=True)
            world=server.path/'world'
            # Known-provenance, already saved terrain; no user save is launched or edited.
            shutil.copytree(args.fixture,world,dirs_exist_ok=True)
            try:
                server.start()
                before=helpers['observe'](server)
                require('models=64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9' in before['settings']['context'], 'Model pin mismatch')
                require('backend=CPU/Windows 11/amd64' in before['settings']['context'],'Expected CPU baseline')
                server.command('save-all flush')
                original_scale=(world/'data/terrain_diffusion_world_settings.dat').read_bytes()
                preserved=helpers['preserve'](world)
                terrain_before=terrain(world)
                require(any(k.startswith('geologic_variation:') and v>0 for k,v in before['chunk']['counts'].items()),'Empty regional sample')
                # stdin avoids waiting for an RCON response while the fatal latch closes RCON.
                server.process.stdin.write(f'acceptance live-context {field} {route}\n'.encode())
                server.process.stdin.flush()
                server.process.wait(timeout=120)
                server.console.close();helpers['storage_ok'](server)
                text=helpers['log'](server).read_text(errors='replace')
                matches=re.findall(r'LIVE_CONTEXT (\{.*\})',text)
                require(len(matches)==1,'Missing unique live result')
                live=json.loads(matches[0])
                require(live['rejected'] and live['heightmap_calls_after_edit']==0,'Returned stale result or entered heightmap route')
                if args.expected_addon_sha256!='39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226':
                    require('pipeline_data_calls_after_edit' in live,'Candidate requires elevation-entry instrumentation')
                require(live.get('pipeline_data_calls_after_edit',0)==0,'Entered elevation API after edit')
                require(live['cache_entries_before_edit']==(1 if route=='cached' else 0),'Wrong cache precondition')
                require(live['cache_entries_after']==0,'Failure did not clear cache')
                require(live['thread']=='Server thread','Query did not run on server thread')
                match=re.search(r'Saved: GenerationContext\[(.*?)\]; runtime: GenerationContext\[(.*?)\]',text)
                require(match is not None,'Missing contexts')
                saved,current=({k:v for k,v in (part.split('=',1) for part in value.split(', '))} for value in match.groups())
                require([k for k in saved if saved[k]!=current[k]]==[field],'Unexpected context difference')
                require('Restore this world\'s original' in text and 'Stopping server' in text,'Missing diagnostic/shutdown')
                after=helpers['preserve'](world)
                terrain_after=terrain(world)
                require(preserved['snapshot']==after['snapshot'],'Snapshot changed after live rejection')
                require(terrain_before==terrain_after,'Existing block states/status or persisted chunk coverage changed')
                rejection_log=runtime['sha'](helpers['log'](server))
                helpers['cleanup_cache'](server)
                # Restore this disposable world's own captured scale bytes. Seed API is transient;
                # reopening initializes it from unchanged level.dat.
                (world/'data/terrain_diffusion_world_settings.dat').write_bytes(original_scale)
                server.start();restored=helpers['observe'](server);server.stop();helpers['storage_ok'](server)
                require(before['chunk']['blocks_sha256']==restored['chunk']['blocks_sha256'],'Existing blocks changed')
                require(before['region']==restored['region']==live['expected_region'],'Geology changed')
                require(before['settings']==restored['settings'],'Settings/context changed')
                require(helpers['preserve'](world)['snapshot']==preserved['snapshot'],'Snapshot changed on reopen')
                terrain_restored=terrain(world)
                require(terrain_before==terrain_restored,'Restored terrain/status/coverage differs')
                item={'name':server.path.name,'before':before,'live':live,'preserved_before':preserved,
                    'preserved_after_rejection':after,'saved_context':saved,'runtime_context':current,
                    'terrain_before':terrain_before,'terrain_after_rejection':terrain_after,
                    'terrain_restored':terrain_restored,
                    'restored':restored,'exit_code':server.process.returncode,
                    'artifacts':{p.name:runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))},
                    'logs':{'console-1.log':rejection_log,'console-2.log':runtime['sha'](helpers['log'](server))}}
                results['cases'].append(item)
                (args.output/'live-results.json').write_text(json.dumps(results,indent=2)+'\n')
                print('PASSED',server.path.name,flush=True)
            finally:
                try:
                    helpers['close'](server)
                finally:
                    # Only the process launched for this disposable case; retain logs on timeout.
                    if hasattr(server,'process') and server.process.poll() is None:
                        server.process.kill();server.process.wait(timeout=30)
                    if hasattr(server,'console') and not server.console.closed:server.console.close()
                    helpers['cleanup_cache'](server)
    require(fixture_manifest=={p.relative_to(args.fixture).as_posix():runtime['sha'](p) for p in args.fixture.rglob('*') if p.is_file()},'Source fixture changed')
    require(model_manifest=={p.name:runtime['sha'](p) for p in args.models.iterdir() if p.is_file()},'Shared model inputs changed')
    results['shared_inputs_unchanged']=True
    (args.output/'live-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--td',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--fixture',type=Path,required=True,help='Verified disposable matching scale-1 world, copied read-only')
    parser.add_argument('--expected-addon-sha256',default='39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226')
    for name,default in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                         'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                         'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():
        parser.add_argument('--'+name,type=Path,default=ROOT/default)
    args=parser.parse_args()
    for name,value in vars(args).items():
        if isinstance(value,Path):setattr(args,name,value.resolve())
    run(args)
