"""Recheck retained raw integrated-client evidence and export a portable summary."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

h=runpy.run_path(str(Path(__file__).with_name('verify-hot-config.py')))
r=h['h']['runtime']; require=h['require']; ROOT=r['ROOT']


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def summarize(case, regression=False):
    result=json.loads((case/'integrated-results.json').read_text())
    raw=(case/'console.log').read_text(errors='replace')
    require(r['sha'](case/'console.log')==result['console_sha256'],'Raw log changed')
    for p,sha in result['source_sha256'].items():
        source=case/'executed-sources'/p
        require(r['sha'](source if source.exists() else ROOT/p)==sha,'Executed source differs: '+p)
    require(result['exit_code']==0 and result['source_unchanged'] and result['shared_unchanged'],'Incomplete process or preservation')
    if not regression:
        require(result['inputs_exactly_restored'],'Inputs not restored')
        require(result['seed_input_hashes']['original']==result['seed_input_hashes']['restored']
                and result['seed_input_hashes']['original']!=result['seed_input_hashes']['alternate'],'Seed restoration hashes differ')
        require(result['control_before']['terrain']==result['control_final']['terrain'],'Compatible control terrain changed')
    require([s['name'] for s in result['steps']]==['control','rejection','next-compatible','restored-reopen'],'Incomplete matrix')
    require(len(re.findall('INTEGRATED_SERVER [1-4]',raw))==4,'Expected four actual integrated-server starts')
    require('Terrain diffusion inference: CPU' in raw and 'TD_MODEL_RETURN provider=CPU' in raw,'Missing actual TD execution')
    require(not any(s in raw for s in ('No space left on device','There is not enough space on the disk','Failed to save chunk','Failed to store chunk')),'Storage failure')
    steps=[]
    cleanup=True
    for item in result['steps']:
        require(item['state']['pid']==result['pid'],'Client PID changed')
        stopped=item['stopped']
        require(not any(stopped['server_threads_alive']) and stopped['client_server_null'] and stopped['previous_shutdown'],'Server not stopped')
        require(all(stopped[k] for k in ('owner_null','active_null','context_null')) and stopped['geology_cache']==0,'Geology state leaked')
        require(stopped['td_pending']==0 and not stopped['explorer_running'] and stopped['explorer_port']==-1,'TD resource active')
        cleanup &= not any(t['name'] in ('terrain-explorer-http','HTTP-Dispatcher') for t in stopped['td_threads'])
        entry={k:v for k,v in item.items() if k!='log'}
        if 'observed' in entry:
            entry['observed']=json.loads(json.dumps(entry['observed']))
            entry['observed']['region']['addon_origin']='<disposable>/mods/geologic-variation-0.2.2-dev.jar'
        steps.append(entry)
    rejected=result['steps'][1]
    require(rejected['log'] in raw,'Rejection log segment differs')
    require(rejected['runtime_context']=={**rejected['saved_context'],'seed':str(int(rejected['saved_context']['seed'])+1)},'Wrong mismatch')
    require('caller=addon-anchor' not in rejected['log'],'Incompatible geology generated')
    require('TD_MODEL_RETURN' not in rejected['log'] and 'TD_REQUEST' not in rejected['log']
            and 'uncached region requested' not in rejected['log'],'Terrain work during incompatible load')
    require(result['original']==result['rejected'],'Rejection changed snapshot/regions/terrain')
    require(result['original']['terrain']==result['final']['terrain'],'Restoration altered persisted terrain')
    require(result['original']['preserved']['snapshot']==result['final']['preserved']['snapshot'],'Snapshot changed')
    screenshot=case/'screenshots/recovery.png'; require(screenshot.is_file(),'Missing recovery-screen capture')
    require(cleanup != regression,'Expected '+('reproduced executor cleanup failure' if regression else 'complete explorer cleanup'))
    return {k:result[k] for k in ('source_baseline','pid','exit_code','free_bytes_before_launch','source_sha256',
            'addon_sha256','probe_sha256','td_sha256','launcher_manifest_sha256','console_sha256',
            'source_unchanged','shared_unchanged','explorer_before_rejection','explorer_before_rejection_state')} | {
        'explorer_executor_cleanup_pass':cleanup,'rejection_model_returns':0,'rejection_logged_heightmap_requests':0,
        'steps':steps,'snapshot_fields':result['original']['snapshot_fields'],
        'persisted_records':len(result['original']['terrain']),
        'persisted_status_counts':dict(Counter(v['status'] for v in result['original']['terrain'].values())),
        'terrain_sha256':{k:digest(result[k]['terrain']) for k in ('original','rejected','final')},
        'separate_region_hashes':{k:result[k]['preserved']['regions'] for k in ('original','rejected','final')},
        'snapshot_sha256':result['original']['preserved']['snapshot'],
        'source_fixture_manifest_sha256':digest(result['source_fixture']),
        'shared_inputs':result['shared_inputs'],'screenshot_sha256':r['sha'](screenshot),
        'inputs_exactly_restored':result.get('inputs_exactly_restored'),
        'seed_input_hashes':result.get('seed_input_hashes',{}),
        'original_inputs':result.get('original_inputs',{}),
        'jdk_recheck':json.loads((case/'jdk-recheck.json').read_text()) if (case/'jdk-recheck.json').exists() else None}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('case',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--regression',action='store_true')
    a=p.parse_args(); a.output.write_text(json.dumps(summarize(a.case.resolve(),a.regression),indent=2)+'\n',newline='\n')
    print('Verified raw evidence and exported portable integrated-client summary')
