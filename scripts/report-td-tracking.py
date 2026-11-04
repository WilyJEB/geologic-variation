"""Render descriptive tables from strictly exported portable evidence."""
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def report():
    data=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text())
    cases=data['cases'];native=[c for c in cases if c['scale']==1]
    profiles=runpy.run_path(str(ROOT/'scripts/audit-td-tracking-profiles.py'))['audit'](data)
    full=sum(p['tracked_two_sided_stations']==5 for p in profiles['rows'])
    supported=sum(a['diagnosis']['runs']['tracked']['supported'] for c in native for a in c['attempts'])
    out=['# Bounded TD center and orientation diagnostic (#11)', '',
        '**Diagnostic only: retain actual-target point diagnostics. Geological selection abstains; geology-1 is unchanged.**', '',
        f"{full}/{len(profiles['rows'])} native candidate attempts contain five qualifying two-sided fine-point stations after tracking; {supported}/{len(profiles['rows'])} pass all frozen point-path criteria. Partial recovery is not complete continuity. Failed finite greedy searches do not establish genuine physical interruption.", '',
        '[Portable evidence](evidence/td-tracking-negative.json), [frozen protocol](td-tracking-protocol.md), and [excluded development attempts](evidence/td-tracking-attempts.json).', '',
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
            number=lambda key:f"{t[key]:.2f}" if key in t else 'absent'
            out.append(f"| {c['seed']} / {c['split']} | {a['candidate']['kind']} | {'pass' if a['legacy_evaluation']['supported'] else '**fail**'} | {flags} | {len(t['stations'])} | {number('center_displacement_native_pixels')} | {number('total_turn_degrees')} | {number('minimum_prominence_or_depth_metres')} |")
    out += ['', 'Every original fine-point station is retained in the [full-station audit](evidence/td-tracking-profiles.json), including tails where greedy tracking stopped. This uses the frozen 50 m/range/residual arithmetic for description; it does not replace the frozen coverage gate.', '',
        '| Seed / kind | Original / localized / tracked two-sided stations | Original fine-point weakest side (m) | Original strict fine-point result |',
        '| --- | --- | ---: | --- |']
    for p in profiles['rows']:
        original=p['original_fine_point_strict']
        out.append(f"| {p['seed']} / {p['kind']} | {p['original_two_sided_stations']} / {p['localized_two_sided_stations']} / {p['tracked_two_sided_stations']} | {original['minimum_prominence_or_depth_metres']:.2f} | {'pass' if original['supported'] else '**fail**'} |")
    localized=sum(p['original_two_sided_stations']<5 and p['localized_two_sided_stations']==5 for p in profiles['rows'])
    turning=sum(p['localized_two_sided_stations']<5 and p['tracked_two_sided_stations']==5 for p in profiles['rows'])
    height_only=sum(p['original_two_sided_stations']==5 and not p['original_fine_point_strict']['supported'] for p in profiles['rows'])
    out += ['', f"Recentring restores all five two-sided stations in {localized} attempt(s); allowing orientation changes adds five-station recovery in {turning} more. {height_only} original fine-point profile(s) already have two-sided extrema at all five stations and fail the longitudinal height conditions instead. Attempted paths exceeding the combined 90-degree turn limit stay failed; the limit is checked after both bounded branches are assembled.", '']
    out += ['', 'Recovery of five two-sided stations can demonstrate a localization/orientation contribution while the complete longitudinal rule remains failed. Missing bounded stations leave genuine interruption, off-center alternatives and limited orientation/curvature tracking unresolved.', '', 'Failure reasons and ablation interpretations (native observations only):', '']
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
            flag=lambda x:'absent' if x is None else 'pass' if x['supported'] else '**fail**'
            residual='incomplete' if not n or n['longitudinal_linear_residual_metres'] is None else f"{n['longitudinal_linear_residual_metres']:.2f}"
            values='absent' if not n else f"{n['minimum_prominence_or_depth_metres']:.2f} / {n['longitudinal_range_metres']:.2f} / {residual}"
            out.append(f"| {c['seed']} | {p['kind']} | {flag(n)} | {flag(t)} / {flag(u)} | {values} |")
    out += ['', f"Frozen new coverage gate: **{'PASS' if data['decision']['tracked_morphology_coverage_passed'] else 'FAIL'}**. It requires a ridge AND basin on BOTH fresh seeds, with unambiguous tracked points, native-cell means and scaled tiles at BOTH scales. This is a separate descriptive gate; no output-changing policy is adopted.", '',
        'Full native-cell means summarize 65,536 floating elevations. Coarse 3x3 neighborhood range is a different support statistic. Scaled 256-world-block tiles retain 25 quantized sample heights; at scale 6 their native footprint is smaller. Fine-cell relief and fine-tile relief remain separate from all means and from coarse range. No p5 or geology-1 cutoff is transferred.', '',
        '## Terrain agreement and boundaries', '',
        'Mean absolute central coarse versus matched-target fine-cell error, in metres; each policy remains compared with the actual target. Scales6 are excluded from these native support counts. Selected features and overlapping strata are correlated.', '',
        '| Seed / group | Rows | Province anchor | Actual target | Fixed grid4 |',
        '| --- | ---: | ---: | ---: | ---: |']
    corners=profiles['tile_origin_corner_checks'];bad_corners=[p for p in corners if not p['equal']]
    corner_text=f"Supplementary same-coordinate check: {len(corners)-len(bad_corners)}/{len(corners)} quantized patch/tile origin-corner records agree, over {len({(p['seed'],*p['native_corner']) for p in corners})} distinct seed/native corners. These repeated records are correlated."
    for p in bad_corners:
        corner_text+=f" Seed {p['seed']} at {p['native_corner']}: patch {p['patch_elevation_metres']} m quantizes to {p['patch_quantized']}, tile corner is {p['tile_corner_height']}."
    corner_text+=' Discrepancies remain visible, without a tolerance or a causal claim. This descriptive coordinate/product audit does not replace any frozen acceptance criterion.'
    index=out.index('## Terrain agreement and boundaries');out[index:index]=[corner_text,'']
    for c in native:
        for group in ('coverage','contrasts','features'):
            m=c['terrain_agreement'][group]
            if m:
                out.append(f"| {c['seed']} / {group} | {m['target']['n']} | "+' | '.join(f"{m[p]['target_mean_absolute_error_metres']:.2f}" for p in ('province_anchor','target','fixed_grid_4'))+' |')
    out += ['', '| Seed / scale | Coarse/grid contacts / province contacts | Max anchor / target / grid coarse jump (m) | Max tile jump (m) |',
        '| --- | --- | --- | ---: |']
    for c in cases:
        b=c['boundary_evaluation']
        out.append(f"| {c['seed']} / {c['scale']} | 4 / {sum(x['province_changed'] for x in b[-2:])} | "+' / '.join(f"{max(x['central_mean_jumps_metres'][p] for x in b):.2f}" for p in ('province_anchor','target','fixed_grid_4'))+f" | {max(x['target_tile_mean_jump_metres'] for x in b):.2f} |")
    out += ['', 'Boundary jumps describe changed statistical support, not one-block physical cliffs. Province contacts are independently located and required to change the Java-reported province. Actual-target support is distinguished from province-anchor support in every paired comparison:', '']
    for pair in data['paired_support']:
        counts=pair['policies'];out.append(f"- Seed {pair['seed']}: " + '; '.join(f"{p}: {m['matching_hashes']}/{m['matched_support']} hashes on matching support, {len(m['differing_support'])} differing supports" for p,m in counts.items())+f"; full native patch hashes match: {pair['patch_hashes_match']}.")
    retained=runpy.run_path(str(ROOT/'scripts/audit-td-tracking-retained.py'))['audit'](data)['rows']
    policies=[p for row in retained for p in row['policies'].values()]
    out += ['', f"Separate [cross-run PR51 point audit](evidence/td-tracking-retained.json): {len(retained)} repeated world-location rows, {sum(p['native_object_equal'] for p in policies)}/{len(policies)} exact full native-policy objects; coarse objects equal at {sum(p['coarse_equal'] for p in policies)}/{len(policies)}. Maximum native-mean difference {max(p['mean_absolute_difference_metres'] for p in policies):.12g} m; maximum relief difference {max(p['relief_absolute_difference_metres'] for p in policies):.12g} m. These numeric differences remain strict mismatches despite their small magnitude. Their cause was not isolated. They are separate from within-fixture exact traversal and cannot repair #5's stronger failed assertion.", '']
    out += ['', '## Requests, traversal and cache limits', '',
        '| Seed / scale | Unique comparisons | Deduplicated coarse / native misses forward | Forward / reverse new windows | All post-startup C/D/H/W | Native LRU peak |',
        '| --- | ---: | --- | --- | --- | ---: |']
    for c in cases:
        a=c['request_accounting'];d=c['post_startup_delta']
        out.append(f"| {c['seed']} / {c['scale']} | {len(c['observations'])} | {a['expected_deduplicated_coarse_requests']} / {a['expected_deduplicated_native_fine_requests']} | {a['forward_actual_delta']['computed_windows']} / {a['reverse_actual_delta']['computed_windows']} | "+'/'.join(str(d[k]) for k in ('coarse_calls','pipeline_data_calls','heightmap_calls','computed_windows'))+f" | {a['max_retained_fine_entries']} |")
    u=data['units']
    out += ['', f"{u['forward_comparisons']} forward world-location comparisons and the same number reversed cover {u['distinct_seed_native_targets']} distinct seed/native target cells. Twelve forward patch grids represent {u['distinct_seed_native_patches']} distinct seed/native patches; reverse recomputation is additional paired work, not new coverage. The fixed screen has486 rows, representing243 seed/native cells.", '',
        'C/D/H/W means public coarse / direct-data / heightmap calls / newly computed windows. Each fixture makes four direct patch-data misses, serving196 row commands through a one-entry patch cache; none of those row hits imply new model requests. Fine comparison misses are independently replayed against cleared128-entry coarse/native LRUs forward and reverse. Two uncached tile reads occur per comparison. Window counts for patches, screen and suites are retained jointly in post-startup totals; they are not isolated patch/policy timings. Startup counters remain separate in JSON.', '',
        'Within every fixture, forward/reverse comparison evidence and reversed patch values/full hashes match exactly after explicit cache clear. Provider tensors can remain warm; this is traversal evidence, not fresh-process final-block determinism. The real coarse suite passes four concurrent callers producing one public request, 129 misses retaining 128 entries and recomputing eviction. Native-cache eviction is not claimed merely because its cap is 128. The patch cache retains one 49x49 float grid; the full 3073x3073 height plane is transient. Internal provider-cache occupancy and native-memory peaks were not measured. The accepted matrix stays within 52 forward/reverse comparisons, 12,000 post-startup windows, 6 GiB heap, 360s startup, 300s command, 45min fixture, 4h matrix and disk reserve guards.', '',
        '## Preserved failures, scope and remaining gate', '',
        'PR51’s frozen strict exporter is unchanged and still rejects its retained matrix with **Paired coarse drift**. Its morphology coverage gate remains **failed**. The separate negative exporter first requires that original rejection, then repeats strict source/artifact/transcript checks. This slice neither weakens those assertions nor changes geology-1 to make displaced province anchors correspond.', '',
        '**Additional frozen assertion: FAIL — Actual matching native support changed.** The new original strict exporter also remains unchanged and rejects this matrix. At seed -2026110411, province-anchor rows at native targets (-320,-4032) and (-64,-3648) share one cell whose fine hash differs across scales; a fixed-grid row at (1088,-3520) differs in a second cell. Support coordinates and coarse evidence match. Mean differences are 7.748603820800781e-7 and 7.003545761108398e-7 m; these are failed exact comparisons, not accepted equivalence. Actual-target native hashes match at all 110 paired rows. This differs from PR51’s displaced-anchor failure: these two cells have matching support but different fine hashes, and their cause was not isolated.', '',
        'The separately named export-negative-td-tracking.py first executes and requires that exact original rejection, then repeats all source/artifact/raw transcript, selection, traversal, resource and counter checks. Only the three recorded same-support mismatches are retained as failures; all other rejections remain fatal. It corrects descriptive hash-match counts after the frozen hard assertion, records the failed flag and full numeric objects, uses no tolerance, and cannot turn either strict comparison or morphology coverage into a pass. CI explicitly requires the frozen rejection and complete negative replay. The original positive portable-test path is intentionally absent; the separate negative test covers the full matrix.', '',
        'New work: frozen selector/analytical controls, six CPU sampling fixtures, fine point patches and profiles, exact reverse recomputation, coarse concurrency/eviction/oracles, per-fixture snapshot-byte checks, model/template unchanged checks, source/artifact/log export and request accounting. The production addon is byte-identical to main; every prior probe entry is unchanged and only TrackingPatch.class is added. CI runs build/resource/domain/semantic/portable replay checks; inference runs locally.', '',
        'Reused work: #47 coarse prototype/original-artifact restoration and save/reopen guards; #48/#49 terrain diagnostics/source-byte portability; #50 actual-target/native-cell support and save/reopen evidence; #51 failed strict profiles and cross-scale anchor evidence. Their original strict exports reproduce committed JSON. Their complete sampled blocks and529 persisted-container/reopen checks are retained acceptance, not newly executed by this sampling-only slice. #5’s stronger failed final-block assertion remains failed; historical route timing is separate.', '',
        'Excluded attempts: -01 failed a sandbox hardlink before launch; -02 exposed omitted patch transcript logging on development data and was manually stopped (hung shutdown required termination); -03 hit the frozen disk guard and shut down normally. This totals eight JVM launches: six complete accepted fixtures and two excluded development launches; -01 launched none. No fresh seed was inspected in the excluded attempts. Only stopped new-fixture ONNX caches were removed. The user freed disk space before the unchanged accepted -04 restart. Excluded attempts have no complete new-window counter endpoint, so model-return log rows are not substituted for new-window counts or included in the accepted matrix totals.', '',
        'Remaining gate: first resolve the demonstrated discrete-axis/support-length aliasing with a preregistered constant-bandwidth orientation/localization control and bounded alternative-path/gap tests. Then demonstrate unambiguous independently localized actual TD ridges AND basins, finite two-sided continuity and matched-native/scaled-tile support at scales 1/6 on at least two NEW held-out seeds. Keep this original strict exporter and its failed rules separate. The now-examined seeds become development data for any revision. A finer/wider search or looser continuity rule is not silently substituted here. Independent geological plausibility, history and contact-coherence/calibration remain separate even if morphology succeeds. Retained synthetic-prior-1 competing interpretations remain seeded synthetic hypotheses with uncertainty and abstention, never recovered geological history.', '',
        'No palettes, dikes, minerals or integrations. Ulti-World stays optional. #9/#11 stay open. Any future output adoption still needs immutable generator identity, explicit new-world-only selection, genuine bidirectional continuing-save rejection, exact original-artifact restoration/reopen and complete snapshot/block/persisted-container preservation. Never migrate continuing geology-1 snapshots. Integrated candidates additionally need alternating paired CPU startup/cold/warm/full-route benchmarks on NEW fixtures. Isolated-query savings are not route savings.', '',
        'Local verification: JDK 21 build/domain/settings/coarse/probe checks, resources (64 blocks / 158 recipes / 711 JSON), catalog and Python syntax pass. Python suites run 32 tests: 31 pass, with the frozen positive portable path intentionally skipped; the separate two-test negative suite replays the complete matrix and requires its original rejection. Strict retained re-exports match every committed JSON value. No diagnostic JVM/collector process or game/RCON listener remains. [PR52 CI checks](https://github.com/WilyJEB/geologic-variation/pull/52/checks) validate builds and portable replay separately from local inference.', '',
        '## Reproduction', '', '```powershell',
        './scripts/bootstrap.ps1', './gradlew.bat build runtimeProbeJar',
        'python scripts/test-td-tracking.py',
        'python scripts/verify-td-tracking.py --java <java21> --td <pinned-cpu-jar> --baseline <retained-main-addon> --protocol-commit 2a52336fb926a89e15e13940cd2fddd339341e0d --output <NEW-directory>',
        'python scripts/summarize-td-tracking.py <NEW-directory> --output <portable-json>',
        '# The frozen exporter must reject the retained matrix with Actual matching native support changed.',
        'python scripts/export-negative-td-tracking.py <NEW-directory> --output <negative-portable-json>',
        'python scripts/test-negative-td-tracking.py',
        'python scripts/reexport-retained-terrain.py', '```', '',
        'Raw accepted matrix: runs/acceptance/td-tracking-2026-11-04-04. Strict re-export after the final Windows checkout is required; LF attributes preserve exact executed source bytes. Portable replay is not a replacement for artifact/source/raw transcript verification.']
    return '\n'.join(out)+'\n'


if __name__=='__main__':(ROOT/'docs/td-tracking.md').write_text(report(),encoding='utf-8',newline='\n')
