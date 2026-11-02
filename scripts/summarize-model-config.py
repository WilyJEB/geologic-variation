"""Recheck raw config-substitution logs, contexts and terrain, then export portable evidence."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

h = runpy.run_path(str(Path(__file__).with_name('verify-model-config.py')))
require = h['require']; sha = h['runtime']['sha']


def export(source):
    data = json.loads((source/'model-config-results.json').read_text())
    require(data['fixture_unchanged'] and data['shared_inputs_unchanged'], 'Shared input preservation failed')
    launches = data['launches']
    require(len(launches) == len({v['pid'] for v in launches}) == 3, 'Not three independent launches')
    require(all(v['free_bytes_before'] >= 2*1024**3 for v in launches), 'Insufficient disk')
    require(all(v['exit_code'] == 0 for v in launches), 'Process exit differs')
    original,changed,restored = (data[k] for k in ('original_inputs','substituted_inputs','restored_inputs'))
    require(original == restored, 'Inputs not restored')
    require(original['mods'] == changed['mods'] and original['config'] == changed['config'], 'Artifact/config switch changed')
    require([k for k in original['assets'] if original['assets'][k] != changed['assets'][k]] == [h['ASSET']], 'Wrong asset substitution')
    require(original['assets'] == {k:v['sha256'] for k,v in data['manifest']['assets'].items()}, 'Original assets unverified')
    case = source/'model-config'
    require(h['hot']['manifest'](case/'mods') == restored['mods'], 'Retained runtime artifacts differ')
    require(h['hot']['manifest'](case/'config') == restored['config'], 'Retained runtime config differs')
    require({k:sha(case/'terrain-diffusion-models'/k) for k in restored['assets']} == restored['assets'], 'Retained assets differ')
    raw = (case/'terrain-diffusion-models'/h['ASSET']).read_bytes()
    alternate = raw.replace(b'"residual_mean": 0.0', b'"residual_mean": 1.0')
    require(raw != alternate and hashlib.sha256(alternate).hexdigest() == changed['assets'][h['ASSET']], 'Alternate derivation differs')
    require(data['derivation'] == {'asset':h['ASSET'],'field':'residual_mean','original':0.0,'alternate':1.0,
                                  'kind':'test-derived custom config, not an official alternate model'}, 'Provenance claim differs')
    require(list(original['mods'].values()).count(h['CPU']) == 1, 'Wrong TD distribution')
    require('validate_model=false' in (case/'config/terrain-diffusion-mc.properties').read_text(), 'Unsupported selection mechanism')
    before,reopened = data['before'],data['reopened']
    require(before['settings'] == reopened['settings'] and before['region'] == reopened['region'], 'Restored settings/geology differs')
    require(before['chunk']['blocks_sha256'] == reopened['chunk']['blocks_sha256'] == '09163724065ec1385a0c43dcdc739a3673b63c596ade17041a46fb8f20383a00', 'Sample changed')
    rejection = data['rejection']; saved,current = rejection['saved_context'],rejection['runtime_context']
    require(set(saved) == set(current) == h['FIELDS'], 'Incomplete contexts')
    require([k for k in saved if saved[k] != current[k]] == ['models'], 'Wrong mismatch')
    require(saved == h['context'](before['settings']['context']), 'Control/rejection context differs')
    require(saved['models'] == h['aggregate'](original['assets']) and current['models'] == h['aggregate'](changed['assets']), 'Model aggregate differs')
    require(saved['dependency'] == h['CPU'] and saved['backend'] == 'CPU/Windows 11/amd64', 'Wrong pinned environment')
    require(not rejection['ready'] and rejection['process_exited'], 'Did not reject before Ready')
    require(set(data['logs']) == {'console-1.log','console-2.log','console-3.log'}, 'Missing logs')
    for name,digest in data['logs'].items():
        path = case/name; require(sha(path) == digest, 'Raw log hash differs')
        text = path.read_text(errors='replace')
        value = '1.0' if name == 'console-2.log' else '0.0'
        require(re.findall(r'TD_MODEL_CONFIG residual_mean=([\d.]+) native_resolution=30.0 latent_compression=8',text) == [value], 'Actual loaded config differs')
        require('Terrain diffusion inference: CPU' in text and 'Stopping server' in text, 'CPU/shutdown missing')
        require('Terrain-diffusion ML models loaded in' in text, 'Models failed initialization')
        if name == 'console-2.log':
            require('Geologic Variation is aborting this world:' in text and "Restore this world's original" in text, 'Wrong diagnostic')
            require('Done (' not in text and 'RCON running on' not in text, 'Late rejection')
            match = re.search(r'Saved: GenerationContext\[(.*?)\]; runtime: GenerationContext\[(.*?)\]',text)
            require(match is not None, 'No raw contexts')
            require([h['context']('GenerationContext['+v+']') for v in match.groups()] == [saved,current], 'Raw contexts differ')
            require(text.index('TD_MODEL_CONFIG residual_mean=1.0') < text.index('Geologic Variation is aborting'), 'Config loaded after rejection')
            require(text.index('Terrain diffusion inference: CPU') < text.index('Geologic Variation is aborting'), 'Native initialization did not precede guard')
            require('TD_REQUEST caller=addon-anchor' not in text, 'Geology entered heightmap route')
        else:
            require('Done (' in text and 'Geologic Variation is aborting' not in text, 'Control/reopen failed')
    a,b,c = (data.pop(k) for k in ('before_state','rejected_state','final_state'))
    require(a['terrain'] == b['terrain'] == c['terrain'], 'Terrain preservation failed')
    require(a['snapshot_fields'] == b['snapshot_fields'] == c['snapshot_fields'], 'Snapshot fields changed')
    require({k:a['snapshot_fields'][k] for k in h['FIELDS']} == saved, 'Saved context differs')
    require(a['preserved']['snapshot'] == b['preserved']['snapshot'] == c['preserved']['snapshot'] == 'c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d', 'Snapshot bytes changed')
    require(h['hot']['live']['terrain'](case/'world') == c['terrain'], 'Retained terrain differs')
    require(len(a['terrain']) == 529, 'Unexpected coverage')
    data['preservation'] = {'persisted_chunks':len(a['terrain']), 'statuses':dict(Counter(v['status'] for v in a['terrain'].values())),
        'chunk_set_status_and_block_containers_sha256':hashlib.sha256(json.dumps(a['terrain'],sort_keys=True).encode()).hexdigest(),
        'identical_after_rejection_and_reopen':True,'snapshot_sha256':a['preserved']['snapshot'], 'snapshot_fields':a['snapshot_fields'],
        'region_metadata_before':a['preserved']['regions'], 'region_metadata_after_rejection':b['preserved']['regions'],
        'region_metadata_after_reopen':c['preserved']['regions']}
    data['raw_results_sha256'] = sha(source/'model-config-results.json')
    text = json.dumps(data,indent=2)+'\n'
    require(all(s not in text for s in ('addon_origin','union:/','C:/Users/','C:\\\\Users','rcon.password')), 'Nonportable evidence')
    return text


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('source',type=Path); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); a.output.write_text(export(a.source))
