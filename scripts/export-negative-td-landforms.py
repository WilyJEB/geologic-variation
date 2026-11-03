"""Negative-result audit: preserve the frozen paired-scale failure with strict raw/source/artifact checks."""
import argparse
import json
from pathlib import Path
import runpy

v=runpy.run_path(str(Path(__file__).with_name('verify-td-landforms.py')))
old=runpy.run_path(str(Path(__file__).with_name('summarize-sampling-support.py')))
s=v['s'];r=v['r'];require=v['require'];ROOT=v['ROOT'];sha=r['sha']


def evaluate(data):
    require(len(data['cases'])==6 and {(c['seed'],c['scale'],c['split']) for c in data['cases']}==
            {(seed,scale,split) for seed,split in s['SEEDS'] for scale in (1,6)},'Incomplete matrix')
    for c in data['cases']:
        require(len(c['scan'])==81,'Screen limit')
        expected=s['candidates'](c['scan'])
        require(len(expected)==len(c['attempts'])<=4,'Candidate count')
        for a,b in zip(c['attempts'],expected):
            require(all(a[k]==value for k,value in b.items()),'Candidate drift')
            require(len(a['stations'])==5,'Station support')
            require([(x['row'],x['col']) for x in a['stations']]==s['stations'](a),'Station coordinates')
            require(a['evaluation']==s['evaluate'](a,a['stations']),'Support drift')
        require(c['selection']==v['locations'](c) and len(c['selection'])<=52,'Selection drift')
        require([(x['x'],x['z'],x['groups']) for x in c['observations']]==
                [(p['x'],p['z'],p['groups']) for p in c['selection']],'Observation support')
        require([{k:v for k,v in v['d']['canonical'](x).items() if k!='groups'} for x in c['observations']]==
                [v['d']['canonical'](x) for x in reversed(c['reverse'])],'Reverse evidence differs')
        counting=dict(c,reverse_deltas=[x['delta'] for x in c['reverse']])
        c['request_accounting']=old['validate_counts'](counting)
        require(c['final_metrics']['computed_windows']-c['initial_metrics']['computed_windows']<=12000,'Window limit')
        suite=c['suite'];require(suite['concurrent_requests']==1 and suite['real_cache_entries']==128 and suite['evicted_recomputed'] and suite['traversal_equal'] and c['oracle']['equal'],'Coarse suite')
        require(c['exit_code']==0 and c['snapshot_unchanged'],'Fixture failure')
        c['coherence']=old['coherence'](c['observations'])
        c['features']=[]
        for i,a in enumerate(s['choose'](c['attempts'])):
            rows=[next(x for x in c['observations'] if f'feature_{i}_{j}' in x['groups']) for j in range(15)]
            c['features'].append(dict(kind=a['kind'],row=a['row'],col=a['col'],axis=a['axis'],
                coarse=a['evaluation'],fine=s['fine_evaluate'](a,rows),
                feature_center_world=[a['col']*256*c['scale']+128*c['scale'],a['row']*256*c['scale']+128*c['scale']]))
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
        points=v['d']['boundary_points'](c['seed'],c['scale'])
        for a,b in zip(points[::2],points[1::2]):
            pair=[next(x for x in c['observations'] if (x['x'],x['z'])==(p['x'],p['z'])) for p in (a,b)]
            c['boundary_evaluation'].append(dict(selection=a['selection'],a=[a['x'],a['z']],b=[b['x'],b['z']],
                province_changed=pair[0]['province']!=pair[1]['province'],
                central_mean_jumps_metres={p:abs(pair[0]['policies'][p]['coarse']['elevations'][4]-pair[1]['policies'][p]['coarse']['elevations'][4]) for p in old['POLICIES']},
                target_tile_mean_jump_metres=abs(pair[0]['target_fine_tile']['mean_metres']-pair[1]['target_fine_tile']['mean_metres'])))
        require(all(x['province_changed'] for x in c['boundary_evaluation'][-2:]),'Province boundaries missing')
        for x in c['observations']:
            p=x['policies']['target']['coarse']
            x['synthetic_geology']=old['prior'](c['seed'],p['row'],p['col'],v['d']['d']['tendency'](p))
    pairs=[]; mismatches=[]
    for seed,split in s['SEEDS']:
        a,b=[next(c for c in data['cases'] if c['seed']==seed and c['scale']==k) for k in (1,6)]
        right={(x['x']//6,x['z']//6):x for x in b['observations'] if not any(g.endswith('_boundary') for g in x['groups'])}
        total=matches=0
        for x in a['observations']:
            if (x['x'],x['z']) not in right:continue
            y=right[x['x'],x['z']]
            for p in old['POLICIES']:
                
                if x['policies'][p]['coarse']['elevations']!=y['policies'][p]['coarse']['elevations']:
                    mismatches.append(dict(seed=seed,x=x['x'],z=x['z'],policy=p,scale1_province=x['province'],scale6_province=y['province'],scale1_coarse=x['policies'][p]['coarse'],scale6_coarse=y['policies'][p]['coarse']))
                total+=1;matches+=x['policies'][p]['matched_native_cell']['float_sha256']==y['policies'][p]['matched_native_cell']['float_sha256']
        pairs.append(dict(seed=seed,split=split,paired_policy_rows=total,native_hash_matches=matches))
    passed=all(len(c['features'])==2 and {f['kind'] for f in c['features']}=={'ridge','basin'} and
               all(f['coarse']['supported'] and f['fine']['native_cell']['supported'] and f['fine']['scaled_tile']['supported'] for f in c['features'])
               for c in data['cases'] if c['split']=='held_out')
    data['cross_scale_pairs']=pairs
    data['frozen_paired_scale_assertion']={'passed':not mismatches,'assertion':'Paired coarse drift','mismatches':mismatches,'interpretation':'Failed frozen equality criterion remains failed; not statistical independence or accepted anchor equivalence.'}
    passed = passed and not mismatches
    data['coverage_gate']={'passed':passed,'rule':'Both held-out seeds: ridge AND basin, coarse/matched native/scaled tile at both scales',
        'policy':'supported straight-feature diagnostics' if passed else 'actual-target point diagnostics only',
        'geological_classification':'abstain','geological_confidence':'unestablished','p5_used':False,
        'remaining_gate':'New frozen bounded orientation/scale protocol with independent fine crest localization and enough TD ridges AND basins; geological plausibility remains a separate gate.'}
    data['observation_units']={'screen_rows':sum(len(c['scan']) for c in data['cases']),
        'distinct_seed_native_screen_cells':len({(c['seed'],p['evidence']['row'],p['evidence']['col']) for c in data['cases'] for p in c['scan']}),
        'forward_comparisons':sum(len(c['observations']) for c in data['cases']),
        'distinct_seed_native_target_cells':len({(c['seed'],p['policies']['target']['coarse']['row'],p['policies']['target']['coarse']['col']) for c in data['cases'] for p in c['observations']}),
        'native_feature_candidates':sum(len(c['attempts']) for c in data['cases'] if c['scale']==1),
        'paired_scales_are_independent':False}
    return data


def export(source):
    # Keep and execute the original rejection. This audit cannot convert it to pass.
    frozen=runpy.run_path(str(Path(__file__).with_name('summarize-td-landforms.py')))
    try:
        frozen['export'](source)
    except RuntimeError as error:
        require(str(error)=='Paired coarse drift','Unexpected frozen-export failure: '+str(error))
    else:
        raise RuntimeError('Negative export requires the preserved frozen rejection')
    data=json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'] and data['production_sha256']==data['baseline_sha256'],'Inputs changed')
    for name,digest in data['sources'].items():require(sha(ROOT/name)==digest,'Executed source changed: '+name)
    for c in data['cases']:
        for name,digest in c['logs'].items():require(sha(source/c['name']/name)==digest,'Raw log changed')
        raw=[]
        for line in (source/c['name']/'console-1.log').read_text(errors='replace').splitlines():
            if 'ACCEPTANCE {' in line:raw.append(json.loads(line.split('ACCEPTANCE ',1)[1]))
        require(raw==[c['initial_metrics']]+[e['result'] for e in c['events']],'Raw transcript differs')
        comparisons=[e['result'] for e in c['events'] if e['command'].startswith('acceptance sampling-compare ')]
        n=len(c['observations'])
        require(comparisons==[{k:v for k,v in x.items() if k!='groups'} for x in c['observations']]+c['reverse'],'Raw fine observations differ')
        coarse=[e['result'] for e in c['events'] if e['command'].startswith('acceptance coarse ')]
        require(coarse==[p['evidence'] for p in c['scan']]+[x for a in c['attempts'] for x in a['stations']],'Raw selection evidence differs')
        for pattern,digest in [('geologic-variation-*.jar',data['production_sha256']),('geology-runtime-probe-*.jar',data['probe_sha256']),
                              ('NeoForge-terrain-diffusion-*.jar','3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8')]:
            files=list((source/c['name']/'mods').glob(pattern));require(len(files)==1 and sha(files[0])==digest,'Artifact drift')
    data=evaluate(data);data['frozen_exporter_sha256']=sha(Path(__file__).with_name('summarize-td-landforms.py'));data['frozen_strict_export']={'passed':False,'failure':'Paired coarse drift','preserved_source':'scripts/summarize-td-landforms.py'};data['raw_results_sha256']=sha(source/'results.json');data['exporter_sha256']=sha(Path(__file__))
    def scrub(x):
        if isinstance(x,dict):return {k:scrub(v) for k,v in x.items() if k!='addon_origin'}
        if isinstance(x,list):return [scrub(v) for v in x]
        return x
    return scrub(data)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.write_text(json.dumps(export(args.source),indent=2)+'\n')
