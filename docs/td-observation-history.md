# Observation target and historical execution prefix (#11)

Diagnostic only, based on merged PR54 `9ccc867`. Geology-1 and production sources
are unchanged. Neither adoption gate passes. No new TD execution, arrays, seeds,
selector or discriminator; no new runtime collector is authorized by this report.

[Portable prefix/source/bytecode/transcript archive](evidence/td-observation-history.zip)
and [hash manifest and target locations](evidence/td-observation-history.json).
Reproduce offline with `scripts/audit-td-history.py`; portable verification uses
`scripts/test-td-history.py`. Existing frozen exports remain unchanged.

## Resolve the measurement target

The measurable target is **finite-support transverse confinement**, specified by
transverse shoulder distance, path extent, orientation search and uncertainty.
It is not global ridge/basin identity. A ridge cross-section can remain confined
while its center height rises, falls, has a summit, or crosses a saddle. A global
taxonomy that excludes every saddle or closed extremum conflicts with allowing
arbitrary longitudinal trends. This is a definition conflict, not a missing
curvature cutoff. No replacement discriminator is proposed.

In PR54's functions, write elevation as `h(u,v)=f(u)-a*v²` for a ridge, with
the opposite sign for a basin. Shoulder sum at distance d is `2*a*d²`.
For `f=b*u²+c*u`, the confinement ratio is `|b|/a`, independent of c.
The retained elongated isolated extremum (`b=-0.0002`) and shallow saddle
(`b=+0.0002`), with `a=0.004`, both give 0.05 on a straight exact axis.
Their observed curvature signs differ, so they are NOT identical local fields;
their absolute-ratio diagnostic is identical. Rejecting positive longitudinal
curvature would also reject allowed quadratic trends; rejecting negative
curvature would reject allowed longitudinal summits. All old false positives
remain false positives under their original taxonomy.

The strong nonlinear trend `0.004*u²+2*u-0.004*v²` is exactly
`0.004*(u+250)²-0.004*v²-250`: a translated symmetric saddle. Its saddle point
is at u=-250. Even perfect observations cannot assign two incompatible labels
to this same function. Its frozen false negatives remain false negatives under
the original intended-positive label. Gentle quadratic trend has a critical
point at u=-2500, outside the nominal five-station 1024-pixel path; its critical
point need not be observed locally. Linear trends move the critical point;
they do not certify absence of a saddle elsewhere. Rotation and sign reversal
do not resolve these mathematical aliases.

For any finite observed domain D, smooth extensions can agree identically on
a neighborhood of D and differ outside it: multiply a smooth modification by
a cutoff supported outside D. One extension can close a crest into a summit;
another can continue it, branch or terminate. Thus even continuous perfect
observations on D cannot certify unrestricted global identity. Finite sampled
points are weaker: a smooth bump vanishing at every sampled point can change
unsampled extrema. Without derivative/error assumptions there is no universal
finite sample spacing or observation radius that eliminates either ambiguity.

Required extent must therefore be stated with the claim:

* A local claim names the observed path length L, shoulder distance d, sampled
  positions, two-sided contrasts and longitudinal behavior. PR54 uses five
  stations with four actual 256-pixel steps (L=1024) and d=256, plus its bounded
  localization/alternative queries. It establishes nothing beyond the exported
  query footprint, and search failure is not physical interruption.
* A domain-relative crest/valley claim needs a preregistered finite domain and
  stopping/boundary rules, observed cross-sections along the entire claimed
  path, competing branches, critical points and terminations inside that domain.
  A path reaching the boundary is censored; its exterior identity abstains.
  Such a protocol has not been implemented or validated here.
* An unrestricted global claim needs global observations or a justified model
  class with a finite identifiability theorem. Neither exists for these TD data.
  For the quadratic family only, determining its coefficients and critical point
  can answer a model-relative question; assuming that family for TD is unjustified.

