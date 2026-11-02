"""Validate raw hot-reload evidence and export portable observations and hashes."""
import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path
import runpy

h = runpy.run_path(str(Path(__file__).with_name('verify-hot-config.py')))
require = h['require']; sha = h['runtime']['sha']


def export(source):
    data = json.loads((source/'hot-config-results.json').read_text())
    require(len(data['cases']) == 2 and {c['name'] for c in data['cases']} == {'cached','uncached'}, 'Incomplete matrix')
    require(data['fixture_unchanged'], 'Fixture changed')
    for c in data['cases']:
        before, after, reopened = (c[k] for k in ('before','after','reopened'))
        require(c['exit_code'] == 0 and len(set(c['pids'])) == 2, 'Missing clean fresh-process reopen')
        require(c['artifacts']['geologic-variation-0.2.2-dev.jar'] == '39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226', 'Addon changed')
        context = before['settings']['context']
        for pin in ('dependency=3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8',
                    'models=64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9', 'backend=CPU/Windows 11/amd64'):
            require(pin in context, 'Context pin mismatch')
        require(before['settings']['active'] == before['settings']['requested'] != h['EXPECTED'], 'Wrong initial proposals')
        require(after['settings'] == reopened['settings'] == {**before['settings'], 'requested':h['EXPECTED']}, 'Settings/context changed')
        require(before['region'] == after['region'] == reopened['region'] == c['query']['region'], 'Geology changed')
        require(before['chunk']['blocks_sha256'] == after['chunk']['blocks_sha256'] == reopened['chunk']['blocks_sha256'], 'Blocks changed')
        require(any(k.startswith('geologic_variation:') and v > 0 for k,v in before['chunk']['counts'].items()), 'Empty sample')
        require(c['events'] and all(e['watcher_stack'] and e['spec_matches'] and e['type'] == 'COMMON'
                    and e['event'] == 'net.neoforged.fml.event.config.ModConfigEvent$Reloading'
                    and e['requested'] == h['EXPECTED'] for e in c['events']), 'Missing watcher event')
        require(c['query']['entries_before'] == (1 if c['name'] == 'cached' else 0) and c['query']['entries_after'] == 1, 'Wrong cache arm')
        require(c['query']['heightmap_calls'] == 0 if c['name'] == 'cached' else c['query']['heightmap_calls'] > 0, 'Cache route unproved')
        states = c.pop('terrain_before')
        require(states and states == c.pop('terrain_saved') == c.pop('terrain_reopened'), 'Persisted terrain/coverage changed')
        require(len({c[k]['snapshot'] for k in ('preserved_before','preserved_saved','preserved_reopened')}) == 1, 'Snapshot changed')
        require(c['config_before_sha256'] != c['config_after_sha256'], 'Config not edited')
        require(set(c['logs']) == {'console-1.log','console-2.log'}, 'Missing logs')
        for name,digest in c['logs'].items():
            path = source/c['name']/name
            require(sha(path) == digest, 'Raw log changed')
            text = path.read_text(errors='replace')
            require('Stopping server' in text and 'Done (' in text, 'Missing lifecycle evidence')
            require('Geologic Variation is aborting' not in text, 'Unexpected geology failure')
            if name == 'console-1.log':
                require('HOT_CONFIG ' in text and 'Saved world settings remain active; edits apply only to new worlds.' in text, 'Missing reload/warning log')
                observed = [json.loads(s) for s in re.findall(r'HOT_CONFIG (\{.*\})',text)]
                require(observed and all(e['watcher_stack'] and e['spec_matches'] and e['requested'] == h['EXPECTED'] for e in observed), 'Unexpected late reload')
                require(observed[:len(c['events'])] == c['events'], 'Event observations disagree with log')
                c['all_logged_reload_events'] = observed
        c['terrain_preservation'] = {'persisted_chunks':len(states), 'statuses':dict(Counter(v['status'] for v in states.values())),
            'chunk_set_status_and_block_containers_sha256':hashlib.sha256(json.dumps(states,sort_keys=True).encode()).hexdigest(),
            'identical_after_save_and_reopen':True}
    data['raw_results_sha256'] = sha(source/'hot-config-results.json')
    return data


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    a.output.write_text(json.dumps(export(a.source),indent=2)+'\n')
