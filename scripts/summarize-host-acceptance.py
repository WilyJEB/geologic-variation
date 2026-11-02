"""Export stage and host fixture evidence, with final scale-6 saved-block comparisons."""
import argparse
import json
from pathlib import Path
import runpy

HERE = Path(__file__).parent
compare = runpy.run_path(str(HERE/'compare-runtime-chunks.py'))['compare']
clean = runpy.run_path(str(HERE/'summarize-runtime-acceptance.py'))['clean']


def summarize(stages, fixtures, audit):
    rows = json.loads((stages/'stage-results.json').read_text())
    if len(rows)!=8:
        raise ValueError('Expected eight stage worlds')
    results = {'stage_cases':clean(rows),
               'stage_comparisons':json.loads((stages/'comparisons.json').read_text()),
               'fixtures':json.loads((fixtures/'fixture-results.json').read_text()),
               'resource_audit':json.loads(audit.read_text()),'saved_scale6_comparisons':{}}
    for result in results['stage_comparisons']:
        if result['stage']!='full' and (not all(result['normalized_addon_vs_td_only']) or
            not all(arm['full_states_equal'] for arm in result['traversal'].values())):
            raise ValueError('Surface/carver preservation assertion failed')
    hosts = {'geologic_variation:'+name for name in ('limestone','slate','quartzite','gabbro')}
    for row in rows:
        for stage,chunks in row['stages'].items():
            if len(chunks)!=4:
                raise ValueError('Incomplete chunk sample')
            for chunk in chunks:
                regional = {name for name in chunk['counts'] if name.startswith('geologic_variation:')}
                if not regional.issubset(hosts) or (row['addon'] and stage=='surface' and not regional):
                    raise ValueError('Unexpected or empty regional hosts')
    # Scale-1 trial-0 addon world in the first run also hosted a destructive fixture
    # AFTER its stage measurements. Do not compare that modified save as natural terrain.
    for addon in (False,True):
        pair = [r for r in rows if r['scale']==6 and r['addon']==addon]
        coords = pair[0]['plan']['chunks']
        results['saved_scale6_comparisons']['addon' if addon else 'td_only'] = compare(
            stages/pair[0]['name']/'world',stages/pair[1]['name']/'world',coords)
    return results


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stages',type=Path)
    parser.add_argument('fixtures',type=Path)
    parser.add_argument('audit',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(summarize(args.stages,args.fixtures,args.audit),indent=2)+'\n')
