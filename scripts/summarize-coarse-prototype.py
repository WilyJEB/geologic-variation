"""Validate raw #11 prototype evidence and export portable paired measurements."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import statistics
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value: raise RuntimeError(message)


def export(source):
    data=json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'],'Missing preservation checks')
    for name,digest in data['sources'].items():
        require(sha(Path(__file__).with_name(name))==digest,'Executed source changed: '+name)
    for case in data['cases']:
        for name,digest in case['logs'].items():
            require(sha(source/case['name']/name)==digest,'Raw log changed')
        require(case['exit_code']==0 and case['terrain_unchanged'] and case['persisted_records']>0,'Incomplete reopen')
        require(case['sample']['blocks_sha256']==case['reopened']['blocks_sha256'],'Reopen blocks changed')
        require(all(v==0 for row in case['warm'] for v in row['delta'].values()),'Cache hit scheduled TD work')
        if 'suite' in case:
            require(case['suite']['concurrent_requests']==1 and case['suite']['real_cache_entries']==128
                and case['suite']['traversal_equal'] and case['suite']['evicted_recomputed'],'Bounded determinism failed')
            require(case['contract']['equal'],'Signal oracle failed')
    rejection=data['generator_rejection']
    require(rejection['changed_context_fields']==['generator'] and not rejection['ready'],'Wrong generator rejection')
    require(data['generator_restoration']['terrain_snapshot_unchanged'],'Incomplete restoration')
    for name,digest in data['generator_restoration']['logs'].items():
        require(sha(source/'generator-boundary'/name)==digest,'Generator raw log changed')
    pairs=[]
    for scale,trial in sorted({(c['scale'],c['trial']) for c in data['cases']}):
        rows={c['arm']:c for c in data['cases'] if (c['scale'],c['trial'])==(scale,trial)}
        require(set(rows)=={'current','coarse'},'Incomplete pair')
        pairs.append({'scale':scale,'trial':trial,
            'current_ms':rows['current']['cold']['ms'],'coarse_ms':rows['coarse']['cold']['ms'],
            'paired_saving_ms':rows['current']['cold']['ms']-rows['coarse']['cold']['ms'],
            'current_delta':rows['current']['cold']['delta'],'coarse_delta':rows['coarse']['cold']['delta']})
    data=copy.deepcopy(data)
    data['raw_results_sha256']=sha(source/'results.json');data['pairs']=pairs
    data['scale1_median_paired_saving_ms']=statistics.median(p['paired_saving_ms'] for p in pairs if p['scale']==1)
    data['warm_medians_ms']={c['name']:statistics.median(row['ms'] for row in c['warm']) for c in data['cases']}
    def scrub(value):
        if isinstance(value,dict):return {k:scrub(v) for k,v in value.items() if k!='addon_origin'}
        if isinstance(value,list):return [scrub(v) for v in value]
        return value
    return scrub(data)


def cold_export(source):
    data=json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'],'Cold inputs changed')
    for name,digest in data['sources'].items():
        require(sha(Path(__file__).with_name(name))==digest,'Cold executed source changed')
    for case in data['cases']:
        require(case['cold']['delta']['computed_windows']>0 and case['exit_code']==0,'Cold work incomplete')
        require(case['environment']['backend']=='CPU','Wrong backend')
        for name,digest in case['logs'].items():require(sha(source/case['name']/name)==digest,'Cold raw log changed')
        require(all(v==0 for row in case['warm'] for v in row['delta'].values()),'Cold fixture warm query did TD work')
    pairs=[]
    for trial in range(3):
        rows={c['arm']:c for c in data['cases'] if c['trial']==trial}
        require(set(rows)=={'current','coarse'},'Missing cold pair')
        pairs.append({'trial':trial,'current_ms':rows['current']['cold']['ms'],'coarse_ms':rows['coarse']['cold']['ms'],
            'paired_saving_ms':rows['current']['cold']['ms']-rows['coarse']['cold']['ms'],
            'current_delta':rows['current']['cold']['delta'],'coarse_delta':rows['coarse']['cold']['delta']})
    data['pairs']=pairs;data['median_paired_saving_ms']=statistics.median(v['paired_saving_ms'] for v in pairs)
    data['raw_results_sha256']=sha(source/'results.json')
    return data


def production_comparison(source, baseline):
    data=json.loads((source/'results.json').read_text())
    case=data['cases'][0]
    name=next(n for n in case['artifacts'] if n.startswith('geologic-variation-'))
    addon=source/case['name']/'mods'/name
    require(sha(baseline)=='6f1a143a8b117abdabdfd1c72270d5270c19e18f7920a7df3aab908d3f6ec1ae','Expected retained PR #46 baseline')
    with zipfile.ZipFile(baseline) as old,zipfile.ZipFile(addon) as new:
        classes=[n for n in old.namelist() if n.endswith('.class')]
        require(all(old.read(n)==new.read(n) for n in classes),'Existing production class changed')
        added=[n for n in new.namelist() if n.endswith('.class') and n not in classes]
        require(added==['dev/wilyjeb/geology/domain/CoarseEvidence.class'],'Unexpected production addition')
    alternate=source/'generator-boundary.jar'
    require(sha(alternate)==data['alternate']['sha256'],'Alternate artifact changed')
    with zipfile.ZipFile(addon) as original,zipfile.ZipFile(alternate) as changed:
        require(original.namelist()==changed.namelist(),'Alternate entries changed')
        changed_names=[]
        for n in original.namelist():
            before=original.read(n);after=changed.read(n)
            if before!=after:
                require(n.endswith('.class') and before.replace(b'\x01\x00\x09geology-1',b'\x01\x00\x11coarse-evidence-1')==after,
                    'Alternate changed more than generator constants')
                changed_names.append(n)
        require(changed_names==data['alternate']['changed_classes'],'Alternate class record changed')
    return {'baseline_sha256':sha(baseline),'addon_sha256':sha(addon),'unchanged_existing_classes':len(classes),
        'added_classes':added,'alternate_only_generator_constants':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('--cold',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    args=p.parse_args()
    data=export(args.source);data['far_cold']=cold_export(args.cold)
    data['production_comparison']=production_comparison(args.source,args.baseline)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
