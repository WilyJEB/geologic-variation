# Terrain-informed classification diagnostics (#11)

## Decision and scope

Continue merged PR #47 with a **diagnostic-only terrain-tendency classifier**.
No output-changing geological classifier is justified by this slice. All entries
of the production addon JAR equal the retained main artifact; geology-1, its
classification thresholds, province identities, save guards and generated blocks
are unchanged. The extra command is in the opt-in probe excluded from releases.
The Python classifier consumes exported evidence and has no worldgen caller.

`terrain-tendency-diagnostic-1` describes nine coarse elevations as ocean
(all below zero), coast (negative and nonnegative values), or land (all
nonnegative). Zero is the elevation datum, not a fitted relief cutoff. This
describes coarse average-elevation tendency, not guaranteed fine-resolution
shoreline location. Even unanimous signs do not rule out unresolved islands,
valleys or local exposure. It assigns no rocks and explicitly reports geological
confidence as unestablished.

Possible marine sedimentary/mafic domains, sedimentary margins/inherited belts,
or platforms/uplifted/intrusive belts are **synthetic geological hypotheses**,
not recovered tectonic history. Multiple competing hypotheses remain in every
class. Climate, physical formation depth, tectonic plates and mineralization
are not inferred. p5 is excluded: PR #47's metadata checks do not establish its
training statistic or pooling meaning.

## Reconciliation

Fetched origin/main and local main matched PR #47 merge
`d6d59cae4e46dd7a09ff6c27f77645cfb03a736b`. Read current GitHub #11, #9 and
PR #47, repository workflow, reproducibility and world-upgrade contracts and
retained coarse-prototype report/code/evidence. No ancestor AGENTS.md was found.
The branch follows the repository's `feature/` convention.

Re-ran PR #47's exporter against its retained near/cold raw fixtures and exact
PR #46 baseline artifact. Source/artifact/raw-log and rejection/restoration
validation passes; exported JSON values equal the committed PR #47 evidence.
This is revalidation of retained evidence, not a rerun of its JVM matrix.

A post-merge Windows checkout exposed automatic CRLF conversion of the new
Python sources. The three new scripts are now pinned to LF in `.gitattributes`,
matching their exact executed bytes. Re-export after restoring those checkout
bytes passes strict source hashes and reproduces all committed JSON values;
no raw result, artifact or recorded source digest was changed.

PR #47 established the supported blocking coarse API, signed coordinates,
Explorer channel oracle, bounded/deduplicated evidence caching and isolated CPU
query measurements. Its numerical savings are not route savings. Its alternate
artifact test established one generator-only rejection direction, not an accepted
new algorithm or a bidirectional upgrade matrix. Those limits remain visible.

#11's dikes, contacts, layer palettes and geological calibration remain open.
#9 remains open. #5's stronger failed final-block assertion is unchanged; these
tests do not normalize it into a pass. Ulti-World stays optional; shared inputs
and unrelated `temp/` are preserved.

## Diagnostic design

The new `acceptance terrain-compare x z` resolves the unchanged production
province, returns its complete identity/anchor, geology-1 stone and fine-tile
mean/relief, and samples PR #47's coarse adapter at that **same anchor**. It
does not independently resample or replace geology-1.

The inputs have different spatial support:

- Fine-tile relief: range of geology-1's 25 sampled, quantized fine heights in
  its 256-block anchor tile. Scale 6 retains the existing upsampled/noisy path.
- Coarse neighborhood range: max minus min of nine decoded coarse averages
  over a 3x3 neighborhood, each cell spanning `256 * scale` blocks.
- Survey point versus province anchor: a survey point may be assigned a
  province with an anchor far enough away to have different terrain tendency.

No fine-relief, ocean-ceiling, lowland or mountain thresholds are applied to the
coarse range. No numerical range equivalence, geological truth labels, trained
decision boundary or held-out classification accuracy is claimed.

## Runtime protocol and evidence

[Portable evidence](evidence/terrain-diagnostics-2026-11-03.json) retains raw
survey values, selections, comparisons, identities, classifications, artifact/
source/log hashes and persistence results. Raw worlds/logs remain ignored under
`runs/acceptance/terrain-diagnostics-2026-11-03-02`; they are not uploaded.
Attempt `-01` was denied at the first hardlink before launch and supplies no
runtime evidence.

