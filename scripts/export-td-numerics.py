"""Strict raw bit/source/log verification and portable exact comparisons."""
import argparse
import hashlib
import io
import json
import math
import re
from pathlib import Path
import struct
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def floats(raw):return [v[0] for v in struct.iter_unpack('>f',raw)]


def compare(a,b):
    assert len(a)==len(b)
    av,bv=floats(a),floats(b)
    ai=[v[0] for v in struct.iter_unpack('>I',a)];bi=[v[0] for v in struct.iter_unpack('>I',b)]
    differing=[i for i,(x,y) in enumerate(zip(ai,bi)) if x!=y]
    ordered=lambda x: 0xffffffff-x if x&0x80000000 else x+0x80000000
    quantize=lambda x:max(-32768,min(32767,math.floor(x)))
    return dict(exact_equal=not differing,differing_indices=differing,
        maximum_absolute_difference_metres=max(abs(x-y) for x,y in zip(av,bv)),
        maximum_ulp_difference=max(abs(ordered(x)-ordered(y)) for x,y in zip(ai,bi)),
        mean_a=sum(av)/len(av),mean_b=sum(bv)/len(bv),
        relief_a=max(av)-min(av),relief_b=max(bv)-min(bv),
        quantized_differing_indices=[i for i,(x,y) in enumerate(zip(av,bv)) if quantize(x)!=quantize(y)])


def evaluate(read):
    data=json.loads(read('results.json'))
    for name,digest in data['sources'].items():assert sha(read('executed-sources/'+name))==digest, 'Executed source drift '+name
    rows=[];baselines={};mode_baselines={};total=0
    for case in data['cases']:
        assert case['exit_code']==0 and case['snapshot_unchanged']
        assert 'CPU/' in case['settings']['context'] and f"seed={case['seed']}" in case['settings']['context']
        transcript=[]
        for name,digest in case['logs'].items():
            raw_log=read(f"cpu-{case['index']}/{name}");assert sha(raw_log)==digest
            for line in raw_log.decode(errors='replace').splitlines():
                match=re.search(r'ACCEPTANCE (\{.*\})',line)
                if match:transcript.append(json.loads(match.group(1)))
        local={}
        for event in case['events']:
            value=event['result']
            logged={k:v for k,v in value.items() if k!='sha256'}
            assert logged in transcript, 'Result missing from raw transcript'
            assert event['working_set_bytes']<=16*1024**3
            if 'file' not in value:continue
            total+=len(value['requests'])
            x,z=value['col']*256,value['row']*256
            expected={0:[[z,x,z+256,x+256]],1:[[z-1,x-1,z+257,x+257]],
                2:[[z,x,z+128,x+256],[z+128,x,z+256,x+256]],3:[[z,x,z+1,x+1]]}[value['mode']]
            assert value['requests']==expected
            raw=read(f"cpu-{case['index']}/numerical-bits/{value['file']}")
            assert sha(raw)==value['sha256'] and len(raw)==value['samples']*4
            key=(case['seed'],value['row'],value['col'])
            baseline=local.setdefault(key,raw)
            if value['mode']==3:baseline=baseline[:4]
            mode_key=key+(value['mode'],)
            same_mode=mode_baselines.setdefault(mode_key,raw)
            rows.append(dict(case=case['index'],file=value['file'],row=value['row'],col=value['col'],mode=value['mode'],
                requests=value['requests'],sha256=value['sha256'],versus_first_same_process=compare(baseline,raw),
                versus_first_same_mode=compare(same_mode,raw),
                versus_first_process=compare(baselines[key][:len(raw)],raw) if key in baselines else None))
            if value['mode']==0:baselines.setdefault(key,raw)
        assert case['final_metrics']['computed_windows']<=1500
    assert total==data['requests']<=32 and len(data['cases'])<=3 and data['elapsed_seconds']<2400
    assert data['shared_inputs_unchanged']
    return dict(protocol_commit=data['protocol_commit'],base=data['base'],sources=data['sources'],
        exporter_sha256=sha(Path(__file__).read_bytes()),
        artifacts=data['artifacts'],models=data['models'],cases=data['cases'],
        comparisons=rows,direct_requests=total,launches=len(data['cases']),
        elapsed_seconds=data['elapsed_seconds'],shared_inputs_unchanged=True,
        held_out_validation=False,geological_selection='abstain',
        failure_preserved='PR52 Actual matching native support changed remains failed; no tolerance',
        limitation='Small support/context experiment cannot attribute historical scale-paired discrepancies or recreate original large patch context')


def export(source,archive):
    data=json.loads((source/'results.json').read_text())
    for name,digest in data['artifacts'].items():assert sha((ROOT/name).read_bytes())==digest
    # Geometry was corrected OFFLINE after collection. Preserve the exact earlier
    # bytes captured for this experiment; do not relabel them as the revised code.
    import subprocess
    for name,digest in data['sources'].items():
        original=subprocess.check_output(['git','show',data.get('source_commit','56cfca7')+':'+name],cwd=ROOT)
        assert sha(original)==digest==sha((source/'executed-sources'/name).read_bytes())
    result=evaluate(lambda name:(source/name).read_bytes())
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        names=['results.json']+['executed-sources/'+name for name in data['sources']]
        for case in data['cases']:
            prefix=f"cpu-{case['index']}/"
            names += [prefix+n for n in case['logs']]
            names += [prefix+'numerical-bits/'+e['result']['file'] for e in case['events'] if 'file' in e['result']]
        for name in names:
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(source/name).read_bytes(),compresslevel=9)
    result['portable_archive_sha256']=sha(archive.read_bytes())
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(json.dumps(export(a.source,a.archive),indent=2)+'\n')
