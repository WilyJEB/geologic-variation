"""Validate and export portable live-context evidence, excluding local paths/credentials."""
import argparse
import json
from pathlib import Path
import runpy
import hashlib
from collections import Counter

h=runpy.run_path(str(Path(__file__).with_name('verify-live-context.py')))


def export(source, expected_addon='39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226'):
    data=json.loads((source/'live-results.json').read_text())
    h['require']({c['name'] for c in data['cases']}=={f'{f}-{r}' for f in ('seed','scale') for r in ('cached','uncached')},'Incomplete matrix')
    for c in data['cases']:
        live=c['live'];field,route=c['name'].split('-')
        h['require'](c['artifacts']['geologic-variation-0.2.2-dev.jar']==expected_addon,'Addon changed')
        h['require'](c['saved_context']['dependency']=='3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8','TD pin mismatch')
        h['require'](c['saved_context']['models']=='64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9' and c['saved_context']['backend']=='CPU/Windows 11/amd64','Model/backend mismatch')
        h['require'](live['rejected'] and live['heightmap_calls_after_edit']==0,'Query guard failed')
        if expected_addon!='39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226':
            h['require']('pipeline_data_calls_after_edit' in live,'Missing elevation-entry instrumentation')
        h['require'](live.get('pipeline_data_calls_after_edit',0)==0,'Elevation API entered after edit')
        h['require'](live['cache_entries_before_edit']==(1 if route=='cached' else 0),'Wrong cache route')
        h['require'](c['terrain_before'] and c['terrain_before']==c['terrain_after_rejection'],'Terrain changed')
        if 'terrain_restored' in c:
            h['require'](c['terrain_before']==c.pop('terrain_restored'),'Restored terrain changed')
            c['restored_terrain_matches']=True
        h['require'](c['preserved_before']['snapshot']==c['preserved_after_rejection']['snapshot'],'Snapshot changed')
        h['require']([k for k in c['saved_context'] if c['saved_context'][k]!=c['runtime_context'][k]]==[field],'Wrong mismatch')
        h['require'](c['before']['region']==c['restored']['region']==live['expected_region'],'Restoration differs')
        h['require'](c['before']['chunk']['blocks_sha256']==c['restored']['chunk']['blocks_sha256'],'Restored blocks differ')
        for name,digest in c['logs'].items():
            h['require'](h['runtime']['sha'](source/c['name']/name)==digest,'Raw log changed')
        states=c.pop('terrain_before');c.pop('terrain_after_rejection')
        c['terrain_preservation']={'persisted_chunks':len(states),'statuses':dict(Counter(v['status'] for v in states.values())),
            'chunk_set_status_and_block_containers_sha256':hashlib.sha256(json.dumps(states,sort_keys=True).encode()).hexdigest(),
            'identical_after_rejection':True}
    data['raw_results_sha256']=h['runtime']['sha'](source/'live-results.json')
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expected-addon-sha256',default='39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226')
    a=p.parse_args();a.output.write_text(json.dumps(export(a.source,a.expected_addon_sha256),indent=2)+'\n')