Four NEW metadata-only fixtures use seeds `-1550453200536840819` and `8675309`
at scales 1/6. Before first launch only, each new fixture's seed metadata and
matching snapshot seed are established together; no terrain is copied from the
template. This is new-fixture construction, not continuing-save migration or
manufactured mismatch evidence. The original template is never launched.

Each fixture surveys a fixed 9x9 signed global lattice: coarse indices -64..64
in steps of 16, with a 3x3 halo per point. The survey is bounded; no unbounded
continent search or flood fill occurs. Four deterministic strata select deepest
unanimous-negative neighborhood, mixed-sign neighborhood closest to zero mean,
and lowest/highest mean unanimous-land neighborhoods. The latter two are called
lowland/mountain **sampling strata**, not validated terrain or lithological
labels. The diagnostic preserves both point evidence and anchor evidence so
selection at one location cannot conceal contradictory evidence at the other.

Six signed boundary queries include both sides of a negative coarse-cell edge,
negative axes, and an actual nearest-site province contact located with the
independent Python oracle. Reverse order follows a coarse-cache clear and must
return identical complete comparison objects. The production fine cache remains
warm during reversal; this tests coarse recomputation, not fresh-JVM final-feature
determinism. PR #47's four-caller same-cell test and real 129-entry/128-retained
LRU/eviction test run in every fixture. Explorer's asymmetric six-channel oracle
also runs in every fixture; decoding p5 for an oracle never makes it a classifier
input.

Each fixture then generates the complete sample chunk at (-32,-65), saves/stops,
and reopens in a fresh JVM. Complete sampled-block hashes, exact snapshot bytes,
and every persisted Overworld record's coverage, status and section block-state
containers must match. Raw region timestamps/light/ticks are excluded from the
terrain identity. Models and template manifests must remain unchanged; addon
and probe are copied, immutable TD/models linked. Only stopped NEW fixtures'
regenerable ONNX caches are removed.

Pinned runtime: MC 1.21.1, NeoForge 21.1.251, official TD 2.3.0 CPU
`3212b53c…4092fe8`, Java 21.0.6, Windows 11/amd64, tile 256, model/config
aggregate `64fe6b1a…39601d9`. CPU is required from resolved context. Production
artifact is `c5775ecafaefaaebb192d81152ab128d291d98e824fd4794e4b8d61f20850fa2`.

## Results

All four cases and eight JVM launches pass. There are 324 surveyed neighborhoods
(162 distinct seed/native locations repeated at two scales), 16 selected
point/anchor comparisons, 24 forward signed-boundary comparisons and 24 reverse
comparisons. Each case retains exactly 128 real cache entries after 129 distinct
samples, deduplicates four concurrent callers to one coarse request and requests
an evicted entry again. All four Explorer oracles pass. Each save/reopen preserves
all 529 persisted records, the complete sample block hash and exact snapshot
bytes. Source/model/template manifests and original production bytes are unchanged.

| Seed | Scale | Survey ocean / coast / land | Persisted records |
| --- | --- | --- | --- |
| -1550453200536840819 | 1 | 40 / 17 / 24 | 529 |
| -1550453200536840819 | 6 | 40 / 17 / 24 | 529 |
| 8675309 | 1 | 32 / 28 / 21 | 529 |
| 8675309 | 6 | 32 / 28 / 21 | 529 |

The coarse neighborhood ranges at selected province anchors span
1228.53–2833.06 m; fine-tile relief spans 21–1792 m. Their median paired
difference is 1063.88 m in this selected sample, **not a conversion factor**.
The coarse evidence repeats across scales at these corresponding native
locations; those repetitions are not independent geological observations.
Fine support changes with scale, and scale 6 follows the existing heightmap path.

| Seed / sampling stratum | Survey mean (m) | Anchor coarse mean (m) | Coarse range (m) | Fine relief scale 1 / 6 (m) |
| --- | --- | --- | --- | --- |
| original / ocean | -5305.28 | -2752.05 | 1927.69 | 841 / 299 |
| original / coast | 4.40 | 554.88 | 1290.83 | 1377 / 583 |
| original / lowland | 245.51 | 1450.37 | 1755.21 | 1783 / 59 |
| original / mountain | 2970.30 | -518.03 | 2139.73 | 1732 / 29 |
| 8675309 / ocean | -5423.71 | -3830.62 | 2833.06 | 1792 / 467 |
| 8675309 / coast | 9.59 | -210.19 | 1228.53 | 1016 / 52 |
| 8675309 / lowland | 221.85 | 71.30 | 1401.67 | 387 / 21 |
| 8675309 / mountain | 3440.89 | 2059.16 | 1789.16 | 1438 / 293 |

