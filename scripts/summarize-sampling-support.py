"""Strict raw-evidence validation and portable morphology-only policy comparison."""
import argparse
from collections import OrderedDict
import hashlib
import json
import math
from pathlib import Path
import runpy
import statistics

d=runpy.run_path(str(Path(__file__).with_name('verify-sampling-support.py')))
require=d['require'];sha=d['r']['sha'];ROOT=d['r']['ROOT']
POLICIES=('province_anchor','target','fixed_grid_4')


def prior(seed,row,col,tendency):
    choices={'ocean':['marine sedimentary domain','mafic oceanic domain'],
             'coast':['sedimentary margin','exposed inherited belt'],
             'land':['sedimentary platform','uplifted or intrusive belt']}[tendency]
    # Explicit uncalibrated synthetic v1 prior, never a posterior/confidence.
    digest=hashlib.sha256(f'synthetic-prior-1:{seed}:{row}:{col}'.encode('ascii')).digest()
    if digest[0]&1:choices=list(reversed(choices))
    weight=0.4+0.2*digest[1]/255
    return {'identity':'synthetic-prior-1','hypotheses':[{'name':name,'prior_weight':w} for name,w in zip(choices,(weight,1-weight))],
            'prior_basis':'Arbitrary seeded synthetic weights in [0.4,0.6]; uncalibrated and not geological evidence',
            'posterior':None,'geological_confidence':'unestablished','stone_selection':None,
            'interpretation':'synthetic competing histories; not recovered tectonic history'}


def metrics(rows,policy):
    errors=[];matched=[];fine_displacement=[];signs=0;fine_signs=0;exposure_agreement=0;hidden_mixed=0
    for row in rows:
        value=row['policies'][policy];coarse=value['coarse'];fine=value['matched_native_cell']
        central=coarse['elevations'][4]
        target=row['policies']['target']['matched_native_cell']['mean_metres']
        errors.append(abs(central-target));matched.append(abs(central-fine['mean_metres']))
        signs+=(central<0)==(target<0)
        fine_displacement.append(abs(fine['mean_metres']-target))
        fine_signs+=(fine['mean_metres']<0)==(target<0)
        fraction=row['policies']['target']['matched_native_cell']['below_zero_fraction']
        exposure='ocean' if fraction==1 else 'land' if fraction==0 else 'coast'
        tendency=d['d']['tendency'](coarse)
        exposure_agreement+=tendency==exposure
        hidden_mixed+=tendency!='coast' and exposure=='coast'
    return {'n':len(rows),'central_sign_agreements':signs,
            'target_mean_absolute_error_metres':statistics.mean(errors),
            'target_mean_median_absolute_error_metres':statistics.median(errors),
            'matched_support_mean_absolute_error_metres':statistics.mean(matched),
            'fine_representative_to_target_mean_absolute_error_metres':statistics.mean(fine_displacement),
            'fine_representative_to_target_sign_agreements':fine_signs,
            'neighborhood_vs_target_fine_cell_tendency_agreements':exposure_agreement,
            'unanimous_neighborhood_with_mixed_target_fine_cell':hidden_mixed,
            'exposure_caveat':'Different support: 3x3 coarse signs vs central target fine-cell pixel signs; not shoreline accuracy.'}


def coherence(rows):
    results={}
    for policy in POLICIES:
        groups={}
        for row in rows:
            policy_value=row['policies'][policy]
            value={k:policy_value[k] for k in ('coarse','matched_native_cell')}
            c=value['coarse'];key=(c['row'],c['col'])
            if key in groups:require(value==groups[key],'Shared-cell evidence incoherent')
            groups[key]=value
        results[policy]={'queries':len(rows),'representative_cells':len(groups),
                         'repeated_cell_queries':len(rows)-len(groups),'shared_cell_evidence_equal':True}
    return results


