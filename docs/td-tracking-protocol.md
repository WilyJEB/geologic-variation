# Frozen bounded center and orientation diagnostic (#11)

Base main e3fdbcf (merged #51). Diagnostic only; geology-1 unchanged. All previously
examined seeds, including 2026110317 and -2026110319, are development data. Retained
#51 failures are replayed as development, never fresh validation. New collection:
8675309 development; fresh 2026110407 and -2026110411 held out, scales 1/6 paired.
Commit and push this protocol, selector, evaluator and resource rules before
inspecting either new seed. No postinspection parameter changes or seed replacement.

Search the unchanged signed 9x9 native coarse screen (-64..64 cells, step 16).
Use the original 50 m two-sided central-extremum ranking, top center per kind only.
No replacement if absent. Re-evaluate original five straight coarse stations with
unchanged PR51 criteria; its failed strict exporter and paired-anchor assertion
remain untouched. Coarse means do not independently localize a fine crest.

Collect one bounded native fine patch per candidate: original cell center +/-1536
pixels, 3073 squared full floating elevations, hash every float in row-major order;
retain exact point elevations on a 49x49 grid, spacing 64 pixels. This is fine
point terrain, neither full-cell means nor scaled tiles. One diagnostic patch
cache entry (49 squared floats after transient full-array extraction), exact
server/seed identity, explicit clearing. No interpolation/smoothing or p5.

Three separate ablations use these actual fine points: original straight axis and
center; localized with that same fixed axis; localized with orientation tracking.
Center search is a radius-256 disk at 64px spacing. Later stations search radius
128 around the predicted next center, at 64px spacing, and stay within 256px of
the original straight station. Two steps in each longitudinal direction, maximum
five stations. Discrete axis offsets are (256,0),(256,128),(256,256),(128,256),
(0,256),(-128,256),(-256,256),(-256,128), with direction chosen consistently.
Shoulders use the perpendicular offset at each station. Step and shoulder length
are 256..362.04 pixels; accepted finite path length must be 768..2048 native pixels.
Maximum per-step turn 45 degrees, combined total turn 90. No branching: one path,
deterministic ranking by weakest side descending, displacement, point, axis.

Every station requires both signed shoulder differences >=50 metres (ridge down,
basin up). Keep original longitudinal constraints: center range <= twice the
weakest side; endpoint-linear residual <= weakest side. Cross slopes are never
detrended into extrema. Missing stations, insufficient sides, excess tilt/range,
turning or displacement fail. Saddles/interrupted extrema fail these conditions;
they are not relabelled as successful ridges. A center at the search edge abstains.
An alternative within 50 m of the best weakest-side score and >128px transversely away or
>45 degrees apart makes the result ambiguous: crossing/branching interpretations
abstain, including ties. Retain all tested alternatives and failure reasons.

Localization uncertainty: sampling quantization +/-32px per axis (45.26px radial),
plus unresolved between-grid extrema and alternative-center/orientation uncertainty.
This is not a confidence interval or proof of an exact crest. Straight failure
followed by localized success supports off-center sampling; only tracked success
supports orientation/curvature. Failure of all three cannot prove a genuine
interruption: retain incomplete path, failed margins and ambiguity, and abstain
between interruption, unresolved localization and limited orientation resolution.

Collect existing sampling-compare at every tracked center and both shoulders,
maximum 30 feature points. Even incomplete/ambiguous paths stay visibly failed.
Retain actual-target full native-cell mean/hash/relief and coarse neighborhood range,
scaled 256-world-block tile samples/mean/relief, and province anchors/fixed-grid
comparisons separately. Fixed coverage uses unchanged diagonal screen indices
0,20,40,60,80, separate from targeted ocean/coast/low/intermediate/high strata and
12 signed points across four coarse/grid and two independently located province
boundaries. Overlapping memberships deduplicate locations, not evidence labels.
Fine mean/tile profiles use the same 50m/range/residual rules separately; point
success cannot repair their failure. No geology-1 cutoff transfer.

Clear caches and reverse all comparisons and patch bands; require exact evidence
and full-patch hashes, ignoring only request miss/counter fields. Native/provider
caches may be warm: no final-block determinism or fresh-process timing claim.
Run original coarse suite/oracle (four concurrent requests deduplicate to one;
129 misses retain128 entries and recompute eviction). Fine LRU cap128; no eviction
claim unless actually exercised. Paired scales and shared native cells are paired
observations. Compare hashes only on matching actual native support; list differing
province-anchor supports separately, never repair geology-1 for correspondence.

Limits per fixture: 81 screen + <=10 strict confirmation coarse getters; two
patches forward/reverse (four direct-data misses, 196 row commands); <=52 forward
and <=52 reversed sampling comparisons. Six serial JVMs, 6GiB heap each; startup
360s, command300s, fixture45min, total4h. Post-startup new-window cap12000; check
metrics after every patch and forward fine comparison and end of reverse. Window
cap is a stop guard at those checkpoints, not a promise of zero overshoot inside
a single model call. Need1GiB disk before launch and512MiB at each command.
Stop on resource failure with partial evidence, no expanded search or weaker gate.
Link immutable CPU TD/model inputs, copy addon/probe. Clean only stopped NEW
fixtures' regenerable caches; preserve template/shared inputs and unrelated temp/.

Coverage requires both fresh seeds to supply ridge AND basin, unambiguous tracked
point paths AND native-mean AND scaled-tile continuity at both scales. Failure
finishes diagnostic-only with a concrete remaining gate. Analytical controls stay
separate from TD coverage. Competing geological hypotheses remain seeded synthetic
interpretations with unestablished uncertainty and stone-selection abstention;
morphology never establishes geological plausibility. No output adoption even if
this descriptive gate passes; #9/#11 remain open, #5 stronger failure visible.

Reuse #47–#51 save/reopen/production guards explicitly; do not call them new work.
Strict re-export every retained evidence source and the new export after final
Windows checkout, preserving exact source-byte provenance with LF attributes.
No palettes, dikes, minerals or integrations. Ulti-World optional. Any future
output-changing adoption requires immutable generator identity, explicit new-world
selection, real bidirectional continuing-save rejection, exact original-artifact
restoration/reopen and complete snapshot/block/persisted-container preservation.
Never migrate continuing geology-1. Integrated candidates additionally require
alternating paired CPU startup/cold/warm/full-route benchmarks on NEW fixtures.
Isolated-query savings never imply route savings.