Uncertainty rules for any future revision: distinguish sampled contrasts from
continuous extrema. If each height has a defensible error bound epsilon, an
individual shoulder drop must exceed 2*epsilon to certify its sign. At equal
step d, the longitudinal second-difference numerator has error at most
4*epsilon, as does the two-shoulder denominator. Use interval arithmetic with
a strictly positive denominator; if a decision boundary is intersected, abstain.
These bounds apply at fixed observed locations; localization and competing
paths require their own uncertainty assessment. Between-point extrema need
observed bracketing plus a defensible regularity bound or remain unconfirmed.
Unknown TD error is not epsilon=0. Bilinear/checkerboard evidence supplies no
such bound. All six reused TD fields continue to abstain. No old threshold,
failure label, or frozen validation split is rewritten. All previously inspected
analytical cases, including PR54's former validation, are development for revisions.

## Exact retained public history

GitHub confirms merged #47 d6d59ca, #48 db8bcea, #49 05bd8b9, #50 ce91c6a,
#51 e3fdbcf, #52 6c5f105, #53 1c31c0f and #54 9ccc867. Fetched origin/main
matches local main at 9ccc867. No applicable AGENTS.md exists in the checkout
or ancestors through the user/project roots. #9/#11 remain open.

The new offline archive retains PR52's original complete results, both relevant
console transcripts, frozen Java request sources and a deterministic reconstruction.
It expands cache misses using the original 128-entry access-order native/coarse
LRUs, verifies each sampling command against its independent per-API counters,
and checks patch-cache misses. This is the exact source-derived PUBLIC request
prefix, not a fabricated internal tensor trace. Events and request ordinals below
are zero-based. Full order, bounds, climate flags and hashes are portable.

| Historical first native miss | scale1 | scale6 |
| --- | --- | --- |
| row -14 col -6 | event280, request326, province_anchor, compare(-320,-4032) | event280, request322, compare(-1920,-24192) |
| row -14 col +6 | event294, request366, fixed_grid_4, compare(1088,-3520) | event294, request362, compare(6528,-21120) |

Both histories begin with four measured startup windows (startup internal
request trace unavailable), an 81-location coarse scan, candidate coarse
stations and two large patch requests. The patch requests occur at public
ordinals85/90, events88/144, native bounds
`[-9600,-1408,-6527,1665]` and `[-5504,-1408,-2431,1665]`, climate=false.
The second patch contains almost all the target cells but excludes their
leftmost/rightmost 128-pixel margins. Overlap is not proof that all required
latent/decoder windows were populated in the same batches as a later cell read.
The archive retains all subsequent coarse/native/tile requests preceding each
first native miss, including the exact immediately preceding requests.

Scale1 tile sampling directly calls getPipelineData with climate=false. Scale6
calls fetchHeightmap on world rectangles; pinned handleUpsampled maps them to
native support with padding and climate processing. Those are different preceding
execution histories even when the eventual matched-native rectangle is identical.
Public call counts are checked; provider hit/miss and internal window membership
were not logged and cannot be reconstructed exactly from them. The scale1
prefix through the final target command has369 public requests, scale6 has365.
Immediately before col-6, retained metrics report3625 versus3588 computed
windows (scale1/6); before col+6,3706 versus3667. These totals include startup
and do not identify which windows or eviction events occurred.
The duplicate failed province-anchor observation reuses the cached col-6 object;
three failed policy rows represent two native cells, not three independent arrays.

PR53's retained numerical history starts with direct unpadded cell requests,
then explicitly varies halo and batching. PR54 starts AB/BA after matching startup,
then repeats exact rectangles and isolates process/order/scale/diagnostic cache.
Its26 arrays agree exactly and are reused here, never rerun. Neither collector
replayed PR52's large-patch/mixed-tile prefix. PR53's shape sensitivity remains
a different demonstrated effect, not proof of identical-request historical cause.

## Pinned behavior and bounded hypothesis

New `javap -p -c` inspection runs no TD model. Its complete output for
MemoryTileStore, InfiniteTensor and WorldPipeline is portable. CPU JAR remains
SHA256 `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`.
MemoryTileStore uses access-order LinkedHashMaps per tensor, tracks float byte
sizes, and evicts eldest entries while over the limit and more than one remains.
WorldPipeline supplies104857600-byte stage limits. InfiniteTensor.getSlice
ensures missing windows, assembles the result, then evicts that tensor. Missing
windows are deduplicated in insertion order; dependencies are ensured first.
Both latent stages use batches of four; computeBatched slices the missing list
into groups, obtains dependency slices and caches each result. Existing keys
are retained rather than overwritten by cacheWindow. Eviction can change which
windows are missing on a subsequent read. None of this establishes unequal bits.

