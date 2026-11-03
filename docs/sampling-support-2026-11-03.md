# Sampling representativeness diagnostic (#11)

## Predeclared experiment

Production remains geology-1. This experiment changes only the opt-in probe and
offline analysis. No geological classifier or new-world generator is adopted.

**Selected policy: actual-target terrain evidence for point diagnostics;
geological classification abstains.** Keep the existing bounded 3x3 getter,
centered on the target-containing native coarse cell, and distinguish its central
mean from neighborhood context. Retain independently collected target fine cells
and tiles for validation. Province-anchor terrain is retained as a comparison,
not substituted for target terrain. The tested four-cell representative grid
does not improve the held-out point diagnostics. Geology-1 remains a regional
assignment with its original anchor, thresholds and generated output.

[Portable evidence](evidence/sampling-support-2026-11-03.json) contains the raw
numeric observations, selections, source/artifact/log hashes, request accounting,
paired-scale checks, analytical controls and persistence outcomes.

## Terrain agreement results

Cells below show central coarse versus actual-target full native fine-cell
**mean absolute error in metres; central sign agreements / selection rows**.
Only scale-1 rows enter this native comparison; scale 6 is paired sensitivity,
not additional independent native observations.

| Native cohort | Province anchor | Actual target | Fixed grid 4 |
| --- | ---: | ---: | ---: |
| Development fixed coverage | 1289.53; 5/10 | 124.58; 10/10 | 978.00; 8/10 |
| Development selected contrasts | 1335.75; 9/14 | 80.06; 14/14 | 875.88; 10/14 |
| Held-out fixed coverage | 1282.66; 3/5 | 50.49; 5/5 | 672.42; 3/5 |
| Held-out selected contrasts | 1855.87; 4/7 | 106.31; 7/7 | 693.89; 6/7 |

Target evidence passes the frozen held-out rule in both groups. These fixed
transects and selected contrasts are descriptive observations, not a population
accuracy estimate. Boundary stress cases are evaluated separately below.

In development coverage, anchor coarse means agree with their own matched fine
support to 44.27 m MAE, while their error at targets is 1289.53 m. The fine anchor
means themselves differ from fine target means by 1306.11 m MAE. This separates
the displacement problem from coarse/fine model-product disagreement. Changing
relief cutoffs would leave that displacement intact. Even target means retain
model-product residuals, and sign agreement of averages does not validate fine
shoreline exposure or discriminate geological histories.

Target 3x3 neighborhood tendency agrees with the target fine-cell pixel-sign
tendency at 9/10 development coverage locations, 14/14 selected contrasts,
4/5 held-out coverage locations and 7/7 held-out contrasts. This is explicitly
**different support**, not shoreline accuracy: a mixed-sign neighborhood can
surround a wholly positive or negative fine cell. Fine-cell below-zero fractions
and all three policies' corresponding comparisons remain in the portable data.

The selection and recommendation rules were committed and pushed in
`c4cdd43928267aad72f1fced36774579985fe123` before held-out collection. The portable
export identifies that protocol and the exact executed source/probe bytes;
exporter serialization normalization does not change the selections or criteria.

## Reconciliation and retained evidence

Fetched main and local base are PR #49 merge
`05bd8b9accf80f699eb3bc5589f4b280fe9a5eae`. GitHub confirms #47, #48 and #49
merged and #9/#11 open. No repository or ancestor AGENTS.md exists. Read the
workflow, upgrade/recovery and reproducibility contracts, prior diagnostic and
coarse reports, source and portable evidence. PR #47's near/cold exporter and
exact PR #46 artifact comparison pass again; PR #48's strict source/artifact/log
export passes again. Both reproduce their committed JSON values exactly. These
are retained-evidence revalidations, not fresh runs of the earlier JVM matrices.

PR #48's six selected disagreements are three distinct seed/stratum cases
repeated across scales, not six independent coarse observations or an unbiased
error rate. This slice addresses the missing actual-target fine observations.
PR #47's single-direction identity-only rejection is not a bidirectional
generator upgrade acceptance. Its isolated-query timing remains separate from
the historical 14.383-second route scope and PR #46's inconclusive cold-route
saving. #5's stronger final-block assertion stays visibly failed; no strict guard
is weakened. Ulti-World is optional; shared inputs and unrelated temp/ stay intact.

## Frozen selection and evaluation

Development seeds: -1550453200536840819 and 8675309. Held-out seed: 20261103.
Both scales 1/6 run the identical frozen selection/evaluation rules; no tuning
after held-out observations. Repeated scales are paired scale sensitivity,
never independent native coarse observations.

