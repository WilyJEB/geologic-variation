"""Recheck raw artifact-substitution evidence and export portable hashes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

h = runpy.run_path(str(Path(__file__).with_name('verify-td-artifact.py')))
require = h['require']; sha = h['runtime']['sha']


def export(source):
    data = json.loads((source/'artifact-results.json').read_text())
    require(data['fixture_unchanged'] and data['models_unchanged'] and data['exit_code'] == 0, 'Incomplete recovery')
    require(len(data['launches']) == len({v['pid'] for v in data['launches']}) == 3, 'Not three independent launches')
    require(all(v['free_bytes_before'] >= 2*1024**3 for v in data['launches']), 'Insufficient disk')
    require(data['identical_td_classes'] == 58 and data['identical_model_manifest'], 'API/manifest inspection differs')
    require(data['original_inputs'] == data['restored_inputs'], 'Restoration differs')
    original, changed = data['original_inputs'], data['substituted_inputs']
    require(original['config'] == changed['config'], 'Config changed during substitution')
    require(sorted(original['mods'].values()).count(h['CPU']) == 1 and sorted(changed['mods'].values()).count(h['ALT']) == 1, 'Wrong TD artifacts')
    require({k:v for k,v in original['mods'].items() if v != h['CPU']} == {k:v for k,v in changed['mods'].items() if v != h['ALT']}, 'Other mods changed')
    require(original['mods']['geologic-variation-0.2.2-dev.jar'] == '39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226', 'Addon changed')
    before, reopened = data['before'], data['reopened']
    require(before['settings'] == reopened['settings'] and before['region'] == reopened['region'], 'Restored settings/context/geology differ')
    require(before['chunk']['blocks_sha256'] == reopened['chunk']['blocks_sha256'], 'Restored blocks differ')
    rejection = data['rejection']
    saved, current = rejection['saved_context'], rejection['runtime_context']
    require(set(saved) == set(current) == {'generator','seed','scale','tileSize','dependency','models','backend'}, 'Incomplete contexts')
    require([k for k in saved if saved[k] != current[k]] == ['dependency'], 'Not isolated artifact mismatch')
    require(saved['dependency'] == h['CPU'] and current['dependency'] == h['ALT'], 'Wrong hashes')
    require(saved['models'] == '64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9' and saved['backend'] == 'CPU/Windows 11/amd64', 'Wrong model/backend')
    require(not rejection['ready'] and rejection['process_exited'], 'Did not reject before Ready')
    require(set(data['logs']) == {'console-1.log','console-2.log','console-3.log'}, 'Missing logs')
    for name,digest in data['logs'].items():
        path = source/'artifact'/name
        require(sha(path) == digest, 'Raw log hash differs')
        text = path.read_text(errors='replace')
        require('Stopping server' in text, 'Missing shutdown')
        if name == 'console-2.log':
            require('Geologic Variation is aborting this world:' in text and "Restore this world's original" in text, 'Wrong rejection')
            require('Done (' not in text and 'RCON running on' not in text, 'Late rejection')
            match = re.search(r'Saved: GenerationContext\[(.*?)\]; runtime: GenerationContext\[(.*?)\]',text)
            require(match is not None, 'No raw contexts')
            parsed = [{k:v for k,v in (part.split('=',1) for part in value.split(', '))} for value in match.groups()]
            require(parsed == [saved,current] and 'Terrain diffusion inference: CPU' in text, 'Raw contexts/provider differ')
        else:
            require('Done (' in text and 'Geologic Variation is aborting' not in text, 'Control/reopen failed')
    a,b,c = (data.pop(k) for k in ('before_state','rejected_state','final_state'))
    require(a == b and a['terrain'] == c['terrain'] and a['preserved']['snapshot'] == c['preserved']['snapshot'], 'Preservation failed')
    states = a['terrain']; require(len(states) == 529, 'Unexpected coverage')
    data['preservation'] = {'persisted_chunks':len(states),'statuses':dict(Counter(v['status'] for v in states.values())),
        'chunk_set_status_and_block_containers_sha256':hashlib.sha256(json.dumps(states,sort_keys=True).encode()).hexdigest(),
        'identical_after_rejection_and_reopen':True,'snapshot_sha256':a['preserved']['snapshot'],
        'region_metadata_before':a['preserved']['regions'],'region_metadata_after_rejection':b['preserved']['regions'],
        'region_metadata_after_reopen':c['preserved']['regions']}
    data['raw_results_sha256'] = sha(source/'artifact-results.json')
    text = json.dumps(data,indent=2)+'\n'
    require(all(s not in text for s in ('addon_origin','union:/','C:/Users/','C:\\\\Users','rcon.password')), 'Nonportable evidence')
    return text


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(export(a.source))
