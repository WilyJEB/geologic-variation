"""Validate raw multi-seed evidence and export an explicitly diagnostic classifier."""
import argparse
import json
import math
from pathlib import Path
import runpy
import statistics

d = runpy.run_path(str(Path(__file__).with_name('verify-terrain-diagnostics.py')))
require = d['require']; sha = d['r']['sha']


def classify(evidence):
    """Only sign-based terrain tendency is supported; abstain from rock selection."""
    values = evidence['elevations']
    require(len(values) == 9 and all(math.isfinite(v) for v in values), 'Unavailable elevation')
    require(evidence['p5_used'] is False, 'p5 must remain excluded')
    tendency = d['tendency'](evidence)
    hypotheses = {'ocean':['marine sedimentary domain','mafic oceanic domain'],
                  'coast':['sedimentary margin','exposed inherited belt'],
                  'land':['sedimentary platform','uplifted or intrusive belt']}
    return {'terrain_tendency':tendency, 'synthetic_geological_hypotheses':hypotheses[tendency],
            'geological_confidence':'unestablished', 'stone_selection':None,
            'basis':'signs of nine coarse average elevations relative to zero datum', 'p5_used':False}


def export(source):
    data = json.loads((source/'results.json').read_text())
    require(data['shared_inputs_unchanged'], 'Inputs changed')
    require(data['production_sha256'] == data['baseline_sha256'], 'Production changed')
    require(len(data['cases']) == 4 and {(c['seed'],c['scale']) for c in data['cases']} ==
            {(s,k) for s in (-1550453200536840819,8675309) for k in (1,6)}, 'Incomplete matrix')
    for name,digest in data['sources'].items():
        require(sha(Path(__file__).with_name(name)) == digest, 'Executed source changed: '+name)
    observations = []
    for case in data['cases']:
        mods = source/case['name']/'mods'
        for pattern,digest in [('geologic-variation-*.jar',data['production_sha256']),
                               ('geology-runtime-probe-*.jar',data['probe_sha256']),
                               ('NeoForge-terrain-diffusion-*.jar','3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8')]:
            paths = list(mods.glob(pattern))
            require(len(paths) == 1 and sha(paths[0]) == digest, 'Runtime artifact changed')
        for name,digest in case['logs'].items():
            require(sha(source/case['name']/name) == digest, 'Raw log changed')
        require(case['exit_code'] == 0 and case['terrain_snapshot_unchanged'] and case['persisted_records'] > 0,
                'Incomplete persistence verification')
        require(case['sample']['blocks_sha256'] == case['reopened']['blocks_sha256'], 'Complete sample changed')
        suite = case['suite']
        require(suite['concurrent_requests'] == 1 and suite['real_cache_entries'] == 128 and
                suite['traversal_equal'] and suite['evicted_recomputed'] and case['traversal_equal'] and case['oracle']['equal'],
                'Cache/traversal/oracle failed')
        require(len(case['scan']) == 81 and set(case['selected']) == {'ocean','coast','lowland','mountain'}, 'Incomplete survey')
        require(case['selected'] == d['select'](case['scan']), 'Selection changed')
        case['stratum_counts'] = {label:sum(d['tendency'](p['evidence']) == label for p in case['scan'])
                                  for label in ('ocean','coast','land')}
        for row in case['comparisons'] + case['boundaries']:
            row['diagnostic_classification'] = classify(row['coarse'])
            row['range_minus_fine_relief_metres'] = row['coarse']['neighborhood_range_metres']-row['fine_tile_relief_metres']
            if 'stratum' in row:
                survey = case['selected'][row['stratum']]['evidence']
                row['survey_classification'] = classify(survey)
                row['survey_minus_anchor_mean_metres'] = survey['mean_metres']-row['coarse']['mean_metres']
        observations.extend(case['comparisons'])
    data['diagnostic_classifier'] = {'identity':'terrain-tendency-diagnostic-1', 'production_caller':False,
        'new_world_selection':False, 'immutable_generator_adopted':False,
        'decision':'diagnostic only; geological confidence and lithology calibration absent',
        'warning':'Neighborhood range and fine-tile relief have different spatial support; no shared thresholds.'}
    data['summary'] = {'selected_comparisons':len(observations),
        'survey_anchor_tendency_disagreements':sum(v['survey_classification']['terrain_tendency'] !=
            v['diagnostic_classification']['terrain_tendency'] for v in observations),
        'coarse_range_metres':[min(v['coarse']['neighborhood_range_metres'] for v in observations),
                               max(v['coarse']['neighborhood_range_metres'] for v in observations)],
        'fine_relief_metres':[min(v['fine_tile_relief_metres'] for v in observations),max(v['fine_tile_relief_metres'] for v in observations)],
        'median_range_minus_fine_relief_metres':statistics.median(v['range_minus_fine_relief_metres'] for v in observations)}
    data['raw_results_sha256'] = sha(source/'results.json')
    data['exporter_sha256'] = sha(Path(__file__))
    def scrub(value):
        if isinstance(value,dict): return {k:scrub(v) for k,v in value.items() if k != 'addon_origin'}
        if isinstance(value,list): return [scrub(v) for v in value]
        return value
    return scrub(data)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.output.write_text(json.dumps(export(args.source),indent=2)+'\n')
