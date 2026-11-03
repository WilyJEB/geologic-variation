# Bounded coarse evidence prototype (#11)

## Scope and reconciliation

Local and fetched origin/main matched merged PR #46 at
`d0020d1710ece2bfa08ea79c20d4b6661bb26b16`. No ancestor/repository AGENTS.md
was found. The repository workflow, reproducibility contract, world-upgrade
rules, #11's coarse API contract and #9's remaining gates were reconciled.
Unrelated untracked `temp/` is preserved. Ulti-World remains optional.

Production remains **geology-1**, with the identical sampler, province rules,
classification, block application and strict generation-context guards. The new
codec has no production caller. The adapter lives in the opt-in runtime probe,
which is excluded from release JARs. Its identity is `coarse-evidence-1`; it
returns explicitly unclassified evidence, never a replacement stone palette.
All 31 pre-existing production class files compare byte-for-byte equal to the
retained PR #46 candidate JAR; only the unused `CoarseEvidence` codec class is added.

The broader #11 terrane/contact/minette design is not implemented here. #9 stays
open. The stronger #5 strict post-feature assertion remains failed and unchanged;
this slice does not turn it into a passing assertion.

## Validated input contract

Pinned TD source `8acd2b680ee248334637f8cf13f6c78ac20003da` exposes the supported,
blocking `LocalTerrainProvider.getPipelineCoarse(row0,col0,row1,col1)` API.
Its bounds are exclusive, row is z and column is x. One coarse index spans
256 native pixels, or `256 * worldScale` Minecraft blocks. Negative coordinates
use integer floor division directly by that product. The 30-metre native
resolution is physical elevation/grid metadata, not another block-coordinate
factor. Metadata checks require latent compression 8, coarse pooling 1, native
resolution 30, and average elevation/p5 pooling for this pinned experiment.

`WorldPipeline.generateCoarse` already applies model means/stds before weighting
its six signals. Divide each channel by channel 6's blend weight exactly once;
do not apply means/stds again. Channels 0/1 use signed square to undo signed
square root. Channels 2–5 retain TD's denormalized temperature, seasonality,
precipitation and variability values. Invalid/nonfinite signals or weight <=1e-8
are unavailable evidence, not zero elevation. The prototype rejects unavailable
elevation rather than classifying it.

The runtime oracle compares all six decoded channels over an asymmetric 2x3
rectangle against TD Explorer's own `coarseChannel`, then checks each raw cell
against independent one-cell API slices. Domain tests cover negative axes and
both sides of coarse boundaries at scales 1/6, weighted signed-square examples,
invalid weights/signals, and incompatible generator identities.

TD derives channel 1 as channel 0 minus the model's second denormalized output,
then Explorer applies signed square. The retained model metadata says average
p5 pooling. This does not establish the underlying training statistic/percentile
or justify interpreting p5 as local relief. **p5 is not used.** The 3x3 elevation
range is explicitly a neighborhood range, not geology-1's 5x5 fine-tile relief.
Neither terrain nor climate recovers physical tectonic plates or formation depth.

## Bounds, determinism and guarding

The adapter requests exactly one 3x3 coarse neighborhood around the current
province anchor's containing global coarse cell. A 128-entry LRU bounds retained
decoded evidence; values are immutable. Owner, seed, scale, saved settings and
global cell identify entries. Serialized misses deduplicate concurrent callers.
The production current-context check runs before cache hits and after inference;
failures clear the prototype cache. Inference-thread callers reject before taking
the monitor or entering the blocking API, avoiding executor/monitor lock inversion.
No inference callback schedules blocking work.

The runtime suite exercises four simultaneous same-cell callers, reversed
exploration across signed coordinate boundaries, 129 real cache entries, bounded
128-entry retention and actual recomputation of an evicted cell. This is stronger
than a synthetic map-only capacity test, but not broad integrated-world lifecycle
or in-flight edit certification.

## Measurement protocol

`scripts/verify-coarse-prototype.py` creates eight NEW metadata-only worlds:
three alternating current/coarse pairs at scale 1 and one exploratory pair at
scale 6. Both arms use the current production addon and same probe. Only the
diagnostic command chooses the measured sampler; generated chunks always use
geology-1. Fresh-process startup resolves TD/backend as required by the existing
save guard; "cold" means the first remote sampler query after this common startup,
not cold native/model initialization. OS filesystem caches are not flushed.

