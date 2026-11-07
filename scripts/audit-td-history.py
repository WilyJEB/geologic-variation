"""Offline reconstruction of public requests, not unobserved tensor execution."""
import hashlib
import json
from collections import OrderedDict
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'runs/acceptance/td-tracking-2026-11-04-04'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def reconstruct(case):
    coarse, fine = OrderedDict(), OrderedDict()
    ledger, targets = [], []
    patches = None
    def request(event, role, api, bounds, **extra):
        ledger.append(dict(ordinal=len(ledger), event=event, role=role, api=api,
                           bounds=bounds, **extra))
    def cached(cache, key):
        hit = key in cache
        cache[key] = True
        cache.move_to_end(key)
        if len(cache) > 128:
            cache.popitem(last=False)
        return hit
    def sample(event, value, role):
        row, col = value['row'], value['col']
        if not cached(coarse, (row,col)):
            request(event, role, 'getPipelineCoarse', [row-1,col-1,row+2,col+2])
    for i, event in enumerate(case['events']):
        cmd, value = event['command'], event['result']
        if cmd == 'acceptance sampling-clear':
            fine.clear(); coarse.clear()
        elif cmd == 'acceptance track-clear':
            patches = None
        elif cmd.startswith('acceptance coarse '):
            sample(i, value, 'coarse command')
        elif cmd.startswith('acceptance track-patch '):
            col,row,band = map(int,cmd.split()[-3:])
            miss = patches != (row,col)
            assert miss == value['public_data_miss']
            if miss:
                z,x = row*256-1408,col*256-1408
                request(i,'patch', 'getPipelineData',[z,x,z+3073,x+3073],withClimate=False)
            patches = row,col
        elif cmd.startswith('acceptance sampling-compare '):
            before = len(ledger)
            for policy in ('province_anchor','target','fixed_grid_4'):
                p = value['policies'][policy]
                sample(i,p['coarse'],policy)
                cell = p['matched_native_cell']; row,col = cell['row'],cell['col']
                if not cached(fine,(row,col)):
                    request(i,policy,'getPipelineData',[row*256,col*256,(row+1)*256,(col+1)*256],
                            withClimate=False, float_sha256=cell['float_sha256'])
                    if row == -14 and col in (-6,6):
                        targets.append(dict(col=col,event=i,ordinal=len(ledger)-1,command=cmd,
                                            policy=policy,cell=cell))
            for role in ('target_fine_tile','anchor_fine_tile'):
                tile=value[role]; x,z=tile['x0'],tile['z0']
                api='getPipelineData' if case['scale']==1 else 'fetchHeightmap'
                request(i,role,api,[z,x,z+256,x+256],**({'withClimate':False} if case['scale']==1 else {}))
            actual = ledger[before:]
            # Independently retained counters check cache reconstruction per command.
            for api,counter in [('getPipelineCoarse','coarse_calls'),('getPipelineData','pipeline_data_calls'),
                                ('fetchHeightmap','heightmap_calls')]:
                assert sum(r['api']==api for r in actual)==value['delta'][counter], (i,api)
            if {t['col'] for t in targets} == {-6,6}:
                break
    assert {t['col'] for t in targets} == {-6,6}
    return dict(scale=case['scale'],initial_metrics=case['initial_metrics'],
                events_through_last_target=case['events'][:i+1],requests=ledger,targets=targets,
                startup_request_trace=None,internal_batch_trace=None,internal_evictions=None,
                note='Exact public prefix inferred from frozen sources and checked deltas; fetchHeightmap internals and startup not invented')


def evaluate(read):
    raw=json.loads(read('pr52-results.json'))
    cases=[reconstruct(c) for c in raw['cases'] if c['seed']==-2026110411]
    assert len(cases)==2
    return dict(cases=cases,new_td_launches=0,historical_indices_and_ulps=None,
                historical_assertion_passed=False,geometry_adoption=False,
                all_inspected_analytical_controls='development for any revision')


def export():
    contents={'pr52-results.json':(RAW/'results.json').read_bytes(),
              'pinned-tensor-javap.txt':(ROOT/'runs/acceptance/td-history-pinned-javap.txt').read_bytes()}
    for label,folder in [('pr53','td-numerics-2026-11-04-02'),('pr54','td-identical-2026-11-04-01')]:
        contents[label+'-results.json']=(ROOT/'runs/acceptance'/folder/'results.json').read_bytes()
    provider=ROOT/'runs/acceptance/td-identical-2026-11-04-01'
    contents['pinned-provider-javap.txt']=(provider/'provider-javap.txt').read_bytes()
    jar=provider/'cpu-0/mods/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar'
    assert sha(jar.read_bytes())=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8'
    raw=json.loads(contents['pr52-results.json'])
    for c in raw['cases']:
        if c['seed']!=-2026110411: continue
        for name,digest in c['logs'].items():
            data=(RAW/c['name']/name).read_bytes(); assert sha(data)==digest
            contents[c['name']+'/'+name]=data
    for name in ('scripts/audit-td-history.py','src/runtimeProbe/java/dev/wilyjeb/geology/probe/SamplingDiagnostic.java',
                 'src/runtimeProbe/java/dev/wilyjeb/geology/probe/CoarseSampler.java',
                 'src/runtimeProbe/java/dev/wilyjeb/geology/probe/TrackingPatch.java'):
        data=(ROOT/name).read_bytes()
        if name in raw['sources']: assert sha(data)==raw['sources'][name],name
        contents['sources/'+name]=data
    result=evaluate(contents.__getitem__)
    contents['reconstruction.json']=(json.dumps(result,indent=2)+'\n').encode()
    path=ROOT/'docs/evidence/td-observation-history.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(contents.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)
    summary=dict(archive_sha256=sha(path.read_bytes()),members={n:sha(d) for n,d in contents.items()},
                 new_td_launches=0,cases=[dict(scale=c['scale'],targets=c['targets'],
                 public_prefix_requests=len(c['requests']),
                 patch_requests=sum(r['role']=='patch' for r in c['requests'])) for c in result['cases']])
    (ROOT/'docs/evidence/td-observation-history.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    print(json.dumps(export(),indent=2))
