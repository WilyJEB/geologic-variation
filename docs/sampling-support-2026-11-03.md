# Sampling representativeness diagnostic (#11)

## Predeclared experiment

Production remains geology-1. This experiment changes only the opt-in probe and
offline analysis. No geological classifier or new-world generator is adopted.

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
path. These tiles do not match a 3x3 coarse neighborhood; neighborhood range and
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