Each arm times a remote query at 8192*scale on both axes, five same-region cache
hits, then a second remote query at 4096*scale. The coarse arm resolves the exact
same production province anchor before mapping to coarse coordinates. Timing is
inside the server command around sampler execution; RCON and hashing are outside
the interval. Before/after counters record actual heightmap, elevation and coarse
API entries and newly computed TD windows. Counts are not overlapping wait times.
Oracle/cache-pressure tests and chunk generation occur after sampler measurements.
No build or other inference process overlaps the accepted timings.

The near query is outside the sampler's cache but inside already-computed TD
coarse windows. A separate `scripts/verify-coarse-cold.py` matrix repeats three
alternating fresh-process pairs at x=z=65536, requiring **positive newly computed
window counts in both arms**. This distinguishes a cold adapter hit on warm
coarse tensors from genuine cold coarse inference. These additional fixtures time
only queries, then save/stop; the eight near fixtures independently exercise
production terrain save/reopen. The same native/model startup cost precedes both
far arms and is excluded from the sampler timings.

The pinned runtime is Minecraft 1.21.1 / NeoForge 21.1.251 / official TD 2.3.0
CPU (`3212b53c…4092fe8`), Java 21.0.6, six available JVM processors, 2/6 GiB
heap, seed -1550453200536840819, tile 256, model/config aggregate
`64fe6b1a…39601d9`, Windows 11/amd64. The original properties' device request is
ignored by the official CPU distribution; the resolved CPU backend is required,
rather than inferred from that requested option.

Every arm then generates a sample chunk, saves/stops and reopens in a fresh JVM.
Complete sampled blocks, exact snapshot bytes and all persisted Overworld records'
coverage/status/section block containers must match. Raw region-file metadata is
not used as terrain identity. Shared TD/models are immutable hardlinks; the addon
and probe are copies. The template is never launched. Full template/model manifests
must remain unchanged. Disk/startup/RCON/shutdown bounds reuse the accepted runner;
only each stopped new case's ONNX cache is removed.

## Explicit version rejection and restoration

Before any possible output-changing adoption, the codec's experimental identity
is rejected by the production compatibility boundary, including self-validation
of an unsupported generator. Domain tests retain geology-1's original fingerprint.

The independent runtime boundary test creates an explicitly test-derived alternate
addon by replacing only UTF8 `geology-1` constants in class files with
`coarse-evidence-1`. It does not implement or certify an alternate geological
algorithm. A NEW copy of this run's verified saved terrain retains its original
snapshot. Loading the alternate artifact must initialize TD and reach the intended
geology guard, parse all seven saved/runtime context fields, differ only in
generator, exit before Ready/RCON, and preserve snapshot and decoded terrain.
Restoring the exact original addon bytes must reopen with the original complete
sample blocks and unchanged snapshot/terrain. No snapshot is edited to manufacture
the mismatch, no migration occurs, and the alternate artifact is never released.

## Evidence and decision

[Portable evidence](evidence/coarse-prototype-2026-11-02.json) validates all raw
logs and both matrices. The accepted production addon hash is
`c5775ecafaefaaebb192d81152ab128d291d98e824fd4794e4b8d61f20850fa2`;
the separate probe is
`3b927892a54e958ed16a3ec048659c227e78869d970df62cd3efde4fb5142155`.

### Adapter-cold, startup-warm coarse tensors

| Scale / pair | Current query | Coarse evidence | Current / coarse new windows |
| --- | --- | --- | --- |
| 1 / 0 | 14.624496 s | 1.0876 ms | 61 / 0 |
| 1 / 1 (coarse first) | 12.857821 s | 1.0336 ms | 61 / 0 |
| 1 / 2 | 11.778089 s | 1.0350 ms | 61 / 0 |
| 6 / 0 | 10.466817 s | 1.1689 ms | 56 / 0 |

Each current scale-1 query enters the public elevation API once; scale 6 enters
the original heightmap API once. Each coarse query enters the supported coarse
API once. There is no inference-request elimination, but the requested stage/work
changes. The median scale-1 paired query saving is 12.856787 s in this specific
startup-warm neighborhood. Zero newly computed coarse windows is explicitly not
a measurement of cold coarse neural inference.

### Genuine cold TD windows at x=z=65536

| Pair / arm order | Current | Coarse | Paired saving | Current / coarse windows |
| --- | --- | --- | --- | --- |
| 0 / current, coarse | 16.561562 s | 1.240475 s | 15.321087 s | 65 / 2 |
| 1 / coarse, current | 15.987784 s | 0.811669 s | 15.176116 s | 65 / 2 |
| 2 / current, coarse | 15.771733 s | 0.816099 s | 14.955634 s | 65 / 2 |