Here “original” denotes seed -1550453200536840819. Six of 16 selected comparisons
(three distinct seed/stratum pairs repeated across scales) change sign-based
terrain tendency between survey and province anchor. The original seed's highest
survey-land mean is 2970.30 m, yet its anchor neighborhood mean is -518.03 m and
mixed-sign. Its lowest-land survey becomes a much higher anchor. These selected
extremes demonstrate a representativeness problem; they do not estimate an
unbiased population error rate. Refining range thresholds alone cannot resolve
that anchoring mismatch.

**Decision: keep only offline terrain tendency and competing synthetic hypotheses;
do not integrate geological classification or replace the production sampler.**
The fixed grid covers useful contrasts but not independent fine-resolution terrain
labels at every survey point. It cannot validate geological classes, shoreline
accuracy, elongated contacts or a new generator.

JDK 21 build/domain/settings/coarse/probe checks, resource checks (64 blocks,
158 recipes, 711 JSON), research catalog, Python syntax, diagnostic tests,
portable raw/source/artifact validation and retained PR #47 revalidation pass.
Final process/listener checks find no Java/Python test process or game/RCON
listener. About 5.04 GiB free remains. Broad ore/carver/client/pack acceptance is
retained historical evidence, not newly executed here; production is unchanged.

## Concrete remaining adoption gate

Choose a shared sampling/anchoring policy and gather independent, spatially
representative calibration/validation evidence before turning these hypotheses
into rocks. In particular, validate fine terrain at actual target locations as
well as province anchors, refine ocean/coast exposure, distinguish neighborhood
range from fine relief and cover intermediate elevations, multiple contacts,
elongated ridges/basins and held-out seeds. Four selected strata per fixture do
not establish geological confidence or universal mountain/lowland thresholds.
No broad geological terrane or contact classifier is accepted here.

Specify seeded synthetic-history priors and measurable plausibility/coherence
criteria rather than treating topography as geological ground truth. Validate
those criteria on held-out terrain, report competing interpretations and abstain
where inputs cannot distinguish them. This design work remains necessary even
if morphological threshold calibration later succeeds.

Before any changed worldgen output is adopted, implement a distinct immutable
generator identity and an explicit opt-in **new-world-only** selection policy.
Continuing worlds must select their saved supported generator or reject; config
edits must never upgrade geology-1. The diagnostic ID is not that generator ID,
is never written into saves and is not a new-world option. Current production
continues to support geology-1 alone.

Acceptance must use genuinely generated continuing fixtures in both version
directions, reject with the exact intended context differences before Ready,
restore each fixture's exact original addon bytes and reopen, preserving snapshot
bytes, complete sampled blocks and all persisted coverage/status/block containers.
Never edit geology-1 snapshots to simulate acceptance or migrate them silently.
PR #47's identity-only single-direction test cannot satisfy this gate.

An integrated candidate must then receive alternating paired CPU runs against
current main on NEW disposable fixtures, separately reporting startup, genuine
cold tensors with positive newly computed windows, warm sampling and full chunk
routes. Count actual accessor entries and new windows, including overlaps and
cache hits. No integrated candidate or performance benchmark is introduced here;
startup durations and chunk-command timings in raw evidence are operational
records, not comparative benchmarks. No PR #47 isolated-query saving is
extrapolated into route savings.

## Reproduction

With the pinned Java/CPU inputs and a retained exact main addon:

```powershell
./gradlew.bat build runtimeProbeJar
python scripts/verify-terrain-diagnostics.py --java <java21> --td <cpu-jar> --baseline <main-addon> --output <NEW-output>
python scripts/summarize-terrain-diagnostics.py <NEW-output> --output <portable-json>
python scripts/test-terrain-diagnostics.py
```

The exporter verifies the exact matrix, source/artifact/raw-log hashes, stratum
selection, oracle/cache/traversal checks and persistence outcomes before emitting
classifications. CI builds the probe and production addon and tests sign/datum,
mixed-neighborhood, unavailable-input and p5 exclusion behavior; local dedicated
runtime evidence remains separate from CI.
