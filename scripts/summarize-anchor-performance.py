"""Validate local raw trials and export portable #11 measurements without credentials."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import statistics
import runpy


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value: raise RuntimeError(message)


def load(source, exclude):
    data=json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'],'Input preservation incomplete')
    rows=[]
    for c in data['cases']:
        if c['trial'] in exclude: continue
        for name,digest in c['logs'].items():
            require(sha(source/f"t{c['trial']}-{c['arm']}"/name)==digest,'Raw log changed')
        require(any(name.startswith('NeoForge-terrain-diffusion') and digest=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8' for name,digest in c['artifacts'].items()),'CPU artifact changed')
        require(c['exit_code']==0,'Process failed')
        text=(source/f"t{c['trial']}-{c['arm']}"/'console-1.log').read_text(errors='replace')
        # Stop at the fourth cold-route chunk response, before later cold-query probes.
        last=c['chunks'][-1]['value']
        marker=f'"x":{last["x"]},"z":{last["z"]},"generation_ms"'
        require(text.count(marker)>=1,'Missing route end')
        route=text[:text.index(marker)]
        c=copy.deepcopy(c)
        c['route_ms']=sum(v['value']['generation_ms'] for v in c['chunks'])
        c['route_counters']={k:sum(v['delta'][k] for v in c['chunks']) for k in c['chunks'][0]['delta']}
        c['route_uncached_rectangles']=[list(map(int,m)) for m in re.findall(r'uncached region requested: \((-?\d+), (-?\d+)\)-\((-?\d+), (-?\d+)\)',route)]
        if c['arm']!='td':
            require(c['snapshot_before']==c['snapshot_after'],'Snapshot changed')
            require(c['terrain_before']==c['terrain_after'] and c['terrain_before'],'Saved terrain changed')
            require([v['value']['blocks_sha256'] for v in c['chunks']]==[v['blocks_sha256'] for v in c['reopened']],'Reopen complete blocks changed')
            require(all(any(k.startswith('geologic_variation:') and n>0 for k,n in v['value']['counts'].items()) for v in c['chunks']),'Empty regional samples')
            c['persisted_terrain']={'records':len(c['terrain_before']),'status_block_containers_coverage_sha256':hashlib.sha256(json.dumps(c['terrain_before'],sort_keys=True).encode()).hexdigest(),'unchanged_on_reopen':True}
        c.pop('terrain_before',None);c.pop('terrain_after',None)
        def scrub(v):
            if isinstance(v,dict): return {k:scrub(x) for k,x in v.items() if k!='addon_origin'}
            if isinstance(v,list): return [scrub(x) for x in v]
            return v
        rows.append(scrub(c))
    return {'raw_results_sha256':sha(source/'results.json'),'executed_sources':data.get('sources',{}),
            'models':data['models'],'shared_inputs_unchanged':True,'cases':rows}


def export(sources,candidate,sampler,exclude_first):
    candidate_path=candidate
    compare=runpy.run_path(str(Path(__file__).with_name('compare-runtime-chunks.py')))['compare']
    baseline=[load(path,set(exclude_first) if index==0 else set()) for index,path in enumerate(sources)]
    candidate=load(candidate,set())
    oldrows=[c for d in baseline for c in d['cases']]
    pairs=[]
    for trial in sorted({c['trial'] for c in oldrows}):
        rows={c['arm']:c for c in oldrows if c['trial']==trial}
        require(set(rows)=={'td','old'},'Incomplete baseline pair')
        pairs.append({'trial':trial,'td_ms':rows['td']['route_ms'],'old_ms':rows['old']['route_ms'],'added_ms':rows['old']['route_ms']-rows['td']['route_ms']})
    savings=[]
    for trial in sorted({c['trial'] for c in candidate['cases']}):
        rows={c['arm']:c for c in candidate['cases'] if c['trial']==trial}
        require(set(rows)=={'td','old','new'},'Incomplete candidate triplet')
        a,b=rows['old'],rows['new']
        require([v['value']['region'] for v in a['regions']]==[v['value']['region'] for v in b['regions']],'Region identity changed')
        require(a['cold_region']['value']['region']==b['cold_region']['value']['region'],'Cold region changed')
        require(a['concurrent']['value']['region']==b['concurrent']['value']['region'],'Concurrent region changed')
        require(a['snapshot_before']==b['snapshot_before'],'Snapshot identities differ')
        comparisons={key:[v['value'][key] for v in a['chunks']]==[v['value'][key] for v in b['chunks']] for key in ['blocks_sha256','geology_sha256','normalized_sha256']}
        diagnostic=compare(candidate_path/f't{trial}-old/world',candidate_path/f't{trial}-new/world',a['plan']['chunks'])
        require(not diagnostic['palette_conflicts'],'Saved regional palette changed')
        savings.append({'trial':trial,'td_ms':rows['td']['route_ms'],'old_ms':a['route_ms'],'new_ms':b['route_ms'],
                        'saved_ms':a['route_ms']-b['route_ms'],'remaining_added_ms':b['route_ms']-rows['td']['route_ms'],
                        'sample_hash_equality':comparisons,'post_feature_diagnostic':diagnostic})
    require(len(pairs)==len(savings)==3,'Expected three clean pairs in each matrix')
    checks=[v for c in candidate['cases'] for v in c.get('elevation_checks',[])]
    require(len(checks)==2 and all(v['equal'] and v['samples']==65536 for v in checks),'Missing full anchor elevation proof')
    micro=json.loads((sampler/'sampler-results.json').read_text())
    require(micro['shared_inputs_unchanged'] and micro['sampler']['exit_code']==0,'Sampler process failed')
    for name,digest in micro['sampler']['logs'].items():
        require(sha(sampler/'sampler'/name)==digest,'Sampler log changed')
    for sample in micro['sampler']['samples']:
        require(sample['equal'] and sample['computed_windows']==0 and len(sample['pairs'])==20,'Invalid sampler comparison')
        sample['median_saved_ms']=statistics.median(v['old_ms']-v['new_ms'] for v in sample['pairs'])
        sample['median_old_ms']=statistics.median(v['old_ms'] for v in sample['pairs'])
        sample['median_new_ms']=statistics.median(v['new_ms'] for v in sample['pairs'])
    require(all(d['models']==candidate['models']==micro['models'] for d in baseline),'Models differ between matrices')
    return {'baseline':baseline,'candidate':candidate,'baseline_pairs':pairs,'optimization_pairs':savings,
            'excluded_first_baseline_trials':exclude_first,
            'raw_source_directories':{'baseline':[p.name for p in sources],'candidate':candidate_path.name,'sampler':sampler.name},
            'warm_tensor_sampler':micro,'sampler_raw_results_sha256':sha(sampler/'sampler-results.json'),
            'median_refreshed_added_ms':statistics.median(v['added_ms'] for v in pairs),
            'median_saved_ms':statistics.median(v['saved_ms'] for v in savings),
            'median_remaining_added_ms':statistics.median(v['remaining_added_ms'] for v in savings),
            'limits':['Fresh application caches; OS disk cache not flushed.','Sequential chunk operation times are summed; overlapping caller waits are never summed.','Full post-feature equality is diagnostic; the retained stronger #5 failure is unchanged.']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,nargs='+',required=True)
    p.add_argument('--exclude-first-baseline-trial',type=int,action='append',default=[])
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--sampler',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(json.dumps(export(a.baseline,a.candidate,a.sampler,a.exclude_first_baseline_trial),indent=2)+'\n')