Every arm has positive newly computed windows; every query still issues exactly
one actual public request (elevation versus coarse). Median paired saving is
**15.176116 s** for this isolated query and broader evidence footprint. Cached
current-region median costs across these fixtures are 0.0402–0.0566 ms, coarse
0.0337–0.0358 ms, with zero accessor entries/new windows in all five cache hits
per arm. Near-fixture warm medians are 0.0392–0.0602 ms current and
0.0284–0.0328 ms coarse. These are cached sampler reads, not warm fresh-chunk
generation or end-to-end route timings.

The numerical signals are different: the near province's current tile mean/range
is 2944.76 / 1661 m, versus coarse-neighborhood 2870.843 / 2103.846 m. The far
province's current values are 96.36 / 931 m, versus coarse -104.775 / 1691.532 m.
Different spatial support, statistics and classification implications prevent an
equivalence claim. No p5-derived relief or tectonic inference is adopted.

At both scales, the independent Explorer oracle passes all 36 decoded channel
values and six raw cell placements. Four simultaneous callers issue one coarse
request; reversed boundary traversal agrees; 129 real entries retain exactly
128, and an evicted cell makes one new request. Each of the eight production
terrain fixtures preserves complete sampled blocks, exact snapshot bytes and all
529 persisted records through fresh-process reopen. The generator-only alternate
changes just two class-file constants, differs only in the seven-field context's
generator, and rejects before Ready/RCON. Exact original-addon restoration
preserves the same 529 records, snapshot and sample. All 24 JVM launches exit 0;
shared input/template manifests remain unchanged.

**Decision: retain the opt-in prototype and codec; do not replace production
sampling or adopt new classification outputs.** Evidence supports bounded,
deterministic and substantially cheaper coarse evidence on this pinned CPU setup.
It does not support using the original fine-tile classifier thresholds on a new
3x3 coarse-neighborhood range. Any future output-changing generator must have a
distinct immutable identity, an explicit new-world selection policy, meaningful
terrain-informed classification validation and its own continuing-save boundary
matrix. No automatic migration is introduced here.

Historical PR #46 measurements (including the
14.157-second median remaining route overhead) and the original 14.383-second
performance scope remain separate; isolated-query timings cannot be subtracted
from either route result.

Raw fixtures/logs are retained under ignored `runs/acceptance/` and are not
uploaded. The portable exporter validates every raw-log hash, executed runner
source hashes, complete sampled-block equality, cache-hit work counts and the
generator rejection/restoration observations.

## Verification, provenance and remaining gates

JDK 21 build/domain/settings/coarse/probe checks pass. The unchanged original
province/classification fingerprint remains enforced. Resource checks (64 blocks,
158 recipes, 711 JSON), research catalog checks, Python syntax and portable
raw-log/source/artifact validation pass. Final OS checks find no Java/Python test
process or game/RCON listener; 5.73 GiB free remains. Only stopped new-case ONNX
caches were removed. The exporter also proves all 31 existing production classes equal the
retained PR #46 JAR and verifies that the test alternate changes only the two
generator constants. Existing host/ore/carver and strict #5 evidence is reused;
it is not represented as newly executed broad acceptance. No classification,
surface mixin or natural-host predicate changes.

Retained raw outputs:

- `runs/acceptance/coarse-prototype-2026-11-02-01`: sandbox denied the first
  immutable hardlink before launch; contributes no runtime acceptance.
- `runs/acceptance/coarse-prototype-2026-11-02-02`: eight near arms and their
  independent reopens, plus generator-only rejection and exact restoration.
- `runs/acceptance/coarse-cold-2026-11-02-01`: six independent far cold arms.

Reproduce with NEW outputs and the pinned CPU artifact/Java 21:

```powershell
python scripts/verify-coarse-prototype.py --java <java21> --td <cpu-jar> --output <new-near-output>
python scripts/verify-coarse-cold.py --java <java21> --td <cpu-jar> --output <new-cold-output>
python scripts/summarize-coarse-prototype.py <near-output> --cold <cold-output> --baseline <retained-pr46-jar> --output <portable-json>
```

The generator test is an identity-only boundary test, not a migrated or accepted
new algorithm. Unvalidated p5 statistics/training provenance, terrain-informed
classifier/contact design, far cold scale-6 repetitions, multiple seeds/hardware/
backends/models, in-flight edits and broader integrated lifecycle/concurrency
remain outside this focused slice. #11 and #9 remain open. No historical stronger
assertion is weakened, no shared inputs/user save is modified, and unrelated
`temp/` is preserved.
