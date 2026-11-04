"""Preserve the frozen matched-native rejection; audit every other check unchanged."""
import argparse
import copy
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
f=runpy.run_path(str(Path(__file__).with_name('summarize-td-tracking.py')))
require=f['require'];sha=f['sha']
FAILURE='Actual matching native support changed'


def mismatches(data):
    rows=[]
    for seed,split in f['s']['SEEDS']:
        a,b=[next(c for c in data['cases'] if (c['seed'],c['scale'])==(seed,k)) for k in (1,6)]
        lookup={(p['x']//6,p['z']//6):p for p in b['observations'] if not any(g.endswith('_boundary') for g in p['groups'])}
        for x in a['observations']:
            if (x['x'],x['z']) not in lookup:continue
            y=lookup[x['x'],x['z']]
            for policy in f['old']['POLICIES']:
                left=x['policies'][policy]['matched_native_cell'];right=y['policies'][policy]['matched_native_cell']
                if (left['row'],left['col'])==(right['row'],right['col']) and left!=right:
                    rows.append(dict(seed=seed,split=split,policy=policy,target_native=[x['x'],x['z']],
                        left=left,right=right,mean_difference_metres=left['mean_metres']-right['mean_metres'],
                        coarse_equal={k:v for k,v in x['policies'][policy]['coarse'].items() if k!='scale'}==
                                     {k:v for k,v in y['policies'][policy]['coarse'].items() if k!='scale'}))
    return rows


def audited(call,data):
    # Source bytes remain frozen. Only this named negative audit records the
    # expected rejection instead of ending at the first row; no tolerance is used.
    recorded=[];namespace=f['evaluate'].__globals__;original=namespace['require']
    def guard(condition,message):
        if not condition and message==FAILURE:recorded.append(message)
        else:original(condition,message)
    namespace['require']=guard
    try:result=call()
    finally:namespace['require']=original
    errors=mismatches(result)
    require(len(recorded)==len(errors)==3,'Unexpected matched-native failure set')
    require({(p['seed'],p['policy'],*p['target_native']) for p in errors}==
        {(-2026110411,'province_anchor',-320,-4032),(-2026110411,'province_anchor',-64,-3648),
         (-2026110411,'fixed_grid_4',1088,-3520)},'Unexpected failure locations')
    for pair in result['paired_support']:
        seed=pair['seed'];a,b=[next(c for c in result['cases'] if (c['seed'],c['scale'])==(seed,k)) for k in (1,6)]
        lookup={(p['x']//6,p['z']//6):p for p in b['observations'] if not any(g.endswith('_boundary') for g in p['groups'])}
        for policy,counts in pair['policies'].items():
            objects=hashes=0
            for x in a['observations']:
                if (x['x'],x['z']) not in lookup:continue
                left=x['policies'][policy]['matched_native_cell'];right=lookup[x['x'],x['z']]['policies'][policy]['matched_native_cell']
                if (left['row'],left['col'])!=(right['row'],right['col']):continue
                hashes+=left['float_sha256']==right['float_sha256'];objects+=left==right
            # The frozen implementation increments after its hard assertion.
            # Correct descriptive counts here; the original assertion stays failed.
            counts['matching_hashes']=hashes;counts['matching_objects']=objects
    result['frozen_matched_native_assertion']=dict(passed=False,failure=FAILURE,mismatches=errors,
        distinct_native_cells=len({(p['seed'],p['left']['row'],p['left']['col']) for p in errors}),tolerance_used=False)
    result['decision']['strict_paired_support_passed']=False
    result['decision']['tracked_morphology_coverage_passed']=False
    return result


def rejection(call):
    try:call()
    except RuntimeError as error:require(str(error)==FAILURE,'Unexpected frozen rejection: '+str(error))
    else:raise RuntimeError('Negative audit requires frozen rejection')


def evaluate(data):
    rejection(lambda:f['evaluate'](copy.deepcopy(data)))
    return audited(lambda:f['evaluate'](data),data)


def export(source):
    rejection(lambda:f['export'](source))
    result=audited(lambda:f['export'](source),None)
    result['frozen_strict_export']=dict(passed=False,failure=FAILURE,preserved_source='scripts/summarize-td-tracking.py')
    result['frozen_exporter_sha256']=sha(Path(__file__).with_name('summarize-td-tracking.py'))
    result['negative_exporter_sha256']=sha(Path(__file__))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(json.dumps(export(a.source),indent=2)+'\n')
