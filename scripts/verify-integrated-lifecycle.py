"""Independent packaged integrated-client control/rejection/recovery in one JVM.

Uses only NEW disposable copies. Account files and installed profiles are never read.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import time
import urllib.request

hot=runpy.run_path(str(Path(__file__).with_name('verify-hot-config.py')))
h=hot['h']; r=h['runtime']; require=h['require']; ROOT=r['ROOT']
model=runpy.run_path(str(Path(__file__).with_name('verify-model-config.py')))


def run(a):
    require(r['sha'](a.td)==model['CPU'],'CPU artifact pin')
    require(r['sha'](a.addon)==a.expected_addon_sha256,'Production addon pin mismatch')
    source=hot['manifest'](a.fixture)
    require(source[h['SNAPSHOT'].as_posix()]=='c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d','Unverified source')
    shared={p.name:r['sha'](p) for p in a.models.iterdir() if p.is_file()}
    free=shutil.disk_usage(a.output.parent).free
    require(free>=2*1024**3,'Need 2 GiB before launch')
    launcher=[sys.executable,str(ROOT/'scripts/launch-acceptance-client.py')]
    for name in ('manifest','meta','java','addon','td','output','models','probe'):
        launcher+=['--'+name,str(getattr(a,name))]
    launcher+=['--integrated','--timeout','1800']
    parentlog=a.output.parent/(a.output.name+'-launcher.log')
    sources=['scripts/verify-integrated-lifecycle.py','scripts/launch-acceptance-client.py',
             'src/runtimeProbe/java/dev/wilyjeb/geology/probe/IntegratedLifecycle.java',
             'src/runtimeProbe/java/dev/wilyjeb/geology/probe/mixin/IntegratedClientProbeMixin.java',
             'src/main/java/dev/wilyjeb/geology/mixin/ExplorerCleanupMixin.java','src/main/resources/geologic_variation.mixins.json']
    result={'source_baseline':'32ab500e99387239128b16f60d7ab9138810e734','free_bytes_before_launch':free,'steps':[],
            'source_sha256':{p:r['sha'](ROOT/p) for p in sources},'source_fixture':source,
            'shared_inputs':shared,'addon_sha256':r['sha'](a.addon),'probe_sha256':r['sha'](a.probe),
            'td_sha256':r['sha'](a.td),'launcher_manifest_sha256':r['sha'](a.manifest)}
    log=parentlog.open('w'); process=subprocess.Popen(launcher,stdout=log,stderr=subprocess.STDOUT)
    def text():
        p=a.output/'console.log'; return p.read_text(errors='replace') if p.exists() else ''
    def bridge(command,timeout=300):
        require(process.poll() is None,'Client launcher exited: '+text()[-3000:])
        response=a.output/'bridge-response.json'; response.unlink(missing_ok=True)
        tmp=a.output/'request.tmp'; tmp.write_text(command)
        tmp.replace(a.output/'bridge-request.txt')
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            require(process.poll() is None,'Client exited: '+text()[-3000:])
            if response.exists():
                data=json.loads(response.read_text()); require('error' not in data,str(data)); return data
            time.sleep(.1)
        raise RuntimeError('Bounded bridge timeout: '+command)
    def wait_state(predicate,timeout=90):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            s=bridge('state',max(1,end-time.monotonic()))
            if predicate(s): return s
            time.sleep(.2)
        raise RuntimeError('Bounded state timeout: '+str(s))
    def command(cmd):
        cursor=len(text()); bridge('command '+cmd)
        matches=re.findall(r'ACCEPTANCE (\{.*\})',text()[cursor:])
        return json.loads(matches[0]) if matches else None
    def state(world):
        return {'preserved':h['preserve'](world),'terrain':hot['live']['terrain'](world),
                'snapshot_fields':model['snapshot'](world/h['SNAPSHOT'])}
    def inputs():
        return {'mods':hot['manifest'](a.output/'mods'),'config':hot['manifest'](a.output/'config'),
                'models':{k:r['sha'](a.output/'terrain-diffusion-models'/k) for k in shared}}
    def stopped():
        s=wait_state(lambda s:not any(s['server_threads_alive']) and s['previous_shutdown'] and s['client_server_null']
                     and not any(t['name'] in ('terrain-explorer-http','HTTP-Dispatcher') for t in s['td_threads']),30)
        require(s['owner_null'] and s['active_null'] and s['context_null'] and s['geology_cache']==0,'Geology state leaked')
        require(not s['explorer_running'] and s['explorer_port']==-1 and s['td_pending']==0,'TD resources remain busy')
        return s
    def open_world(name,reject=False):
        cursor=len(text()); start=time.monotonic(); s=bridge('open '+name,360)
        if s['screen'].endswith('BackupConfirmScreen'): s=bridge('confirm',360)
        if reject:
            s=wait_state(lambda s:s['screen'].endswith('DisconnectedScreen'))
        else:
            s=wait_state(lambda s:s['joined'],360)
            require(s['tick_frozen'],'Integrated server was not frozen before joining')
            require(s['geology_cache']==0 and s['td_pending']==0,'World starts with stale geology/inference work')
        return s,text()[cursor:],time.monotonic()-start
    try:
        end=time.monotonic()+180
        while time.monotonic()<end and 'client-pid.txt' not in [p.name for p in a.output.glob('*')]:
            require(process.poll() is None,parentlog.read_text()); time.sleep(.25)
        wait_state(lambda s:s['screen'].endswith('TitleScreen'),180)
        result['pid']=int((a.output/'client-pid.txt').read_text())
        saves=a.output/'saves'; saves.mkdir(exist_ok=True)
        for name in ('control','rejected'):
            world=saves/name; shutil.copytree(a.fixture,world)
            # Ordinary disposable metadata setup, applied equally before the control.
            path=world/'level.dat'; tag=r['nbt_read'](gzip.decompress(path.read_bytes())); d=tag[2]['Data'][1]
            d['GameRules'][1]['spectatorsGenerateChunks']=(8,'false')
            d['GameRules'][1]['spawnRadius']=(8,'0')
            d['SpawnX']=(3,-508); d['SpawnY']=(3,200); d['SpawnZ']=(3,-1027)
            d['Player']=(10,{'Pos':(9,(6,[-508.5,200.,-1027.5])), 'Rotation':(9,(5,[0.,0.])),
                            'Dimension':(8,'minecraft:overworld'),'playerGameType':(3,3)})
            path.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
        baseline=state(saves/'control')
        s,raw,elapsed=open_world('control')
        command('tick freeze')
        before={'settings':command('acceptance settings'),'chunk':command('acceptance chunk overworld -32 -65'),
                'region':command('acceptance region -508 -1027')}
        command('td-explore')
        explorer=bridge('state'); require(explorer['explorer_running'],'Explorer did not start')
        bridge('disconnect',90)
        control_stopped=stopped(); control=state(saves/'control')
        original_inputs=inputs()
        result['steps'].append({'name':'control','state':s,'observed':before,'stopped':control_stopped,'elapsed':elapsed})
        require(control['terrain']==baseline['terrain'],'Client control altered persisted terrain; inspect before acceptance')
        # Base rejection on the independently observed client control, including exact frozen save metadata.
        shutil.copytree(saves/'control',saves/'rejected',dirs_exist_ok=True)
        world=saves/'rejected'; original=state(world)
        path,original_bytes=world/'level.dat',(world/'level.dat').read_bytes()
        tag=r['nbt_read'](gzip.decompress(original_bytes)); d=tag[2]['Data'][1]
        seed=d['WorldGenSettings'][1]['seed'][1]; d['WorldGenSettings'][1]['seed']=(4,seed+1)
        path.write_bytes(gzip.compress(r['nbt_write'](tag),mtime=0))
        result['seed_input_hashes']={'original':hashlib.sha256(original_bytes).hexdigest(),'alternate':r['sha'](path)}
        explorer=bridge('explorer')
        with urllib.request.urlopen(f"http://127.0.0.1:{explorer['explorer_port']}/api/status",timeout=10) as response:
            result['explorer_before_rejection']=json.load(response)
        result['explorer_before_rejection_state']=bridge('state')
        s,raw,elapsed=open_world('rejected',True)
        require('Geologic Variation stopped this world' in s['narration']
                and f'seed (saved={seed}, runtime={seed+1})' in s['narration']
                and 'Restore the original installation and world inputs.' in s['narration']
                and 'Do not edit or delete the geology snapshot.' in s['narration'],'Unreadable recovery UI')
        match=re.search(r'Saved: GenerationContext\[(.*?)\]; runtime: GenerationContext\[(.*?)\]',raw)
        require(match is not None,'Missing full rejection contexts')
        saved,current=[model['context']('GenerationContext['+v+']') for v in match.groups()]
        require(current=={**saved,'seed':str(seed+1)},'Unexpected context differences')
        require('Done (' not in raw and 'caller=addon-anchor' not in raw,'Rejection after generation/Ready')
        require(s['td_seed']==seed+1,'TD did not initialize alternate seed')
        bridge('screenshot'); time.sleep(.5)
        rejected_stopped=stopped(); rejected=state(world)
        require(rejected==original,'Rejection changed snapshot/regions/terrain')
        result['steps'].append({'name':'rejection','state':s,'saved_context':saved,'runtime_context':current,
                                'stopped':rejected_stopped,'elapsed':elapsed,'log':raw})
        # Leave original rejected inputs incompatible while independently opening the compatible world.
        s,raw,elapsed=open_world('control')
        after={'settings':command('acceptance settings'),'chunk':command('acceptance chunk overworld -32 -65'),
               'region':command('acceptance region -508 -1027')}
        bridge('disconnect',90)
        result['steps'].append({'name':'next-compatible','state':s,'observed':after,'stopped':stopped(),'elapsed':elapsed})
        control_final=state(saves/'control')
        require(control_final['terrain']==control['terrain'] and control_final['preserved']['snapshot']==control['preserved']['snapshot'],'Next compatible world altered stored terrain/snapshot')
        path.write_bytes(original_bytes); require(path.read_bytes()==original_bytes,'Restoration bytes')
        result['seed_input_hashes']['restored']=r['sha'](path)
        require(inputs()==original_inputs,'Original installation inputs not restored')
        s,raw,elapsed=open_world('rejected')
        reopened={'settings':command('acceptance settings'),'chunk':command('acceptance chunk overworld -32 -65'),
                  'region':command('acceptance region -508 -1027')}
        bridge('disconnect',90)
        result['steps'].append({'name':'restored-reopen','state':s,'observed':reopened,'stopped':stopped(),'elapsed':elapsed})
        for item in (after,reopened):
            require(item['settings']==before['settings'],'Settings/context ownership changed')
            require(item['chunk']['blocks_sha256']==before['chunk']['blocks_sha256'] and item['chunk']['counts']==before['chunk']['counts'],'Sample changed')
            require(item['region']['region']==before['region']['region'],'Geology changed')
        final=state(world)
        require(original['terrain']==final['terrain'] and original['preserved']['snapshot']==final['preserved']['snapshot'],'Restored terrain/snapshot changed')
        require(all(item['state']['pid']==result['pid'] for item in result['steps']),'JVM changed')
        require(len(set(result['steps'][-1]['state']['server_ids']))==4,'Reused server ownership')
        result.update(original=original,rejected=rejected,final=final,source_unchanged=hot['manifest'](a.fixture)==source,
                      shared_unchanged=shared=={p.name:r['sha'](p) for p in a.models.iterdir() if p.is_file()})
        require(result['source_unchanged'] and result['shared_unchanged'],'Source/shared mutation')
        require(inputs()==original_inputs,'Installation inputs changed during recovery')
        result.update(original_inputs=original_inputs,inputs_exactly_restored=True,control_before=control,control_final=control_final)
        require(result['source_sha256']=={p:r['sha'](ROOT/p) for p in sources},'Executed tooling changed during run')
        for p in sources:
            target=a.output/'executed-sources'/p; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/p,target)
        bridge('quit'); process.wait(timeout=90); require(process.returncode==0,'Nonzero client exit')
        result['exit_code']=process.returncode;result['console_sha256']=r['sha'](a.output/'console.log')
        (a.output/'integrated-results.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASSED independent integrated same-process matrix',flush=True)
    finally:
        if process.poll() is None:
            try: bridge('quit',10); process.wait(timeout=90)
            except Exception:
                # Kill only the recorded disposable child, never a name-wide process set.
                if (a.output/'client-pid.txt').exists():
                    subprocess.run(['taskkill','/PID',(a.output/'client-pid.txt').read_text(),'/T','/F'],timeout=30,capture_output=True)
                process.kill(); process.wait(timeout=30)
        log.close()
        cache=(a.output/'terrain-diffusion-models/onnx-cache').resolve()
        require(cache.is_relative_to(a.output.resolve()),'Cache outside disposable case')
        # The launcher waits for its only Java child, or the bounded fallback terminates that exact PID.
        if process.returncode == 0 and cache.exists(): shutil.rmtree(cache)
        (a.output/'partial-results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','manifest','meta','output'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--fixture',type=Path,default=ROOT/'runs/acceptance/context-startup-2026-11-01-02/baseline/world')
    p.add_argument('--models',type=Path,default=ROOT/'runs/server/terrain-diffusion-models')
    p.add_argument('--addon',type=Path,default=ROOT/'build/libs/geologic-variation-0.2.2-dev.jar')
    p.add_argument('--probe',type=Path,default=ROOT/'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar')
    p.add_argument('--expected-addon-sha256',default='39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226')
    a=p.parse_args()
    for k,v in vars(a).items():
        if isinstance(v,Path): setattr(a,k,v.resolve())
    run(a)