Screen the same bounded 9x9 signed native lattice as PR #48 (-64..64, step 16).
Fine survey: five preselected lattice positions (indices 0,20,40,60,80) provide
fixed diagonal-transect coverage, not a random population estimate or uniform
two-dimensional fine coverage. The coarse screening lattice is two dimensional.
Deliberately selected
contrasts: the four previous ocean/coast/lowest-land/highest-land strata,
median land, and maximal ridge/basin candidate scores. The last two maximize
signed strong axial second difference minus absolute weak axial second
difference over the 3x3 halo. They select anisotropic curvature candidates,
not proven elongated geological structures. Record both curvatures and scores.
Every selected survey receives fine evidence at its actual location and anchor.
Four signed coarse/fixed-grid edge pairs and two independent province contacts
add twelve boundary locations per fixture. No infinite search or flood fill.

Compare exactly three policies: current province-anchor 3x3 coarse evidence,
target-containing coarse-cell 3x3 evidence, and a fixed global 4x4-cell partition
represented by its central cell (index floor(index/4)*4+2). All use the same
128-entry coarse LRU. The fixed-grid policy is deliberately simple and bounded;
its grid seams must be measured, not assumed smooth.

For each policy obtain the full 256x256 native fine elevation cell at its
representative location and compare its mean to the central coarse elevation.
The complete-cell fingerprint encodes all 65,536 IEEE-754 float32 values in
row-major, big-endian order; the 25 quantized fine-tile values are retained directly.
These rectangles have matched coordinate support. The learned coarse average
and generated native fine elevation remain different model products, so equality
is not assumed. The policy's central coarse elevation is also compared to the
actual target's full native fine-cell mean: this measures representation loss
separately from the model-product discrepancy. A new 128-entry native-cell LRU
bounds this evidence; strict context checks run before hits and after inference.
Fine-cell below-zero pixel fractions expose local mixed signs even when coarse
averages do not. Comparing that cell's exposure tendency with a 3x3 coarse
neighborhood still has different support and is not shoreline accuracy or a
measurement of final Minecraft surface blocks.

Also retain geology-1-compatible 25 quantized samples in the 256-block fine tile
at the actual target and province anchor. Scale 6 retains TD's upsample/noise
path. Tiles are floor-aligned to the 256-block world grid; their actual origins
and sample values are retained. Their nominal native footprint is 256 pixels at
scale 1 and about 42.7 at scale 6. The matched native cell remains a separate
model-native statistic, not a complete scaled Minecraft surface. These tiles do
not match a 3x3 coarse neighborhood; neighborhood range and
fine-tile relief remain distinct. p5 is excluded. No geology-1 threshold transfers.

Evaluation is descriptive, split by development/held-out and coverage/selected
extremes/boundaries. Report sign agreement, absolute mean error, shared-cell
coherence, edge jumps, forward/reverse exact evidence equality, retained cache
sizes, actual accessor/new-window deltas and unique requested support counts.
Prefer target evidence only if both held-out coverage and selected-contrast
groups have mean absolute target error no worse and central sign agreement no
worse than either displacement alternative. Otherwise select no supported
winner. Boundary stress cases remain separate. Do not turn morphology into rock labels.
No statistical population accuracy claim or route-speed extrapolation is allowed.
Reverse traversal clears both diagnostic LRUs, then recomputes evidence against
already visited TD windows; TD's provider heightmap cache remains warm. This is
evidence traversal independence, not fresh-process final-feature determinism.
The exporter also requires exact anchor fine mean/relief equality for the sixteen
repeated selected comparisons against retained PR #48 geology-1 results.

Geological policy: each sign class retains two competing synthetic hypotheses
(marine sedimentary/mafic oceanic; sedimentary margin/inherited belt;
platform/uplifted-intrusive). Assign deterministic seeded ordering and weights
in [0.4,0.6] per native cell using SHA-256 of the versioned ASCII seed/row/column
key. These arbitrary weights are explicit uncalibrated synthetic priors, not a
posterior, training result or reconstructed tectonic history. Geological
confidence is unestablished and rock selection always abstains. Morphological
validation cannot establish geological plausibility.

Supplementary known-shape stress controls use analytic Gaussian ridges/basins
with negative center (-1024,-512), widths 128/2048 native pixels (16:1), both
orientations, signed amplitudes +/-1600 m and offsets -/+400 m. A fixed 9x5
long-axis/cross-axis survey spans shoulders and centers across many coarse,
fixed-grid and province cells. Complete discrete coarse-cell means are compared
with 25 actual target-tile values. These controlled elongated shapes test
sampling displacement independently of TD's learned coarse/fine relationship;
they cannot validate TD landform quality, geological history or runtime costs.

