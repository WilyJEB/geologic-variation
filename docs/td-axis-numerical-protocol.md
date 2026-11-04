# axis-confinement-1 / identical-support-controls-1

Frozen before analytical validation inspection or new TD execution. Base main
1c31c0f (merged PR53). All prior seeds are development. No fresh TD seeds in
this slice, even if individual controls pass. No production change.

## Geometric property and evaluation

This is a finite-support elongation diagnostic, not a global landform identity.
Use geometry-arc-1's unchanged center/alternative/turn/branch/gap rules and exact
256-native-pixel shoulders and actual steps. Its full decisions remain exported.
At each of the three interior stations, compute the absolute second divided
difference of center height against actual cumulative distance. Multiply by
256 squared and divide by the sum of the two signed transverse shoulder drops.
All three ratios <=0.25 support transverse confinement dominating longitudinal
curvature; any ratio >=0.5 rejects; intermediate ratios abstain. No tolerance
changes these thresholds. Incomplete/ambiguous/edge/turn failures abstain before
classification. Endpoints do not establish curvature beyond the observed path.

An arbitrary linear elevation trend has zero longitudinal curvature and can
pass even when original height-range/residual assertions fail. Gentle nonlinear
trends can pass; an axis with curvature comparable to its cross-section does
not satisfy this property's elongation requirement. This rejects symmetric
isolated quadratic extrema and symmetric saddles, but shallow saddles or very
elongated closed extrema can be locally indistinguishable. These are mandatory
adversarial controls, not exceptions removed after inspection. Report every
success, false positive/negative, incomplete path, rejection and abstention.
Keep legacy height-range/residual outcomes separate. No retroactive passes.

Analytical functions are queried exactly, with no interpolation. Development:
angles 0/22.5/45/67.5/90, translations (0,0)/(37,-19), both signs. Frozen
validation: angles 11/33/79/123, translations (-53,29)/(101,-67), both signs.
Same fixed 15 families: straight, curve, linear trend, gentle quadratic trend,
sinusoidal trend, slope, isolated quadratic, saddle, crossing, parallel,
gap, elongated isolated quadratic, shallow saddle, strong nonlinear trend,
asymmetric shoulders. Validation is run once after source/protocol push; no
retuning. Every attempted path and exact queried value is retained.

TD: reuse the six PR53 fields only; bilinear descriptive replay is never proof
of extrema. Unknown interpolation error is not bounded by checkerboards or
analytical error. No additional fine queries authorized. All reused-field
outputs abstain from confirmed geometry, regardless of descriptive ratios.
No manufactured between-sample extrema. A remaining alias on adversarial
analytical controls or unknown TD error keeps geometry validation gated.

## Numerical matrix and resources

Seed -2026110411 only, native row -14, cols -6/+6 (A/B). Every new direct
rectangle is exactly [row*256,col*256,(row+1)*256,(col+1)*256], withClimate=false.
No halo, batching, new corner or large-patch query. Reuse PR53 arrays and shape
reproducer to compare against; do not repeat their established shape result.

Four serial JVM launches MAXIMUM, including failed launches; no replacements:
0 scale1 AB reference; 1 scale1 AB fresh-process repeat; 2 scale1 BA order
intervention versus 1; 3 scale6 AB scale intervention versus 1. Each has an
initial AB (or BA) and identical repeat. In process0 only, populate the real
SamplingDiagnostic native-cell cache using A/B (capture both arrays); observe,
read AB, clear only diagnostic caches, observe, read AB, clear only the public
provider heightmap/pending cache, observe, read AB. Repeat-read controls hold
order/process/scale fixed; cache and provider interventions do not reverse order.
Provider tensor caches remain warm: public clearCache clears CACHE/PENDING only,
not WorldPipeline tensor stores. No seed switching or private tensor reset.
First versus repeated queries measures execution-history warming, not asserted
empty tensor state (startup already computes windows). Independent fresh-process
AB repeat is the reference for interpreting order and scale comparisons.

Maximum26 direct requests (14 in process0, four in each other process), two
unique native supports, no additional geometric support. Maximum1500 computed
windows per JVM INCLUDING startup; maximum6000 summed. Poll before/after commands
and during startup/commands via log counters/process monitor where available.
Counters deduplicate computed windows within each provider; cross-process counts
are recomputations, not independent terrain observations. Checkpoint cap may
overshoot within one inference; stop and record a failed cap if that occurs.
6GiB heap/JVM; sampled working set16GiB cap, not an instantaneous bound.
Disk free reserve4GiB throughout; total wall time30min, startup360s, command300s.
External watchdog terminates the process tree at wall/memory/disk limits,
including startup; monitor interval1s. Budget ledger persists BEFORE launch and
BEFORE requests, so failures consume their allocation. Partial evidence retained.
No automatically expanded search. Abort whole matrix after any failure.

Retain every produced float array (big-endian exact bits), requests in executed
order, counters before/after, logs, CPU/backend/context, all config/model/artifact
hashes, exact executed source bytes and source commit. Verify pinned artifact
cache behavior by retained javap output, not just an upstream working tree.
Compare bits, differing indices, max absolute/ULP changes, means, relief and
floor/clamped heights. No tolerance repairs equality. Compare old scale1/6
hashes without inventing historical indices/ULPs: full old arrays do not exist.
No historical reproducer claimed unless this matrix actually reproduces it.

## Preserved boundaries

geometry-arc-1 and PR51/52 selectors/exporters remain byte-identical. Re-export
strict #47–#53 and new evidence after final Windows checkout; retain failed
assertions visibly failed. #5 stronger failure remains failed; #9/#11 open.
Geology-1, strict guards, immutable shared inputs, optional Ulti-World and
unrelated temp/ remain intact. No palettes/dikes/minerals/integrations, p5 or
transferred cutoffs. Different anchor support is not unequal matching-support
hashes. Fine points, means, coarse range, scaled tiles and fine relief stay
separate. Morphology never establishes geological plausibility; interpretations
are competing seeded synthetic hypotheses with uncertainty and abstention.

Future validation requires a separately pushed selector/evaluation/resource
protocol after BOTH gates pass, at least two genuinely new seeds, scales1/6,
negative coordinates, contrasting terrain and multiple coarse/province contacts.
Fixed coverage and selected features are separate; shared cells/scales paired.
Future adoption requires immutable generator identity, explicit new-world-only
selection, genuine bidirectional continuing-save rejection, exact original
artifact restoration/reopen and complete snapshot/block/persisted-container
preservation. Never migrate continuing geology-1. Integrated candidates need
alternating paired CPU startup/cold/warm/full-route benchmarks on NEW fixtures;
isolated-query savings never imply route savings.
