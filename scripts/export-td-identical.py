"""Strict transcript, exact-array, source and bounded comparison export."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
n=runpy.run_path(str(ROOT/'scripts/export-td-numerics.py'))
c=runpy.run_path(str(ROOT/'scripts/collect-td-identical.py'))
sha=n['sha'];compare=n['compare']


def evaluate(read):
    data=json.loads(read('results.json'))
    assert data['base']=='1c31c0f'
    assert data['launch_attempts']==len(data['cases'])<=4
    assert data['direct_request_attempts']<=26
    assert data['elapsed_seconds']<1800 and not data['monitor_failures']
    assert data['shared_inputs_unchanged']
    for name,digest in data['sources'].items():assert sha(read('executed-sources/'+name))==digest
    assert sha(read('provider-javap.txt'))==data['provider_javap_sha256']
    behavior=read('provider-javap.txt').decode().split('public static void clearCache();')[1].split('public static long getSeed')[0]
    assert 'Field CACHE:' in behavior and 'Field PENDING:' in behavior and 'pipeline' not in behavior
    arrays={};requests=0;total_windows=0;rows=[];states=[]
    for case in data['cases']:
        i=case['index'];prefix=f'cpu-{i}/'
        assert 'failure' not in case and case['exit_code']==0 and case['snapshot_unchanged']
        assert case['scale']==(6 if i==3 else 1) and case['seed']==-2026110411
        assert 'CPU/Windows' in case['settings']['context'] and f"scale={case['scale']}" in case['settings']['context']
        assert case['planned_sequence']==c['sequence'](i)
        actual=[e['command'] for e in case['events'] if e['command'].startswith('acceptance numeric')][1:]
        assert actual==case['planned_sequence']
        transcript=[]
        for name,digest in case['logs'].items():
            raw=read(prefix+name);assert sha(raw)==digest
            for line in raw.decode(errors='replace').splitlines():
                m=re.search(r'ACCEPTANCE (\{.*\})',line)
                if m:transcript.append(json.loads(m.group(1)))
        for name,digest in case['config'].items():assert sha(read(prefix+'config/'+name))==digest
        assert sha(read(prefix+'launch-args.txt'))==case['launch_args_sha256']
        values=[]
        for event in case['events']:
            value=event['result'];logged={k:v for k,v in value.items() if k!='sha256'}
            assert logged in transcript,'Missing transcript result'
            if 'computed_windows' in value:assert value['computed_windows']<=1500
            if 'action' in value:states.append(dict(case=i,**value))
            if 'file' not in value:continue
            requests+=1;col=value['col'];row=value['row'];x,z=col*256,row*256
            assert row==-14 and col in (-6,6) and value['seed']==-2026110411
            assert value['mode']==0 and value['samples']==65536 and value['requests']==[[z,x,z+256,x+256]]
            raw=read(prefix+'numerical-bits/'+value['file'])
            assert len(raw)==262144 and sha(raw)==value['sha256']
            # Compare checks all finite decoded values via exact retained baseline.
            assert all(__import__('math').isfinite(v) for v in n['floats'](raw))
            key=(i,len(values));arrays[key]=raw;values.append(value)
            rows.append(dict(case=i,position=key[1],command=event['command'],**value))
        assert len(values)==(14 if i==0 else 4)
        assert case['initial_metrics']['pipeline_data_calls']==0
        assert case['final_metrics']['pipeline_data_calls']==len(values)
        assert case['final_metrics']['heightmap_calls']==0
        assert case['initial_metrics']['coarse_calls']==case['final_metrics']['coarse_calls']==1
        counters=[e['result'] for e in case['events'] if e['command']=='acceptance metrics']
        for left,right in zip(counters,counters[1:]):
            assert all(right[k]>=left[k] for k in left),'Counter reversal'
        total_windows+=case['final_metrics']['computed_windows']
    assert requests==data['direct_request_attempts']==26 and total_windows<=6000
    assert all(s['working_set_bytes']<=16*1024**3 for s in data['memory_samples'])
    assert data['memory_samples']
    # Require genuine populated diagnostic cache and isolated clear, with unchanged order.
    dc=next(s for s in states if s['action']=='diagnostic-clear')
    pc=next(s for s in states if s['action']=='provider-clear')
    assert dc['fine_before']==2 and dc['fine_after']==0
    assert pc['fine_before']==pc['fine_after']==0 and pc['provider_after']==0 and pc['pending']==0
    comparisons=[]
    def pair(label,left,right):
        assert rows[next(j for j,r in enumerate(rows) if (r['case'],r['position'])==left)]['col']==rows[next(j for j,r in enumerate(rows) if (r['case'],r['position'])==right)]['col']
        comparisons.append(dict(factor=label,reference=list(left),intervention=list(right),**compare(arrays[left],arrays[right])))
    for p in (0,1):
        for i in range(4):pair('same-process repeated identical read',(i,p),(i,p+2))
        pair('fresh process same order/scale',(0,p),(1,p))
        pair('request order only versus fresh repeat',(1,p),(2,1-p))
        pair('scale only versus fresh repeat',(1,p),(3,p))
        pair('real diagnostic cache population',(0,p),(0,p+4))
        pair('diagnostic clear only',(0,p+6),(0,p+8))
        pair('no-clear temporal control',(0,p+8),(0,p+10))
        pair('provider public clear only (tensor store unchanged)',(0,p+10),(0,p+12))
    # Reuse full PR53 bits. No new halo/batch execution.
    with zipfile.ZipFile(ROOT/'docs/evidence/td-numerics.zip') as old:
        olddata=json.loads(old.read('results.json'))
        reuse=[]
        for p,col in enumerate((-6,6)):
            event=next(e for e in olddata['cases'][0]['events'] if e['result'].get('mode')==0 and e['result'].get('col')==col)
            raw=old.read('cpu-0/numerical-bits/'+event['result']['file'])
            assert sha(raw)==event['result']['sha256']
            reuse.append(dict(col=col,pr53_sha256=sha(raw),comparison=compare(raw,arrays[(0,p)])))
    historical=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text())['frozen_matched_native_assertion']['mismatches']
    history=[]
    for col in (-6,6):
        old=next(x for x in historical if x['left']['col']==col)
        for row in rows:
            if row['col']==col:history.append(dict(case=row['case'],position=row['position'],col=col,
                old_scale1_sha256=old['left']['float_sha256'],old_scale6_sha256=old['right']['float_sha256'],
                matches_old_scale1=row['sha256']==old['left']['float_sha256'],matches_old_scale6=row['sha256']==old['right']['float_sha256'],
                historical_indices_and_ulps=None))
    return dict(base=data['base'],source_commit=data['source_commit'],sources=data['sources'],artifacts=data['artifacts'],
        retained_inputs={name:sha((ROOT/name).read_bytes()) for name in
            ('docs/evidence/td-numerics.zip','docs/evidence/td-tracking-negative.json')},
        exporter_sha256=sha(Path(__file__).read_bytes()),cases=data['cases'],arrays=rows,comparisons=comparisons,
        reused_pr53=reuse,historical_hashes=history,launches=data['launch_attempts'],direct_requests=requests,
        unique_native_supports=2,computed_windows_including_startup=total_windows,
        startup_windows=sum(x['initial_metrics']['computed_windows'] for x in data['cases']),
        elapsed_seconds=data['elapsed_seconds'],sampled_peak_working_set=max(s['working_set_bytes'] for s in data['memory_samples']),
        shared_inputs_unchanged=True,fresh_validation=False,geological_selection='abstain',
        historical_cause='unresolved; no historical full arrays',corner='unresolved; no new corner query',
        failure_preserved='PR51 Paired coarse drift and PR52 Actual matching native support changed remain failed')


def export(source,archive):
    data=json.loads((source/'results.json').read_text())
    # Verify immutable executed copies, not a subsequently rebuilt probe output.
    for name,digest in data['artifacts'].items():
        for case in data['cases']:
            assert sha((source/f"cpu-{case['index']}"/'mods'/Path(name).name).read_bytes())==digest
    for name,digest in data['sources'].items():
        # Exact Windows checkout bytes, including Git's configured CRLF conversion
        # for older unpinned helpers; the archive retains those bytes verbatim.
        assert sha(subprocess.check_output(['git','cat-file','--filters',data['source_commit']+':'+name],cwd=ROOT))==digest,name
    result=evaluate(lambda n:(source/n).read_bytes())
    names=['results.json','provider-javap.txt']+['executed-sources/'+n for n in data['sources']]
    for case in data['cases']:
        prefix=f"cpu-{case['index']}/"
        names += [prefix+n for n in case['logs']]+[prefix+'launch-args.txt']
        names += [prefix+'config/'+n for n in case['config']]
        names += [prefix+'numerical-bits/'+e['result']['file'] for e in case['events'] if 'file' in e['result']]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(set(names)):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(source/name).read_bytes(),compresslevel=9)
    result['archive_sha256']=sha(archive.read_bytes())
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.write_text(json.dumps(export(args.source,args.archive),indent=2)+'\n')
