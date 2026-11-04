"""Strict frozen selector, transcript, artifact and paired-support audit."""
import argparse
import copy
import json
from pathlib import Path
import runpy

v=runpy.run_path(str(Path(__file__).with_name('verify-td-tracking.py')))
old=runpy.run_path(str(Path(__file__).with_name('summarize-sampling-support.py')))
s=v['s'];r=v['r'];ROOT=v['ROOT'];require=v['require'];sha=r['sha']


def evaluate(data):
    require({(c['seed'],c['scale'],c['split']) for c in data['cases']}=={(seed,scale,split) for seed,split in s['SEEDS'] for scale in (1,6)} and len(data['cases'])==6,'Matrix')
    for c in data['cases']:
        require(len(c['scan'])==81,'Fixed search area')
        require([(p['evidence']['row'],p['evidence']['col']) for p in c['scan']]==[(row,col) for row in range(-64,65,16) for col in range(-64,65,16)],'Screen coordinates')
        require([a['candidate'] for a in c['attempts']]==s['seeds'](c['scan']),'Candidate drift')
        for a in c['attempts']:
            require(a['legacy_evaluation']==s['legacy']['evaluate'](a['candidate'],a['legacy_stations']),'Legacy criteria drift')
            require([(p['row'],p['col']) for p in a['legacy_stations']]==s['legacy']['stations'](a['candidate']),'Legacy support')
            require(a['diagnosis']==s['diagnose'](a['candidate'],a['bands']),'Tracker drift')
            for bands,reverse in ((a['bands'],False),(a['reverse_bands'],True)):
                require([b['public_data_miss'] for b in bands]==([False]*48+[True] if reverse else [True]+[False]*48),'Patch deduplication')
                require(all(b['patch_cache_entries']==1 and b['step_native_pixels']==64 and b['radius_native_pixels']==1536 for b in bands),'Patch bounds')
            require([{k:v for k,v in b.items() if k!='public_data_miss'} for b in a['bands']]==[{k:v for k,v in b.items() if k!='public_data_miss'} for b in a['reverse_bands']],'Patch traversal')
        require(c['selection']==v['locations'](c) and len(c['selection'])<=52,'Fine selection drift')
        require([(p['x'],p['z'],p['groups']) for p in c['observations']]==[(p['x'],p['z'],p['groups']) for p in c['selection']],'Fine coordinates')
        canonical=v['v']['d']['canonical']
        require([{k:v for k,v in canonical(p).items() if k!='groups'} for p in c['observations']]==[canonical(p) for p in reversed(c['reverse'])],'Fine traversal')
        c['request_accounting']=old['validate_counts'](dict(c,reverse_deltas=[x['delta'] for x in c['reverse']]))
        reverse=dict(c,observations=c['reverse'],before={k:0 for k in c['before']},after={k:sum(x['delta'][k] for x in c['reverse']) for k in c['before']},reverse_deltas=[x['delta'] for x in c['observations']])
        old['validate_counts'](reverse)
        c['post_startup_delta']={k:c['final_metrics'][k]-c['initial_metrics'][k] for k in c['initial_metrics']}
        require(c['post_startup_delta']['computed_windows']<=12000,'Window budget')
        accounted=sum(c['request_accounting'][k]['pipeline_data_calls'] for k in ('forward_actual_delta','reverse_actual_delta'))+2*len(c['attempts'])
        require(c['post_startup_delta']['pipeline_data_calls']==accounted,'Public patch/data request accounting')
        suite=c['suite'];require(suite['concurrent_requests']==1 and suite['real_cache_entries']==128 and suite['evicted_recomputed'] and suite['traversal_equal'] and c['oracle']['equal'],'Coarse suite')
        require(c['exit_code']==0 and c['snapshot_unchanged'],'Fixture')
        c['terrain_agreement']={}
        for group in ('coverage','contrasts','boundaries','features'):
            def member(x):
                if group=='coverage':return 'coverage' in x['groups']
                if group=='contrasts':return any(g in ('ocean','coast','lowland','mountain','intermediate') for g in x['groups'])
                if group=='boundaries':return any(g.endswith('_boundary') for g in x['groups'])
                return any(g.startswith('feature_') for g in x['groups'])
            rows=[x for x in c['observations'] if member(x)]
            c['terrain_agreement'][group]={p:old['metrics'](rows,p) for p in old['POLICIES']} if rows else {}
        c['boundary_evaluation']=[]
        points=v['v']['d']['boundary_points'](c['seed'],c['scale'])
        for a,b in zip(points[::2],points[1::2]):
            pair=[next(x for x in c['observations'] if (x['x'],x['z'])==(p['x'],p['z'])) for p in (a,b)]
            c['boundary_evaluation'].append(dict(selection=a['selection'],province_changed=pair[0]['province']!=pair[1]['province'],
                central_mean_jumps_metres={p:abs(pair[0]['policies'][p]['coarse']['elevations'][4]-pair[1]['policies'][p]['coarse']['elevations'][4]) for p in old['POLICIES']},
                target_tile_mean_jump_metres=abs(pair[0]['target_fine_tile']['mean_metres']-pair[1]['target_fine_tile']['mean_metres'])))
        require(all(x['province_changed'] for x in c['boundary_evaluation'][-2:]),'Province contacts')
        c['fine_profiles']=[]
        for i,a in enumerate(c['attempts']):
            path=a['diagnosis']['runs']['tracked']['stations'];n=len(path)
            rows=[next(x for x in c['observations'] if f'feature_{i}_{j}' in x['groups']) for j in range(n*3)]
            assessments={}
            if n:
                for field in ('native_cell','scaled_tile'):
                    values=[p['policies']['target']['matched_native_cell']['mean_metres'] if field=='native_cell' else p['target_fine_tile']['mean_metres'] for p in rows]
                    centers=[dict(height=values[j]) for j in range(1,len(values),3)]
                    pairs=[[a['candidate']['sign']*(values[j+1]-values[j]),a['candidate']['sign']*(values[j+1]-values[j+2])] for j in range(0,len(values),3)]
                    assessments[field]=s['continuity'](centers,pairs)
            c['fine_profiles'].append(dict(kind=a['candidate']['kind'],assessments=assessments))
    data['paired_support']=[]
    for seed,split in s['SEEDS']:
        a,b=[next(c for c in data['cases'] if (c['seed'],c['scale'])==(seed,k)) for k in (1,6)]
        normalize=lambda p:{k:v for k,v in p['evidence'].items() if k!='scale'}
        require([normalize(p) for p in a['scan']]==[normalize(p) for p in b['scan']],'Paired screen')
        require([x['diagnosis'] for x in a['attempts']]==[x['diagnosis'] for x in b['attempts']],'Paired point tracker')
        right={(p['x']//6,p['z']//6):p for p in b['observations'] if not any(g.endswith('_boundary') for g in p['groups'])}
        counts={p:dict(matched_support=0,matching_hashes=0,differing_support=[]) for p in old['POLICIES']}
        for x in a['observations']:
            if (x['x'],x['z']) not in right:continue
            y=right[x['x'],x['z']]
            for p in old['POLICIES']:
                left=x['policies'][p]['matched_native_cell'];rightcell=y['policies'][p]['matched_native_cell']
                if (left['row'],left['col'])!=(rightcell['row'],rightcell['col']):
                    counts[p]['differing_support'].append(dict(target=[x['x'],x['z']],left=left,right=rightcell));continue
                counts[p]['matched_support']+=1
                require(left==rightcell,'Actual matching native support changed')
                counts[p]['matching_hashes']+=1
        data['paired_support'].append(dict(seed=seed,split=split,policies=counts,
            patch_hashes_match=[x['bands'][0]['full_float_sha256'] for x in a['attempts']]==[x['bands'][0]['full_float_sha256'] for x in b['attempts']]))
    passed=all(len(c['attempts'])==2 and all(a['diagnosis']['runs']['tracked']['supported'] for a in c['attempts']) and
        all(len(p['assessments'])==2 and all(x['supported'] for x in p['assessments'].values()) for p in c['fine_profiles']) for c in data['cases'] if c['split']=='held_out')
    data['decision']=dict(tracked_morphology_coverage_passed=passed,production_changed=False,policy='actual-target point diagnostics only',
        geological_selection='abstain',geological_confidence='unestablished',p5_used=False,
        remaining_gate='Independent unambiguous fine crest/trough localization with two-sided finite continuity, native means and scaled tiles on both fresh seeds/scales; geological plausibility remains separate.')
    data['units']=dict(forward_comparisons=sum(len(c['observations']) for c in data['cases']),
        distinct_seed_native_targets=len({(c['seed'],p['policies']['target']['matched_native_cell']['row'],p['policies']['target']['matched_native_cell']['col']) for c in data['cases'] for p in c['observations']}),
        patch_grids=12,distinct_seed_native_patches=sum(len(c['attempts']) for c in data['cases'] if c['scale']==1),
        paired_scales_independent=False)
    return data


def export(source):
    data=json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'] and data['production_sha256']==data['baseline_sha256'],'Inputs changed')
    for name,digest in data['sources'].items():require(sha(ROOT/name)==digest,'Executed source changed: '+name)
    for c in data['cases']:
        for name,digest in c['logs'].items():require(sha(source/c['name']/name)==digest,'Raw log changed')
        raw=[json.loads(line.split('ACCEPTANCE ',1)[1]) for line in (source/c['name']/'console-1.log').read_text(errors='replace').splitlines() if 'ACCEPTANCE {' in line]
        require(raw==[c['initial_metrics']]+[e['result'] for e in c['events']],'Raw transcript differs')
        comparisons=[e['result'] for e in c['events'] if e['command'].startswith('acceptance sampling-compare ')]
        require(comparisons==[{k:v for k,v in x.items() if k!='groups'} for x in c['observations']]+c['reverse'],'Raw fine differs')
        coarse=[e['result'] for e in c['events'] if e['command'].startswith('acceptance coarse ')]
        require(coarse==[p['evidence'] for p in c['scan']]+[x for a in c['attempts'] for x in a['legacy_stations']],'Raw coarse differs')
        bands=[e['result'] for e in c['events'] if e['command'].startswith('acceptance track-patch ')]
        require(bands==[b for a in c['attempts'] for b in a['bands']]+[b for a in reversed(c['attempts']) for b in reversed(a['reverse_bands'])],'Raw patch differs')
        for key,cmd in [('settings','settings'),('before',None),('after',None),('final_metrics',None),('suite','coarse-suite'),('oracle','coarse-check')]:
            if cmd:require(c[key] in [e['result'] for e in c['events'] if e['command']=='acceptance '+cmd],'Raw '+key)
            else:require(c[key] in [e['result'] for e in c['events'] if e['command']=='acceptance metrics'],'Raw metrics')
        for pattern,digest in [('geologic-variation-*.jar',data['production_sha256']),('geology-runtime-probe-*.jar',data['probe_sha256']),('NeoForge-terrain-diffusion-*.jar','3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8')]:
            files=list((source/c['name']/'mods').glob(pattern));require(len(files)==1 and sha(files[0])==digest,'Artifact drift')
    data=evaluate(data);data['raw_results_sha256']=sha(source/'results.json');data['exporter_sha256']=sha(Path(__file__))
    def scrub(x):
        if isinstance(x,dict):return {k:scrub(v) for k,v in x.items() if k!='addon_origin'}
        if isinstance(x,list):return [scrub(v) for v in x]
        return x
    return scrub(data)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(json.dumps(export(a.source),indent=2)+'\n')
