# Bounded axis discrimination and identical-support CPU controls (#11)

**Diagnostic only. Geometry validation remains insufficient; the historical
matching-request discrepancy remains unexplained. No fresh TD seeds inspected.
Geology-1 is unchanged. #9/#11 remain open.**

[Frozen protocol](td-axis-numerical-protocol.md), [analytical summary](evidence/td-axis-summary.json),
[all exact analytical queries and paths](evidence/td-axis-confinement.zip),
[numerical comparisons](evidence/td-identical.json),
[portable float bits, source bytes, configs and transcripts](evidence/td-identical.zip).
This follows [PR53's retained report](td-geometry-numerics.md).

## Reconciliation and execution provenance

Local main and fetched origin/main both started at1c31c0f. GitHub individually
confirmed merged PR47 d6d59ca,48 db8bcea,49 05bd8b9,50 ce91c6a,51 e3fdbcf,
52 6c5f105 and53 1c31c0f. No applicable AGENTS.md in the checkout or project/user
ancestors; unrelated sibling repositories' instructions do not apply.
Protocol, analytical evaluator and executable CPU collector were committed and
pushed at4a2fa1c BEFORE analytical validation or new TD execution. The collector
retains exact executed sources and verifies their Windows checkout bytes against
that commit, including original CRLF helpers. No later retuning or TD run.

All prior seeds, including2026110407 and -2026110411, are development. The
historical frozen JSON labels such as `held_out` are preserved as historical
labels only; revised work on those seeds is never fresh validation. geometry-arc-1,
its original isolated/saddle false positives, cardinal false negative and all
PR51/52 criteria/exporters remain unchanged. Their failures are not repaired.

## Separate geometric property and analytical result

axis-confinement-1 asks whether a finite path has stronger transverse confinement
than longitudinal curvature. It uses the unchanged geometry-arc-1 bounded center
search, alternatives, greedy branches, turn/edge/ambiguity abstention and no gap
bridging. Shoulders and actual center steps are256 native pixels at every
orientation. Cumulative Euclidean path distance supplies the divided differences.
At each of three interior stations, absolute along-path second derivative times
256 squared is divided by the sum of signed transverse shoulder drops. All three
ratios<=0.25 support; any>=0.5 rejects; the middle interval abstains. Endpoints
do not establish what happens outside the path. Full decisions and exact query
values, including rejected alternatives, are portable.

Linear elevation trends have zero longitudinal curvature, even when original
height-range/residual rules fail. Gentle quadratic and sinusoidal trends can
also pass. Thus changing elevation alone is not rejected. This separate property
rejects the original symmetric isolated extrema and saddles, whose longitudinal
curvature has comparable magnitude to transverse confinement. Original failures
of height-range/residual criteria remain recorded under their original names.

The evaluator was frozen before inspecting240 analytical validation cases.
Development has300 cases; rotations/translations, both ridge/basin signs and15
families are retained. Exact analytical function values replace interpolation for
these controls; no analytic accuracy claim transfers to TD.

| Outcome | Development /300 | Frozen analytical validation /240 |
| --- | ---: | ---: |
| Positive supported |120|80|
| Negative correctly rejected |40|32|
| False positive |40|32|
| False negative |20|8|
| Abstention |80|88|
| Incomplete path (subset of abstentions) |72|64|

Symmetric isolated extrema and saddles reject in all20 development and16
validation cases per family. Straight/curved ridges and asymmetric shoulders
succeed20/20 and16/16. Linear and gentle quadratic trends succeed20/20 development,
12/16 validation; sinusoidal trends20/20 and8/16. Remaining validation trends
abstain under the inherited orientation/alternative rules. Slopes, crossings,
parallel alternatives and true gaps abstain; lack of a complete search path does
not prove physical interruption. Strong nonlinear trends produce20 development
and8 validation false negatives, with8 additional validation abstentions.

The mandatory adversaries expose the limit: elongated isolated quadratic extrema
and shallow saddles pass all20 development and16 validation cases each. These
are **false positives under the requested global feature taxonomy**, even though
they meet the finite-support confinement property. A quadratic along-axis trend
can itself have the same local Hessian signature as a saddle; adding a linear
trend shifts its critical point without removing transverse confinement. Local
anisotropy therefore cannot certify global peak-versus-ridge or saddle-versus-
basin identity. No label was changed and no threshold retuned after validation.
This is a bounded negative discrimination result, not a successful selector.

Six PR53 native candidate fields are reused once each (paired scales are not
recounted). Their old paths and original height/residual failures remain in the
archive; new confinement scores are descriptive only. All six explicitly abstain
from confirmed TD extrema and coverage. Unknown TD between-point error remains
unknown. Bilinear convex combinations and checkerboard perturbations are not
bounds on TD error or proof of unsampled extrema. No fine-support query was
authorized or executed, and no between-sample extremum was manufactured.

## Isolated numerical controls

Only seed -2026110411, native row-14 cols-6/+6 (A/B), was queried. Every new
rectangle was identically256x256 native pixels; withClimate=false. Four NEW
metadata-only fixtures used scales1,1,1,6 and initial ordersAB,AB,BA,AB. No
unsafe seed switching, halo, batching, large patch, corner or broader survey.
Each new float array is retained, including the two real diagnostic-cache misses.

| Controlled comparison | Explicit reference / intervention | Exact outcome |
| --- | --- | --- |
| Same process/history | Initial AB or BA / identical repeat in each process | All bits equal |
| Fresh process | process0 scale1 AB / process1 scale1 AB | All bits equal |
| Request order | process1 scale1 AB / process2 scale1 BA | All bits equal per matching cell |
| Scale | process1 scale1 AB / process3 scale6 AB | All bits equal |
| Diagnostic cache | process0 populated native cache, direct AB / clear cache, direct AB | All bits equal |
| Temporal control | post-clear AB / another AB without clear | All bits equal |
| Public provider clear | preceding AB / public clear then AB | All bits equal; clear is limited |

22 cell-level reference/control comparisons all have zero differing indices,
zero maximum absolute/ULP differences and zero quantized-height differences;
means and relief match exactly. The two capture/population requests also match
the initial direct arrays. The real diagnostic native cache is observed at2
entries and cleared to0 without changing request order. Direct reads bypass it.

Retained javap of the pinned CPU JAR verifies public clearCache clears only
CACHE/PENDING; direct getPipelineData calls pipeline.get on the inference executor.
The public provider cache was already empty (0->0), so that arm is explicitly a
**no-op cache control**, not evidence of a populated-provider-cache effect or a
tensor reset. Tensor stores remain warm. Initial requested cells compute new
windows; repeated reads compute none. Startup already computes4 windows/process,
so even a fresh process is not claimed to have an empty tensor store. Fresh
process, matching startup and fixed order are a separate control from within-
process warming. No supported independent tensor-reset API was found or used.

Every new hash also exactly matches PR53's retained unpadded array and the old
PR52 **scale6** hashes:

- col-6:8d4959a72c842dd9d026288dd1d429df05edf97f285cf7570fbe1c48a5c702ad
- col+6:8bdc29080eeb5dcc3beab568097797e1e61e97f669cad34ef0d9d03828b2a738

Neither historical scale1 hash is reproduced. Historical complete float arrays
were not retained, so historical differing indices and ULPs remain null/unknown.
The retained old mean differences remain7.748603820800781e-7 and
7.003545761108398e-7m; those are failed exact assertions, not tolerated passes.
This matrix excludes these specific controlled interventions as sufficient to
reproduce that discrepancy under this bounded execution history. It does not
establish rounding, caching, scale, an upstream bug or any other cause.

PR53's retained shape/batching arrays and reproducer are reused, not rerun.
They establish request-context sensitivity; that remains different from unequal
hashes on identical request rectangles. No minimal *historical* reproducer is
supported by these results. The original patch-versus-tile corner also remains
unresolved: no bounded new query distinguishing a concrete large-patch hypothesis
was identified, so no small halo was substituted for that context.

## Resources, portability and verification

New raw matrix:runs/acceptance/td-identical-2026-11-04-01. Four launch attempts,
four complete processes; no failed/replacement launches.26 direct requests,
two distinct native supports (131072 distinct sampled native pixels). Repeats,
two scales and fresh processes are paired/recomputed observations, not new
coverage. Each process computes126 windows:4 startup and122 post-startup.
Total504 including16 startup; post-startup488. Public direct counts14/4/4/4;
coarse startup calls1/process, heightmap calls0. Budget26 requests/4 launches/
1500 windows per process/6000 summed held. Checkpoint limits are not presented
as instantaneous inference bounds.

Elapsed221.547s of1800s;6GiB heap; maximum sampled Java working set
12,606,472,192 bytes below16GiB. The1s watchdog checks disk reserve4GiB,
elapsed time and process memory including startup. Samples are not an
instantaneous peak guarantee. A benign process-exit sampling race printed a
Get-Process message after normal shutdown; the process was already exited,
no monitor failure or extra launch resulted. Full samples and partial request
ledger are retained. This completed budget is exhausted; do not rerun collector
without another frozen budget. No extra TD execution for packaging/verification.

Shared model/template manifests match before/after. CPU dependency SHA256 is
3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8.
Portable evidence includes all26 exact arrays, chronological requests/bounds,
before/after counters, raw console transcripts, configs, Java/backend/context,
model/artifact hashes, JVM launch arguments and exact executed source bytes.
Strict exports check source bytes against4a2fa1c using Git's Windows checkout
filters; older CRLF helpers are retained verbatim, never normalized silently.
All four new fixture snapshot files remain byte-identical.

Instrumentation changes only; no production caller or output change. Collection
executed4a2fa1c with an opt-in capture hook in SamplingDiagnostic and new numeric-
control commands in NumericalSupport. A retained-suite source-hash check correctly
rejected that changed historical source. The final packaging restores
SamplingDiagnostic byte-for-byte and relocates the opt-in hook to the separate
NumericalCaptureMixin. This packaging is compile-verified only: the exhausted
budget was not rerun. All runtime results refer exclusively to the retained4a2fa1c
sources and copied probe artifact, never the rebuilt probe. Reproduction of the
executed matrix requires those exact source/artifact bytes and a NEW budget.

Historical strict exporters run unchanged in a separately reconstructed1c31c0f
source checkout with raw evidence read through a junction and original artifacts
copied locally. No source assertion is bypassed. Historical exports use exact
original Windows helper bytes; new export verifies executed4a2fa1c bytes and
immutable per-fixture artifact copies independently. The final historical-source
restoration also permits retained source-hash tests in the live checkout.
Scripts/reexport-td-bounded.py performs the original-source/artifact audit.

Newly executed:540 analytical cases (240 frozen validation), descriptive reuse
of six TD fields, four bounded CPU fixtures, strict bit comparisons and portable
corruption/bounds tests. Reused: all #47–#53 fields/shape arrays, strict failures,
prior original-artifact restoration/save/reopen/block and529 persisted-container
acceptance. Those continuing-save acceptance tests were NOT newly executed.

Verification passes Java21 build/domain/settings/coarse/probe tasks, resource
and catalog checks, and38 tests (37 pass; one unchanged frozen positive-path
skip), including portable/negative suites, new analytical/array replay, bit
corruption and request-bound corruption. Process/listener inspection found no
remaining diagnostic JVM/collector or game/RCON/explorer listener. Strict retained #47–#53 exports and
new archives must reproduce after the final Windows checkout; PR/CI/merge and
that final result are recorded with the completed PR. Failed PR51 `Paired coarse
drift`, PR52 `Actual matching native support changed`, original height criteria
and #5 stronger final-block assertion remain failed. Optional Ulti-World,
immutable shared inputs and unrelated temp/ are untouched.

## Concrete remaining gates

Geometry: define the observation extent and intended local-versus-global feature
property that can distinguish the retained shallow-saddle/elongated-extremum
aliases without discarding legitimate trends, then test a newly frozen analytical
set. Establish observed TD support or a defensible uncertainty policy before
confirming extrema; the present interpolation evidence cannot do that. Do not
expand a terrain survey to conceal these analytical failures.

Numerics: obtain a concrete execution-history hypothesis beyond these isolated
controls that reproduces the historical scale1 hashes on identical rectangles.
There is no recoverable old full-array difference map and no supported independent
tensor clear in this experiment. Preserve the unresolved historical assertion
until a bounded reproducer exists. Either insufficient gate keeps this slice
diagnostic-only. No fresh TD seeds or production adoption follow.

Morphology does not establish geological plausibility. Geological interpretations
remain competing seeded synthetic hypotheses with uncertainty and abstention.
Fine points, native means, coarse neighborhood range, scaled tiles and fine
relief stay separate; different anchors are distinct from unequal matching-support
hashes. No p5, transferred geology-1 cutoffs, palettes/dikes/minerals/integrations.
Future output adoption still requires immutable generator identity, explicit
new-world-only selection, genuine bidirectional continuing-save rejection,
exact original-artifact restoration/reopen and complete snapshot/block/persisted-
container preservation. Never migrate continuing geology-1 snapshots. Integrated
candidates additionally require alternating paired CPU startup/cold/warm/full-route
benchmarks on NEW fixtures; isolated-query savings never imply route savings.
