"""Export portable acceptance evidence without credentials, local absolute paths or worlds."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {k:clean(v) for k,v in value.items() if k != 'addon_origin'}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def summarize(root):
    results = {}
    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        for source in sorted(folder.glob('*-results.json')):
            if folder.name == 'repro-02':
                continue  # Exploratory ocean-only sample, explicitly not accepted evidence.
            rows = json.loads(source.read_text())
            if not rows or not isinstance(rows[0], dict):
                results[folder.name] = clean(rows)
                continue
            exported = []
            for row in rows:
                item = clean(row)
                case = folder / row['name']
                item['artifact_hashes'] = {p.name:sha(p) for p in sorted((case/'mods').glob('*.jar'))}
                item['logs'] = {p.name:sha(p) for p in sorted(case.glob('console-*.log'))}
                if 'addon_origin' in str(row):
                    item['packaged_origin_confirmed'] = all('/mods/geologic-variation-' in r['addon_origin']
                        for r in row.get('regions', []))
                if row['name'].startswith('performance'):
                    item['route_generation_ms'] = sum(c['generation_ms'] for c in row['chunks'])
                    lines = (case/'console-1.log').read_text(errors='replace').splitlines()
                    # Stop after timed chunks and their warm read, before remote-query experiments.
                    chunk_results = 0
                    calls, uncached = [], []
                    for line in lines:
                        match = re.search(r'TD_REQUEST caller=(\S+) x=(-?\d+) z=(-?\d+) width=(\d+) height=(\d+) wall_ms=([\d.]+)',line)
                        if match:
                            caller,x,z,width,height,ms = match.groups()
                            if float(ms) >= 10:
                                calls.append({'caller':caller,'x':int(x),'z':int(z),'width':int(width),'height':int(height),'wall_ms':float(ms)})
                        if 'uncached region requested:' in line:
                            uncached.append(line.split('uncached region requested: ',1)[1])
                        if 'ACCEPTANCE {' in line and '"kind":"chunk"' in line:
                            chunk_results += 1
                            if chunk_results == len(row['chunks'])+1:
                                break
                    item['timed_heightmap_calls_over_10_ms'] = calls
                    item['timed_uncached_td_regions'] = uncached
                exported.append(item)
            results[folder.name] = exported
    perf = results.get('perf-01', [])
    if perf:
        pairs=[]
        for trial in range(3):
            baseline=next(r for r in perf if r['trial']==trial and not r['addon'])
            addon=next(r for r in perf if r['trial']==trial and r['addon'])
            pairs.append({'trial':trial,'td_only_ms':baseline['route_generation_ms'],
                          'addon_ms':addon['route_generation_ms'],
                          'difference_ms':addon['route_generation_ms']-baseline['route_generation_ms']})
        results['performance_summary']={'pairs':pairs,'median_paired_difference_ms':statistics.median(p['difference_ms'] for p in pairs)}
    diff=root/'repro-03/scale6-final-diff.json'
    if diff.exists():
        results['scale6_final_difference']=json.loads(diff.read_text())
    for name, relative in [('scale1_final_difference','repro-03/scale1-final-diff.json'),
                           ('scale6_td_only_final_difference','order-control-01/scale6-td-only-final-diff.json')]:
        path=root/relative
        if path.exists():
            results[name]=json.loads(path.read_text())
    repro=results.get('repro-03',[])
    status={}
    keyed=lambda rows:{(c['x'],c['z']):c['geology_sha256'] for c in rows}
    for scale in sorted({r['scale'] for r in repro}):
        pair=[r for r in repro if r['scale']==scale]
        if len(pair)!=2:
            status[str(scale)]={'complete_pair':False}
            continue
        status[str(scale)]={
            'complete_pair':True,
            'positioned_regional_blocks_equal':keyed(pair[0]['chunks'])==keyed(pair[1]['chunks']),
            'region_records_equal':[r['region'] for r in pair[0]['regions']]==[r['region'] for r in pair[1]['regions']],
            'snapshots_unchanged':all(r['snapshot_before']==r['snapshot_after'] for r in pair),
            'reopened_regional_blocks_equal':all(keyed(r['chunks'])==keyed(r['reopened']) for r in pair),
            'new_neighbors_equal':pair[0]['neighbor']['geology_sha256']==pair[1]['neighbor']['geology_sha256'],
            'nonempty_regional_samples':all(any(any(k.startswith('geologic_variation:') for k in c['counts']) for c in r['chunks']) for r in pair)}
    results['strict_reproducibility_status']=status
    smoke={}
    for name in ('packaged-01','packaged-02'):
        case=root/name/'packaged-smoke'
        if case.exists():
            smoke[name]={'artifacts':{p.name:sha(p) for p in sorted((case/'mods').glob('*.jar'))},
                         'logs':{p.name:sha(p) for p in sorted(case.glob('console-*.log'))},
                         'snapshot_sha256':sha(case/'world/data/geologic_variation-geology.properties')}
    client=root/'packaged-client-01'
    if client.exists():
        smoke['client']={'artifacts':{p.name:sha(p) for p in sorted((client/'mods').glob('*.jar'))},
                         'console_sha256':sha(client/'console.log')}
    results['packaged_smoke']=smoke
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summarize(args.root),indent=2)+'\n')