Any future changed output requires a distinct immutable generator identity,
explicit new-world-only selection, genuine continuing-save rejection in both
directions, exact original-artifact restoration/reopen, unchanged snapshot bytes,
complete sampled blocks and all persisted coverage/status/block containers.
Never rewrite or silently migrate geology-1 snapshots. An integrated candidate
also requires alternating paired CPU benchmarks against then-current main on NEW
fixtures separating startup, genuine cold tensors, warm sampling and full routes
with actual deduplicated requests/new windows. PR #47 isolated-query savings do
not establish route savings. This diagnostic introduces no integrated candidate.

## Runtime and reproduction

MC 1.21.1 / NeoForge 21.1.251 / official TD 2.3.0 CPU
`3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`,
Java 21.0.6 / Windows 11 amd64, tile 256, model/config aggregate
`64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`.
Production addon SHA-256 remains
`c5775ecafaefaaebb192d81152ab128d291d98e824fd4794e4b8d61f20850fa2`.

NEW metadata-only fixtures establish their seed/scale before first launch and
copy no terrain from the unchanged template. This is fixture construction, not
continuing-save migration or mismatch acceptance. Immutable TD/models are linked;
addon/probe bytes are copied. Only stopped disposable model optimization caches
are cleaned. Raw results/logs/worlds remain ignored under
`runs/acceptance/sampling-support-2026-11-03-01`.

Each fixture generates the complete sample chunk (-32,-65), saves/stops and
reopens in a fresh JVM. Require complete sample hashes, exact snapshot bytes and
all persisted Overworld records' coverage/status/section block-state containers
to match. Raw region metadata is not used as a terrain-equivalence oracle.

```powershell
./scripts/bootstrap.ps1
./gradlew.bat build runtimeProbeJar
python scripts/verify-sampling-support.py --java <java21> --td <official-cpu-jar> --baseline <retained-main-addon> --output <NEW-output>
python scripts/summarize-sampling-support.py <NEW-output> --output <portable-json>
python scripts/test-sampling-support.py
```

The exporter checks executed source bytes (including probe Java), copied
artifacts and raw-log hashes, directly matches every forward/reverse observation
against raw runtime JSON, independently simulates request deduplication/LRU
counts, recomputes the frozen selections and validates persistence outcomes.
Python/Java source LF attributes preserve executed bytes after Windows checkout.
CI runs build/probe/domain/resource/catalog and offline diagnostic checks;
dedicated inference and save/reopen remain local runtime evidence.

## Runtime outcomes and request accounting

All six NEW fixtures / twelve JVM launches pass. There are 486 screened
neighborhood rows but only 243 distinct seed/native screen locations; 144 forward
comparison rows cover 66 distinct seed/native target cells and 166 distinct
seed/native policy representatives. Another 144 rows reverse traversal after both
diagnostic LRUs are cleared. Distinct cells also share spatial context; these
counts do not establish statistical independence.

For each seed, all 36 paired selected-location/policy rows have identical complete
native-cell hashes across scales, with zero mean difference. The sixteen repeated
development anchor mean/relief pairs exactly match retained PR #48 geology-1.
Every fixture preserves exact snapshot bytes, complete sampled blocks and all
529 persisted terrain records' coverage/status/block-state containers through
fresh-process reopen. Shared model/template manifests remain unchanged.

Each fixture performs 72 forward policy lookups. Actual public coarse calls
equal 54 or 56 deduplicated 3x3 requests, independently reproduced by the exporter.
Native-cell misses also equal 54 or 56; two additional fine-tile reads occur per
location. The table covers only the 24 forward comparisons and their reverse
recomputation, excluding startup, the screening lattice, cache/oracle suites and
production chunk generation.

| Seed | Scale | Coarse API calls | Direct fine-data API calls | Heightmap API calls | New windows forward / reverse |
| --- | ---: | ---: | ---: | ---: | ---: |
| -1550453200536840819 | 1 | 54 | 102 | 0 | 2300 / 241 |
| -1550453200536840819 | 6 | 54 | 54 | 48 | 2300 / 246 |
| 8675309 | 1 | 56 | 104 | 0 | 2287 / 253 |
| 8675309 | 6 | 56 | 56 | 48 | 2284 / 249 |
| 20261103 | 1 | 56 | 104 | 0 | 2367 / 258 |
| 20261103 | 6 | 56 | 56 | 48 | 2361 / 265 |

Reverse traversal reproduces complete evidence exactly while generating additional
windows: visited support is not guaranteed to remain cached. All shared-cell
coarse/native evidence is identical. Each real coarse suite deduplicates four
callers to one request, retains 128 entries after 129 misses and requests an
evicted entry again. The new native-cell LRU is capped at 128; its observed peak
is 56, so this slice does not claim a separate 129-cell native eviction runtime test.
Unique halo cells, representative cells, public API requests and model windows
are retained as distinct units.

