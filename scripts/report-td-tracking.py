"""Render descriptive tables from strictly exported portable evidence."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def report():
    data=json.loads((ROOT/'docs/evidence/td-tracking.json').read_text())
    cases=data['cases'];native=[c for c in cases if c['scale']==1]
    out=['# Bounded TD center and orientation diagnostic (#11)', '',
        '**Diagnostic only: retain actual-target point diagnostics. Geological selection abstains; geology-1 is unchanged.**', '',
        '[Portable evidence](evidence/td-tracking.json), [frozen protocol](td-tracking-protocol.md), and [excluded development attempts](evidence/td-tracking-attempts.json).', '',
        'Main and GitHub were reconciled at e3fdbcf, with merged PRs #47–#51. The selector/evaluator/resource rules were pushed at ecad7da; the transcript-only probe correction was pushed at 2a52336 before either fresh seed was inspected. All previously examined seeds, including 2026110317 and -2026110319, are development data. There was no held-out retuning.', '',
        'New accepted collection uses six serial NEW CPU fixtures: development 8675309 and fresh held-out 2026110407 / -2026110411, each at scales 1/6. Repeated scales and shared native cells are paired observations. Fixed coverage is a diagonal transect, separate from selected features and terrain contrasts; no population-accuracy claim follows.', '',
        '## Geometry and uncertainty', '',
        'The local search uses the top original two-sided coarse candidate per kind. The original strict five-station coarse evaluation remains unchanged. Fine patches contain actual floating TD elevations at 64-native-pixel spacing; they do not substitute analytical terrain. Straight, localized fixed-axis, and turning paths are evaluated separately. All require 50 m on both sides and the original longitudinal range/residual bounds. Full alternatives, reasons, stations and shoulders are portable.', '',
        '| Seed / role | Kind | Strict coarse | Fine straight / localized / tracked | Tracked stations | Center shift (native px) | Axis turn (degrees) | Weakest side (m) |',
        '| --- | --- | --- | --- | ---: | ---: | ---: | ---: |']
    strata=['## Fixed coverage and contrasting terrain', '',
        '| Seed / role | Screen ocean / coast / land | Selected strata present |',
        '| --- | --- | --- |']
    for c in native:
        labels=['ocean' if max(p['evidence']['elevations'])<0 else 'coast' if min(p['evidence']['elevations'])<0 else 'land' for p in c['scan']]
        present={g for p in c['observations'] for g in p['groups']}
        names=('ocean','coast','lowland','intermediate','mountain')
        strata.append(f"| {c['seed']} / {c['split']} | "+' / '.join(str(labels.count(k)) for k in ('ocean','coast','land'))+' | '+', '.join(k if k in present else k+' MISSING' for k in names)+' |')
    strata += ['', 'Ocean/coast/land are signs of nine coarse averages relative to zero, not geological labels or validated fine shoreline exposure. Low/intermediate/high land are selected contrasts, not independent coverage samples. The five fixed coverage points and all twelve boundary points retain their own memberships when locations overlap selected features.', '']
    index=out.index('## Geometry and uncertainty');out[index:index]=strata
    for c in native:
        for a in c['attempts']:
            runs=a['diagnosis']['runs'];t=runs['tracked']
            flags=' / '.join('pass' if runs[k]['supported'] else '**fail**' for k in ('straight','localized','tracked'))
            out.append(f"| {c['seed']} / {c['split']} | {a['candidate']['kind']} | {'pass' if a['legacy_evaluation']['supported'] else '**fail**'} | {flags} | {len(t['stations'])} | {t.get('center_displacement_native_pixels',0):.2f} | {t.get('total_turn_degrees',0):.2f} | {t.get('minimum_prominence_or_depth_metres',float('nan')):.2f} |")
    out += ['', 'Failure reasons and ablation interpretations (native observations only):', '']
    for c in native:
        for a in c['attempts']:
            t=a['diagnosis']['runs']['tracked']
            out.append(f"- {c['seed']} {a['candidate']['kind']}: {a['diagnosis']['interpretation']}; {'; '.join(t['reasons']) or 'all tracked point criteria supported'}.")
    out += ['', 'The localized ablation keeps a fixed shoulder axis but may recenter at each station: it cannot uniquely distinguish a translated straight ridge from a gently curving centerline that retains that axis. Axis-turn limits constrain discrete sampled orientations, not a reconstructed continuous tangent field. Axis choices also change shoulder/step length from 256 to 362 pixels; this is not a controlled constant-bandwidth rotation experiment. The residual is linear in station index, preserving the original arithmetic rather than fitting an arc-length detrend. Greedy tracking never backtracks through a second branch. Failure of all ablations is not proof of genuine interruption. Unresolved center/orientation alternatives, finite search limits and between-grid extrema remain competing explanations.', '',
        'Localization quantization is +/-32 native pixels per axis (45.26 radial); this is not a confidence interval. Additional between-grid and competing-center uncertainty remains. Initial displacement is bounded at 256 pixels; later searches are radius128 and constrained within256 of each original straight station. Edge winners abstain. Comparable alternatives within50 m and >128 pixels transversely or >45 degrees apart abstain as branches/intersections. Missing paths, slopes, saddles, excess range/residual or turning remain failures. Fine point support does not establish a geological origin.', '',
        'Analytical controls are separate: diagonal ridges/basins pass; slopes, saddles, flat fields, edge winners and competing parallel centers abstain. A perfect cardinal ridge can also abstain because unequal discrete axis lengths tie on transverse prominence and trigger orientation ambiguity. This conservative false negative is preserved, not tuned away on examined terrain. Neither analytic success nor this selector limitation establishes actual TD feature coverage.', '',
        '![Fine-point fields and ablation paths](evidence/td-tracking.png)', '',
        '## Matched means and scaled fine tiles', '',
        '| Seed | Kind | Native-cell mean continuity | Tile scale1 / scale6 continuity | Native weakest side / range / residual (m) |',
        '| --- | --- | --- | --- | --- |']
    for c in native:
        paired=next(x for x in cases if x['seed']==c['seed'] and x['scale']==6)
        for i,p in enumerate(c['fine_profiles']):
            n=p['assessments'].get('native_cell');t=p['assessments'].get('scaled_tile');u=paired['fine_profiles'][i]['assessments'].get('scaled_tile')
            flag=lambda x:'pass' if x and x['supported'] else '**fail / absent**'
            residual='incomplete' if not n or n['longitudinal_linear_residual_metres'] is None else f"{n['longitudinal_linear_residual_metres']:.2f}"
            values='absent' if not n else f"{n['minimum_prominence_or_depth_metres']:.2f} / {n['longitudinal_range_metres']:.2f} / {residual}"
            out.append(f"| {c['seed']} | {p['kind']} | {flag(n)} | {flag(t)} / {flag(u)} | {values} |")
    out += ['', f"Frozen new coverage gate: **{'PASS' if data['decision']['tracked_morphology_coverage_passed'] else 'FAIL'}**. It requires a ridge AND basin on BOTH fresh seeds, with unambiguous tracked points, native-cell means and scaled tiles at BOTH scales. This is a separate descriptive gate; no output-changing policy is adopted.", '',
        'Full native-cell means summarize65536 floating elevations. Coarse3x3 neighborhood range is a different support statistic. Scaled256-world-block tiles retain25 quantized sample heights; at scale6 their native footprint is smaller. Fine-cell relief and fine-tile relief remain separate from all means and from coarse range. No p5 or geology-1 cutoff is transferred.', '',
        '## Terrain agreement and boundaries', '',
        'Mean absolute central coarse versus matched-target fine-cell error, in metres; each policy remains compared with the actual target. Scales6 are excluded from these native support counts. Selected features and overlapping strata are correlated.', '',
        '| Seed / group | Rows | Province anchor | Actual target | Fixed grid4 |',
        '| --- | ---: | ---: | ---: | ---: |']
    for c in native:
        for group in ('coverage','contrasts','features'):
            m=c['terrain_agreement'][group]
            if m:
                out.append(f"| {c['seed']} / {group} | {m['target']['n']} | "+' | '.join(f"{m[p]['target_mean_absolute_error_metres']:.2f}" for p in ('province_anchor','target','fixed_grid_4'))+' |')
    out += ['', '| Seed / scale | Coarse/grid contacts / province contacts | Max anchor / target coarse jump (m) | Max tile jump (m) |',
        '| --- | --- | --- | ---: |']
    for c in cases:
        b=c['boundary_evaluation']
        out.append(f"| {c['seed']} / {c['scale']} | 4 / {sum(x['province_changed'] for x in b[-2:])} | {max(x['central_mean_jumps_metres']['province_anchor'] for x in b):.2f} / {max(x['central_mean_jumps_metres']['target'] for x in b):.2f} | {max(x['target_tile_mean_jump_metres'] for x in b):.2f} |")
    out += ['', 'Boundary jumps describe changed statistical support, not one-block physical cliffs. Province contacts are independently located and required to change the Java-reported province. Actual-target support is distinguished from province-anchor support in every paired comparison:', '']
    for pair in data['paired_support']:
        counts=pair['policies'];out.append(f"- Seed {pair['seed']}: " + '; '.join(f"{p}: {m['matching_hashes']}/{m['matched_support']} hashes on matching support, {len(m['differing_support'])} differing supports" for p,m in counts.items())+f"; full native patch hashes match: {pair['patch_hashes_match']}.")
    out += ['', '## Requests, traversal and cache limits', '',
        '| Seed / scale | Unique comparisons | Deduplicated coarse / native misses forward | Forward / reverse new windows | All post-startup C/D/H/W | Native LRU peak |',
        '| --- | ---: | --- | --- | --- | ---: |']
    for c in cases:
        a=c['request_accounting'];d=c['post_startup_delta']
        out.append(f"| {c['seed']} / {c['scale']} | {len(c['observations'])} | {a['expected_deduplicated_coarse_requests']} / {a['expected_deduplicated_native_fine_requests']} | {a['forward_actual_delta']['computed_windows']} / {a['reverse_actual_delta']['computed_windows']} | "+'/'.join(str(d[k]) for k in ('coarse_calls','pipeline_data_calls','heightmap_calls','computed_windows'))+f" | {a['max_retained_fine_entries']} |")
    u=data['units']
    out += ['', f"{u['forward_comparisons']} forward world-location comparisons and the same number reversed cover {u['distinct_seed_native_targets']} distinct seed/native target cells. Twelve forward patch grids represent {u['distinct_seed_native_patches']} distinct seed/native patches; reverse recomputation is additional paired work, not new coverage. The fixed screen has486 rows, representing243 seed/native cells.", '',
        'C/D/H/W means public coarse / direct-data / heightmap calls / newly computed windows. Each fixture makes four direct patch-data misses, serving196 row commands through a one-entry patch cache; none of those row hits imply new model requests. Fine comparison misses are independently replayed against cleared128-entry coarse/native LRUs forward and reverse. Two uncached tile reads occur per comparison. Window counts for patches, screen and suites are retained jointly in post-startup totals; they are not isolated patch/policy timings. Startup counters remain separate in JSON.', '',
        'All returned comparison evidence and reverse patch values/full hashes must match after explicit cache clear. Provider tensors can remain warm; this is traversal evidence, not fresh-process final-block determinism. The real coarse suite requires four concurrent callers to produce one public request,129 misses to retain128 entries and recompute eviction. Native-cache eviction is not claimed merely because its cap is128. All collection runs remain bounded by52 forward/reverse comparisons,12000 post-startup windows,6GiB heap,360s startup,300s command,45min fixture,4h matrix and disk reserve guards.', '',
        '## Preserved failures, scope and remaining gate', '',
        'PR51’s frozen strict exporter is unchanged and still rejects its retained matrix with **Paired coarse drift**. Its morphology coverage gate remains **failed**. The separate negative exporter first requires that original rejection, then repeats strict source/artifact/transcript checks. This slice neither weakens those assertions nor changes geology-1 to make displaced province anchors correspond.', '',
        'New work: frozen selector/analytical controls, six CPU sampling fixtures, fine point patches and profiles, exact reverse recomputation, coarse concurrency/eviction/oracles, per-fixture snapshot-byte checks, model/template unchanged checks, source/artifact/log export and request accounting. The production addon is byte-identical to main; every prior probe entry is unchanged and only TrackingPatch.class is added. CI runs build/resource/domain/semantic/portable replay checks; inference runs locally.', '',
        'Reused work: #47 coarse prototype/original-artifact restoration and save/reopen guards; #48/#49 terrain diagnostics/source-byte portability; #50 actual-target/native-cell support and save/reopen evidence; #51 failed strict profiles and cross-scale anchor evidence. Their original strict exports reproduce committed JSON. Their complete sampled blocks and529 persisted-container/reopen checks are retained acceptance, not newly executed by this sampling-only slice. #5’s stronger failed final-block assertion remains failed; historical route timing is separate.', '',
        'Excluded attempts: -01 failed a sandbox hardlink before launch; -02 exposed omitted patch transcript logging on development data and was manually stopped (hung shutdown required termination); -03 hit the frozen disk guard and shut down normally. No fresh seed was inspected in these attempts. Only stopped new-fixture ONNX caches were removed. The user freed disk space before the unchanged accepted -04 restart. Excluded attempts have no complete new-window counter endpoint, so model-return log rows are not substituted for new-window counts.', '',
        'Remaining gate: demonstrate unambiguous independently localized actual TD ridges AND basins, finite two-sided continuity and matched-native/scaled-tile support under a newly frozen protocol on new held-out seeds if this gate fails. The now-examined fresh seeds become development data for any revision. A finer or wider search is not silently substituted here. Independent geological plausibility, history and contact-coherence/calibration remain separate even if morphology succeeds. Competing geological interpretations remain seeded synthetic hypotheses with uncertainty and abstention, never recovered geological history.', '',
        'No palettes, dikes, minerals or integrations. Ulti-World stays optional. #9/#11 stay open. Any future output adoption still needs immutable generator identity, explicit new-world-only selection, genuine bidirectional continuing-save rejection, exact original-artifact restoration/reopen and complete snapshot/block/persisted-container preservation. Never migrate continuing geology-1 snapshots. Integrated candidates additionally need alternating paired CPU startup/cold/warm/full-route benchmarks on NEW fixtures. Isolated-query savings are not route savings.', '',
        '## Reproduction', '', '```powershell',
        './scripts/bootstrap.ps1', './gradlew.bat build runtimeProbeJar',
        'python scripts/test-td-tracking.py',
        'python scripts/verify-td-tracking.py --java <java21> --td <pinned-cpu-jar> --baseline <retained-main-addon> --protocol-commit 2a52336fb926a89e15e13940cd2fddd339341e0d --output <NEW-directory>',
        'python scripts/summarize-td-tracking.py <NEW-directory> --output <portable-json>',
        'python scripts/reexport-retained-terrain.py', '```', '',
        'Raw accepted matrix: runs/acceptance/td-tracking-2026-11-04-04. Strict re-export after the final Windows checkout is required; LF attributes preserve exact executed source bytes. Portable replay is not a replacement for artifact/source/raw transcript verification.']
    return '\n'.join(out)+'\n'


if __name__=='__main__':(ROOT/'docs/td-tracking.md').write_text(report())