Concrete hypothesis: the retained second patch and intervening mixed tile reads
leave a partial latent-window population around the two edge cells. The later
identical native request can therefore compute a different missing-window group
than PR53/54's early cell reads; stage eviction may modify that population.
This predicts a difference in *missing latent coordinates/batch membership at the
first cell miss*, not merely in total counts. It does not assume a cache fault,
provider bug, or nondeterministic ONNX arithmetic. Floating output sensitivity
to such internal grouping remains a hypothesis for this history.

Evidence is insufficient to justify a bounded new TD run now: no historical
internal batch/eviction trace exists, no offline window-state simulation is yet
validated against this pinned implementation, and a reduced prefix has not been
shown to preserve its distinguishing state. Replaying only a halo, cache clear,
AB/BA or scale would repeat exhausted controls. A full prefix replay would add
substantial work without isolating the proposed mechanism. Next useful offline
work is a pinned window-dependency/state simulator, including getSlice eviction
timing and provider upsampling, checked against retained counters; only then
choose a minimal distinguishing prefix and fresh-process reference. That is a
future bounded slice, not an executed experiment or a claim of causation.

Any future execution requires its protocol AND executable collector committed
and pushed first, with fixed launch cap including failures, public request,
startup/total window, memory, disk and wall caps; preserve every produced array,
exact sequence/counter, executed sources/artifact, inputs and partial failures.
The prior four-launch budget is exhausted. Public provider clear was0->0,
never a tensor reset. Historical full arrays do not exist: indices/ULPs remain
null/unknown. PR54 runtime used4a2fa1c; the final capture mixin is compile-verified
only. These executed and final artifacts are not interchangeable.

## Verification and retained gates

New work consists only of the mathematical target analysis, source-derived
request reconstruction, pinned bytecode inspection and portable replay/corruption
test. All TD arrays/fields, analytical outcomes and save/reopen evidence are reused.
Strict retained #47–#54 re-exports must reproduce after final Windows checkout;
PR51 `Paired coarse drift`, PR52 `Actual matching native support changed`, old
height/residual criteria and #5's stronger final-block failure remain failed.

All adoption gates in [PR54's report](td-axis-numerical-controls.md) and frozen
protocol carry forward: observed/uncertainty-qualified geometry, historical
numerical cause/reproducer, separately pushed selector/evaluation/resource rules,
genuinely new seeds only in a later authorized validation slice, scales1/6,
negative coordinates, contrasting terrain and multiple coarse/province contacts;
fixed coverage and selected features separate, shared cells/scales paired.
Morphology cannot establish geology; geological interpretations remain competing
seeded synthetic hypotheses with abstention. Fine points, native means, coarse
range, scaled tiles and relief remain separate; different anchors are distinct
from unequal matching-support hashes. No p5 or transferred geology-1 cutoffs.

Future adoption still needs immutable generator identity, explicit new-world-only
selection, genuine bidirectional continuing-save rejection, exact original-artifact
restoration/reopen and complete snapshot/block/persisted-container preservation.
Never migrate continuing geology-1. Integrated candidates additionally need
alternating paired CPU startup/cold/warm/full-route benchmarks on NEW fixtures;
isolated-query savings never imply route savings. Reused save/529-container
acceptance is not newly executed. Strict guards, immutable inputs, optional
Ulti-World and unrelated temp/ are preserved. No palettes, dikes, minerals or
integrations. Both insufficient gates keep this slice diagnostic-only.

Pre-PR verification: Java21 build/domain/settings/coarse/probe passes; resource
and catalog checks pass;40 Python tests run (39 pass, one unchanged frozen
positive-path skip). Strict original-source/artifact #47–#53 exports and PR54
analytical/identical-support JSON/archives reproduce. No TD model was executed.
The first local strict-audit directory could not create its junction under the
restricted runner; the complete unchanged audit passed with junction permission
in `runs/acceptance/td-history-strict-premerge-approved`. That is an offline
packaging retry, not a TD launch. Final merge checkout audit is recorded on the PR.