These are combined serial diagnostic workloads sharing TD caches, not independent
per-policy CPU benchmarks. Positive new-window counts prove actual computation;
they do not isolate genuine cold tensor timing, warm accessor cost or full-route
savings. No integrated candidate or alternating paired route benchmark is claimed.

## Elongated morphology coverage and its limit

The six distinct TD ridge/basin candidates (repeated at scales 1/6) all have axial
curvature ratios above two, but **none is a cross-axis local extremum**. Strong
anisotropic second differences can select a curved slope. This is a failed TD
ridge/basin selection gate, not validated extended landform coverage; the frozen
selector was not retuned on held-out results.

The supplementary analytical controls supply two known elongated shapes, each
repeated with two seeded province layouts. Across each fixed 45-location survey,
target-cell errors are 9.57 m MAE with 45/45 sign agreements. The tested fixed
grid has about 316.5 m MAE and 27/45 agreements; anchors span 306.9–438.6 m MAE
and 20–28/45 agreements. The two shapes and repeated layouts are not four
independent TD landforms. Their nonzero target error also reflects full-cell
averaging versus 25-point fine sampling. They demonstrate narrow-feature
displacement under known geometry, not geological plausibility or TD accuracy.

The concrete morphology gate is now sharper: predefine a bounded TD selector
requiring actual cross-axis extrema plus longitudinal support and validate it
on new seeds with fine observations along the selected features. The present
evidence supports actual-target point diagnostics but not a coherent terrane or
contact classifier.

## Verification boundary

JDK 21 build/domain/settings/coarse/probe checks, resource checks (64 blocks,
158 recipes, 711 JSON), research catalog, Python syntax, existing diagnostic
tests, eight new semantic/portable-evidence tests and strict raw export pass.
All production JAR entries equal the retained main artifact; the probe SHA-256 is
`abf66093bc7cdca8254c7fc6c8178358628d7dcdc381f544203278276c553a9c`.
All test Java/Python processes exit. Only stopped disposable optimization caches
are removed; about 2.26 GiB free remains after collection. Broad ore/carver,
client and pack coverage is retained historical evidence, not newly run here.
The stronger #5 failure, optional Ulti-World, unrelated temp/ and strict guards
remain unchanged. #9 and #11 remain open.

## Boundary interpretation

For the original development seed at scale 1, two preselected edges illustrate
the distinction between evidence coherence and terrain representation:

| Adjacent queried positions | Anchor central mean jump (m) | Target central mean jump (m) | Fixed-grid central mean jump (m) | Target fine-tile mean jump (m) |
| --- | ---: | ---: | ---: | ---: |
| (-1996,-1024) to (-1995,-1024), province contact | 1319.52 | 0 | 0 | 0 |
| (-1025,-512) to (-1024,-512), negative grid seam | 0 | 1694.32 | 5089.69 | 1749.60 |

These are jumps between support statistics, not one-block physical cliffs. A
province contact can switch distant anchor evidence while target support stays
fixed. The four-cell grid can impose a much larger representative jump at its own
seam. Target-cell evidence also steps at coarse-cell edges; it is not a validated
continuous-contact algorithm. Constant evidence within a cell is a cache/coherence
property, not proof that it represents every fine pixel in that cell.

## Concrete remaining geological gate

The synthetic priors have no independent geological calibration. Even exact
terrain-mean agreement cannot distinguish a sedimentary domain from a mafic or
inherited belt. No posterior, geological confidence or rock selection is supported.
Before classification, pre-register a seeded synthetic-history model and explicit
plausibility constraints independent of current elevation, then test competing
hypotheses, ambiguity and abstention on new held-out terrain. In particular,
measure domain connectivity, contact continuity/orientation and coherent competing
interpretations over two-dimensional transects rather than rewarding constant
labels or assuming present elevation is formation depth. The current cellwise
prior demonstration is not a coherent terrane model and passes no such gate.

Morphological gates also remain narrower than geological adoption: denser
two-dimensional fine coverage of coast/island exposure and long TD ridges/basins,
plus a declared contact bandwidth, are needed before claiming continuous
terrain-informed contacts. The five fixed fine coverage points are a diagonal
transect; selected extremes and analytical elongated controls cannot establish
population accuracy. Matched central-cell support does not make a whole 3x3
neighborhood equivalent to a fine tile. No conversion factor or geological
threshold is fitted from these different ranges. Palettes, dikes, mineral systems
and integrations remain outside this slice.