def validate_counts(case):
    coarse=OrderedDict();fine=OrderedDict();expected_coarse=expected_fine=0
    unique=set()
    for row in case['observations']:
        new_coarse=new_fine=0
        for name in POLICIES:
            value=row['policies'][name];c=value['coarse'];f=value['matched_native_cell'];key=(c['row'],c['col'])
            require((f['row'],f['col'])==key and f['samples']==65536,'Unmatched spatial support')
            require(len(c['elevations'])==9 and c['p5_used'] is False,'Invalid coarse data')
            require(all(math.isfinite(v) for v in c['elevations']),'Unavailable coarse data')
            require(math.isfinite(f['mean_metres']) and 0<=f['below_zero_fraction']<=1,'Unavailable fine data')
            unique.add(key)
            for cache,kind in ((coarse,'coarse'),(fine,'fine')):
                if key not in cache:
                    if kind=='coarse':new_coarse+=1
                    else:new_fine+=1
                cache[key]=True;cache.move_to_end(key)
                if len(cache)>128:cache.popitem(last=False)
        expected_coarse+=new_coarse;expected_fine+=new_fine
        # Two tile reads are uncached diagnostics; scale 1 uses direct data,
        # scale 6 uses fetchHeightmap (its private pipeline work is not a public data call).
        delta=row['delta']
        require(delta['coarse_calls']==new_coarse,'Coarse request dedup count differs')
        require(delta['computed_windows']>=0,'Invalid new-window count')
        if case['scale']==1:
            require(delta['pipeline_data_calls']==new_fine+2 and delta['heightmap_calls']==0,'Fine request accounting')
        else:
            require(delta['heightmap_calls']==2 and delta['pipeline_data_calls']==new_fine,'Fine scale-6 request accounting')
        require(row['fine_cache_entries']==len(fine)<=128,'Fine cache bound')
        target=row['policies']['target']['coarse'];grid=row['policies']['fixed_grid_4']['coarse']
        stride=256*case['scale']
        require((target['row'],target['col'])==(row['z']//stride,row['x']//stride),'Target orientation/floor')
        require((grid['row'],grid['col'])==(target['row']//4*4+2,target['col']//4*4+2),'Fixed global grid')
        for tile in ('target_fine_tile','anchor_fine_tile'):
            require(len(row[tile]['samples'])==25 and row[tile]['width_blocks']==256,'Fine tile support')
    total={key:case['after'][key]-case['before'][key] for key in case['before']}
    require(total=={k:sum(row['delta'][k] for row in case['observations']) for k in total},'Unaccounted diagnostic requests')
    return {'forward_actual_delta':total,'expected_deduplicated_coarse_requests':expected_coarse,
            'expected_deduplicated_native_fine_requests':expected_fine,'unique_native_cells':len(unique),
            'policy_lookups':len(case['observations'])*3,'max_retained_fine_entries':max(v['fine_cache_entries'] for v in case['observations']),
            'reverse_actual_delta':{k:sum(row[k] for row in case['reverse_deltas']) for k in total},
            'attribution':'Combined serial diagnostic workload with shared TD tensor caches; not independent policy timings or route benchmarks.'}


def boundaries(case):
    rows=case['observations'][12:];out=[]
    for a,b in zip(rows[::2],rows[1::2]):
        edge={'selection':a['selection'],'a':[a['x'],a['z']],'b':[b['x'],b['z']],
              'province_changed':a['province']!=b['province'],'policies':{}}
        for policy in POLICIES:
            ca=a['policies'][policy]['coarse'];cb=b['policies'][policy]['coarse']
            edge['policies'][policy]={'representative_cell_changed':(ca['row'],ca['col'])!=(cb['row'],cb['col']),
                'central_mean_jump_metres':abs(ca['elevations'][4]-cb['elevations'][4]),
                'neighborhood_tendency_changed':d['d']['tendency'](ca)!=d['d']['tendency'](cb)}
        edge['target_fine_tile_mean_jump_metres']=abs(a['target_fine_tile']['mean_metres']-b['target_fine_tile']['mean_metres'])
        out.append(edge)
    require(sum(v['province_changed'] for v in out[-2:])==2,'Province contacts missing')
    return out


def recommend(summary):
    held=summary['held_out'];passed=True
    for group in ('coverage','selected_contrasts'):
        values=held[group]['policies'];target=values['target']
        for alternative in ('province_anchor','fixed_grid_4'):
            other=values[alternative]
            passed &= target['target_mean_absolute_error_metres']<=other['target_mean_absolute_error_metres']
            passed &= target['central_sign_agreements']>=other['central_sign_agreements']
    return {'policy':'target' if passed else 'no supported winner',
        'scope':'Point terrain diagnostics only; no production sampler/classifier adoption',
        'criterion':'Held-out coverage AND selected-contrast mean absolute target error no worse, central sign agreement no worse than either displacement alternative',
        'geological_classification':'abstain','p5_used':False}


def export(source):
    data=json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'] and data['production_sha256']==data['baseline_sha256'],'Preservation failed')
    require({(c['seed'],c['scale'],c['split']) for c in data['cases']}==
        {(seed,scale,split) for seed,split in d['SEEDS'] for scale in (1,6)} and len(data['cases'])==6,'Incomplete matrix')
    for name,digest in data['sources'].items():require(sha(ROOT/name)==digest,'Executed source changed: '+name)
    for case in data['cases']:
        for name,digest in case['logs'].items():require(sha(source/case['name']/name)==digest,'Raw log changed')
        raw=[]
        for line in (source/case['name']/'console-1.log').read_text(errors='replace').splitlines():
            if 'ACCEPTANCE {' not in line:continue
            value=json.loads(line.split('ACCEPTANCE ',1)[1])
            if 'policies' in value and 'target_fine_tile' in value:raw.append(value)
        require(len(raw)==48,'Raw comparison log coverage missing')
        require(raw[:24]==[{k:v for k,v in row.items() if k!='selection'} for row in case['observations']],
                'Forward data differs from raw runtime log')
        require([d['canonical'](v) for v in raw[:24]]==[d['canonical'](v) for v in reversed(raw[24:])],
                'Raw reverse traversal changed evidence')
        require(case['reverse_deltas']==[v['delta'] for v in raw[24:]],'Reverse counts differ from raw log')
        for pattern,digest in [('geologic-variation-*.jar',data['production_sha256']),
                              ('geology-runtime-probe-*.jar',data['probe_sha256']),
                              ('NeoForge-terrain-diffusion-*.jar','3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8')]:
            files=list((source/case['name']/'mods').glob(pattern));require(len(files)==1 and sha(files[0])==digest,'Artifact changed')
        require(case['traversal_equal'] and case['terrain_snapshot_unchanged'] and case['persisted_records']>0 and case['exit_code']==0,'Acceptance incomplete')
        require(case['sample']['blocks_sha256']==case['reopened']['blocks_sha256'],'Complete sample changed')
        require(len(case['scan'])==81 and len(case['observations'])==24,'Incomplete support experiment')
        require(case['selection']==d['select'](case['scan'])+d['boundary_points'](case['seed'],case['scale']),'Selection drift')
        suite=case['suite'];require(suite['concurrent_requests']==1 and suite['real_cache_entries']==128 and suite['evicted_recomputed'] and suite['traversal_equal'] and case['oracle']['equal'],'Coarse contract failure')
        case['request_accounting']=validate_counts(case);case['boundary_evaluation']=boundaries(case)
        require(case['request_accounting']['forward_actual_delta']['computed_windows']>0,'No genuine new fine work')
        case['coherence']=coherence(case['observations'])
        case['elongated_candidate_evaluation']=[]
        for point in case['selection'][10:12]:
            xx,zz=point['curvature'];strong,weak=sorted((xx,zz),key=abs,reverse=True)
            v=point['evidence']['elevations'];center=v[4]
            axis=[v[3],center,v[5]] if abs(xx)>=abs(zz) else [v[1],center,v[7]]
            ridge=point['selection']=='ridge_candidate'
            case['elongated_candidate_evaluation'].append({'selection':point['selection'],
                'curvature':point['curvature'],'axial_curvature_ratio':abs(strong)/abs(weak) if weak else None,
                'anisotropy_at_least_2':abs(strong)>=2*abs(weak),
                'cross_axis_local_extremum':center>=max(axis[0],axis[2]) if ridge else center<=min(axis[0],axis[2]),
                'extent':'three coarse cells only; extended ridge/basin continuity is unvalidated'})
        for row in case['observations']:
            c=row['policies']['target']['coarse']
            row['synthetic_geology']=prior(case['seed'],c['row'],c['col'],d['d']['tendency'](c))
        case['evaluations']={group:{policy:metrics(rows,policy) for policy in POLICIES}
            for group,rows in [('coverage',case['observations'][:5]),('selected_contrasts',case['observations'][5:12]),('boundaries',case['observations'][12:])]}
    # Cross-scale native coarse evidence is counted once per seed/selection/location.
    paired=[]
    for seed,split in d['SEEDS']:
        small=next(c for c in data['cases'] if c['seed']==seed and c['scale']==1)
        large=next(c for c in data['cases'] if c['seed']==seed and c['scale']==6)
        shared=0;max_native_mean_difference=0
        for a,b in zip(small['observations'][:12],large['observations'][:12]):
            for policy in POLICIES:
                ca=a['policies'][policy]['coarse'];cb=b['policies'][policy]['coarse']
                require(ca['elevations']==cb['elevations'],'Repeated native coarse values changed')
                fa=a['policies'][policy]['matched_native_cell'];fb=b['policies'][policy]['matched_native_cell']
                shared+=1;max_native_mean_difference=max(max_native_mean_difference,abs(fa['mean_metres']-fb['mean_metres']))
        paired.append({'seed':seed,'split':split,'paired_policy_observations':shared,
                       'native_fine_max_mean_difference_metres':max_native_mean_difference})
    data['cross_scale_pairs']=paired
    data['observation_units']={
        'screened_neighborhood_rows':sum(len(c['scan']) for c in data['cases']),
        'distinct_seed_native_screen_locations':len({(c['seed'],p['evidence']['row'],p['evidence']['col']) for c in data['cases'] for p in c['scan']}),
        'comparison_rows':sum(len(c['observations']) for c in data['cases']),
        'distinct_seed_native_target_cells':len({(c['seed'],v['policies']['target']['coarse']['row'],v['policies']['target']['coarse']['col']) for c in data['cases'] for v in c['observations']}),
        'distinct_seed_native_policy_cells':len({(c['seed'],p['coarse']['row'],p['coarse']['col']) for c in data['cases'] for v in c['observations'] for p in v['policies'].values()}),
        'interpretation':'Repeated scales and repeated representative cells are not independent coarse observations; descriptive fixed coverage and selected contrasts only.'}
    data['native_scale_summary']={}
    for split in ('development','held_out'):
        cases=[c for c in data['cases'] if c['split']==split and c['scale']==1]
        data['native_scale_summary'][split]={}
        for group,bounds in [('coverage',(0,5)),('selected_contrasts',(5,12)),('boundaries',(12,24))]:
            lo,hi=bounds;rows=[v for c in cases for v in c['observations'][lo:hi]]
            data['native_scale_summary'][split][group]={
                'distinct_seed_native_target_cells':len({(c['seed'],v['policies']['target']['coarse']['row'],v['policies']['target']['coarse']['col']) for c in cases for v in c['observations'][lo:hi]}),
                'policies':{policy:metrics(rows,policy) for policy in POLICIES}}
    data['sampling_recommendation']=recommend(data['native_scale_summary'])
    retained_path=ROOT/'docs/evidence/terrain-diagnostics-2026-11-03.json'
    retained=json.loads(retained_path.read_text());checks=0
    for case in data['cases']:
        old=next((c for c in retained['cases'] if (c['seed'],c['scale'])==(case['seed'],case['scale'])),None)
        if old is None:continue
        for row in case['observations'][5:9]:
            label=row['selection'].removeprefix('extreme_')
            previous=next(v for v in old['comparisons'] if v['stratum']==label)
            require((row['x'],row['z'])==(previous['x'],previous['z']),'Retained selection changed')
            require(row['anchor_fine_tile']['mean_metres']==previous['fine_mean_metres'] and
                row['anchor_fine_tile']['fine_tile_relief_metres']==previous['fine_tile_relief_metres'],'Production-compatible anchor extraction changed')
            checks+=1
    require(checks==16,'Retained anchor comparisons missing')
    data['retained_anchor_crosscheck']={'comparisons':checks,'evidence_sha256':sha(retained_path),
        'result':'Exact geology-1 anchor mean/relief agreement with retained PR #48; old runtime matrix was not rerun.'}
    reference=Path(__file__).with_name('sampling-reference-fields.py')
    data['elongated_reference_fields']=runpy.run_path(str(reference))['experiment']()
    data['elongated_reference_source_sha256']=sha(reference)
    data['analysis_identity']='sampling-support-diagnostic-1'
    data['decision']={'production_caller':False,'generator_adopted':False,'geological_selection':'abstain',
        'remaining_gate':'Independent geological plausibility/coherence criteria and calibration; morphology alone cannot identify terranes. Any output change additionally needs version/new-world/save and paired route acceptance.'}
    data['raw_results_sha256']=sha(source/'results.json');data['exporter_sha256']=sha(Path(__file__))
    def scrub(value):
        if isinstance(value,dict):return {k:scrub(v) for k,v in value.items() if k!='addon_origin'}
        if isinstance(value,list):return [scrub(v) for v in value]
        return value
    return scrub(data)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.write_text(json.dumps(export(args.source),indent=2)+'\n')
