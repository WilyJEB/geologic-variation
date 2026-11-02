# Exact native-scale anchor sampling (#11)

This focused slice tests whether geology-1 can avoid unused TD work without
changing its geological outputs. It does not implement the larger terrane design
in #11. The retained 14.383-second overhead remains historical evidence;
fresh paired results below must be used to assess this change.

## Reconciliation and candidate

Work began from local/origin main `7c3e965368025954cd82f8a125f7b33496dd9521`
with only unrelated untracked `temp/`. No ancestor/repository AGENTS.md was
present. `docs/workflow.md`, runtime acceptance tools, the reproducibility
contract, world-upgrade rules and the live generation guards were inspected.
GitHub #11 remains a broader terrain-informed-geology issue; #9 remains open.
#5 is closed for the selected regional-identity/save-continuity contract, while
its stronger strict scale-6 post-feature assertion remains failed and unchanged.

Pinned TD source `8acd2b680ee248334637f8cf13f6c78ac20003da` exposes
`getPipelineData(z0,x0,z1,x1,false)`. It serializes onto TD's inference executor
and blocks the caller. Its native-scale elevation is the same unpadded
`pipeline.get(...)[0]` used in `handle1x`; the latter also requests padded
elevation and climate for biome classification. Geology samples only elevation.
The candidate requests the identical whole rectangle, reads the identical 5x5
positions and duplicates TD's floor/clamp/short conversion. It changes neither
the province partition nor classification. Scales 2–6 retain `fetchHeightmap`:
their interpolation, Sobel gradient and elevation noise are part of geology-1.
Sparse/coarse replacement, altered rectangle boundaries and new geology rules
are excluded from this change.

The generator remains geology-1 because this is an equivalent elevation path.
Saved generator/dependency/model/backend/seed/scale/tile compatibility checks
remain strict. Context is checked before cache hits and again after inference.
Cold queries on the pinned `terrain-diffusion-inference` thread reject before
either blocking accessor. No callback schedules blocking work on that executor.
No continuing-save snapshot rewrite or migration is introduced. A future sampler
that changes outputs requires a new generator identity and an explicitly reviewed
rejection/restoration or migration contract before adoption.

## Measurement protocol

`scripts/verify-anchor-performance.py baseline` measures three fresh-process
TD-only/old-addon pairs with alternating arm order. `candidate` independently
measures three TD-only/old/new triplets, reversing arm order each trial. This
provides paired old/new savings and paired new/TD remaining overhead. All use the pinned official TD
CPU JAR (`3212b53c…4092fe8`), model/config aggregate `64fe6b1a…39601d9`,
Minecraft 1.21.1, NeoForge 21.1.251, Java 21.0.6, scale 1, tile 256,
seed -1550453200536840819, 2/6 GiB heap and six JVM processors. The separate
probe is present in every arm. Coarse preparation precedes timing in both arms.
OS filesystem caches are not flushed. No other inference runs concurrently.

Each sequential chunk operation is timed separately from block hashing/RCON.
Their sum is route time. Every operation has before/after counters for actual
heightmap entries, addon heightmap entries, public data calls and newly computed
TD tensor windows. TD's actual uncached rectangle logs distinguish cache misses
from duplicate callers; these are counts, not summed overlapping wait durations.
The passive window getter only reads TD's counter and never schedules inference.
Cold single-region, cold four-caller same-region, cached region and loaded-chunk
read costs are separate. Loaded reads are not warm chunk generation.

Every addon case saves/stops, reopens in a fresh JVM, checks complete sampled
blocks and region records, saves/stops again, and compares snapshot bytes plus
all persisted Overworld block containers, statuses and coverage. Region-file
metadata is distinct from terrain identity. New metadata-only fixtures never
launch or edit the source template. Input models/TD are immutable hardlinks;
addon/probe JARs are copies. Before each launch/reopen at least 2 GiB free is
required. Processes use existing bounded startup/RCON/stop limits and forced
cleanup on failure. Only the stopped new case's regenerable ONNX cache is removed.
Offline Dev identity, loopback endpoints, credentials, user profiles, optional
Ulti-World and unrelated temp material remain untouched.

Raw results/worlds/logs stay in ignored `runs/acceptance/`. Portable exports
exclude addon origins and credentials, validate raw log hashes, and retain every
chunk hash/count rather than replacing the stronger failed #5 assertion.

## Results and acceptance

[Portable evidence](evidence/anchor-performance-2026-11-02.json) validates raw-log
hashes and retains every timing, counter, complete block hash and decoded saved
comparison. The old addon is the current main build, SHA-256
`fc52ac33d226719f51a2d23dd7778e94b18a28011942e7e9719375401d07513e`;
the candidate is
`6f1a143a8b117abdabdfd1c72270d5270c19e18f7920a7df3aab908d3f6ec1ae`.
Per-case probe hashes are retained: a later probe build adds only the isolated
sampler command after all cold timings finish. No compilation overlaps accepted
cold measurements.

### Refreshed CPU baseline

| Clean pair | TD-only route | Old addon route | Added time |
| --- | --- | --- | --- |
| 1 | 33.272 s | 55.150 s | 21.878 s |
| 2 | 33.519 s | 49.745 s | 16.226 s |
| 3 | 34.196 s | 49.235 s | 15.039 s |

Median paired overhead is **16.226 seconds**, rather than assuming the historical
14.383 seconds is invariant. Each pair records six versus eight actual uncached
heightmap rectangles and 116 versus 178 new tensor windows. The extra anchor
rectangles remain x=-1024/z=-1536 and x=512/z=-1024.

### Candidate: modest CPU saving, inconclusive cold-route speedup

| Trial | TD-only | Old addon | Candidate | Old minus candidate | Candidate minus TD |
| --- | --- | --- | --- | --- | --- |
| 0 | 33.513 s | 48.866 s | 48.341 s | +0.525 s | 14.828 s |
| 1 | 36.060 s | 49.009 s | 50.012 s | -1.003 s | 13.953 s |
| 2 | 34.327 s | 49.508 s | 48.484 s | +1.024 s | 14.157 s |

Observed median paired saving is **0.525 seconds**, with opposite signs and a
-1.003 to +1.024-second range. Three trials do not establish a reliable cold-route
improvement. Directly paired remaining overhead has a **14.157-second median**;
it is not obtained by subtracting medians of independent experiments.

Both addon versions still compute **178 windows**, 62 more than TD-only. The
candidate replaces two anchor heightmap calls with two public elevation calls;
its six ordinary uncached heightmap rectangles plus two elevation requests are
still eight requests. A smaller heightmap-log count is not eliminated inference.
It avoids padded decoding, climate/biome work and unused full heightmap/biome
outputs; it does not remove the remote fine-elevation window work.

An independent same-JVM diagnostic alternates both exact accessors for 20 pairs
per anchor after three warmup pairs, clearing the provider heightmap cache before
each arm while retaining warm tensor windows. All 40 pairs have equal sampled
values and **zero new windows**:

| Anchor x/z | Old median | Candidate median | Median paired saving |
| --- | --- | --- | --- |
| -1024/-1536 | 16.26 ms | 4.47 ms | 11.79 ms |
| 512/-1024 | 16.36 ms | 4.37 ms | 11.89 ms |

This supports the narrow work-removal optimization, approximately 12 ms per
uncached anchor with already-warm tensors on this CPU. It does not explain or
establish the noisy 0.525-second cold-route median, and the component medians are
not added to overlapping caller waits. No elimination of all 14.383 seconds is
promised.

Cold remote single-region queries are 12.467–14.199 s old and 12.253–12.541 s
candidate; four simultaneous same-region queries are 12.336–12.882 s old and
12.462–12.683 s candidate. These small separate trials do not establish a general
cold/concurrent speedup. Candidate cached-region queries are 0.042–0.100 ms;
candidate loaded-chunk reads are 0.043–0.053 ms. These reads are not warm fresh-chunk
generation. The public data API submits four calls in the concurrent test where
TD's heightmap API deduplicates pending callers; the neural windows are shared,
but repeated decode work remains. Cache-pressure and existing-provider-cache
reuse workloads are not certified by this slice.

### Output and storage checks

All 131,072 elevations in both measured anchor tiles exactly match TD's original
floor/clamp/short output. Across all three old/new pairs, actual contact regions,
cold remote regions, concurrent region identities and positioned regional hashes
match. Every sampled chunk contains regional rock. All six addon cases preserve
their own complete sampled blocks, region records, exact snapshot bytes and all
862 persisted records' block containers/statuses/coverage through save/stop/fresh-JVM reopen.
Separate region-file metadata hashes are retained where captured.

Complete old/new post-feature hashes differ in all four chunks of each pair.
Decoded saved differences total 545/563/886 blocks, with **zero regional-block
changes or palette conflicts** and zero bedrock/deepslate/fluid changes. Soil
differences are 8/8/11 positions. This is not a passing bitwise final-world
comparison or attribution of every feature difference. The original stronger
#5 assertion and its failed evidence remain unchanged.

The independent [live guard evidence](evidence/anchor-guards-2026-11-02.json)
passes all four seed/scale × cached/uncached cases in NEW copies of the old
addon's verified saved world (`anchor-baseline-2026-11-02-03/t3-old/world`).
Each parses all seven context fields, requires exactly seed or scale to differ,
rejects before either heightmap **or public elevation** entry, clears the cache,
and restores/reopens with matching settings/context, actual region and complete
sample blocks. Snapshot bytes and all **862** persisted records' exact coverage,
status and block containers survive rejection and restored reopen. Region-file
metadata hashes remain separate. Original fixture and shared-model manifests
remain unchanged; all eight JVM launches exit code 0. The historical runner's
original addon pin stays the default; this run explicitly supplies the candidate
SHA and requires the new elevation-entry instrumentation.

Build/domain/settings/probe, generated resources (64 blocks/158 recipes/711 JSON),
catalog, Python syntax, portable exports and raw-log hash verification pass.
Final OS checks find no Java/Python test process or game/RCON listener; 6.40 GiB
free remains. Only new stopped-case ONNX caches were removed; raw evidence is retained.
The acceptance decision is to retain the equivalent native-scale work reduction,
with **no reliable cold-route speedup established**. Scales 2–6 follow the original
sampler by inspection; their prior coverage is reused, not a new candidate pass.
New hardware/backend/model sets, >512 real-province pressure, provider-cache reuse,
in-flight edits and broader integrated/concurrency lifecycle cases remain outside
this focused CPU slice. #9 remains open; no prior stronger assertion is relaxed.

### Raw provenance and reproduction

- `runs/acceptance/anchor-baseline-2026-11-02-01`: sandbox-denied immutable
  hardlink before launch; no runtime acceptance.
- `anchor-baseline-2026-11-02-02`: trial 0 is excluded because the first five
  timed seconds overlapped candidate compilation (server log 12:48:31; Gradle
  daemon exited 12:48:36). Accepted clean trials 1/2 use opposite arm order.
- `anchor-baseline-2026-11-02-03`: clean replacement trial 3, old then TD-only.
- `anchor-candidate-2026-11-02-01`: all nine TD/old/new arms, reversing order
  each trial; six additional addon reopen launches.
- `anchor-sampler-2026-11-02-01`: separate 40-pair warm-tensor comparison.
- `anchor-guards-2026-11-02-01`: four live mismatch/restoration cases, eight
  launches, preserving the independently copied old-addon terrain.
- `performance-inputs-2026-11-02`: retained main addon and actual CPU provider
  bytecode inspection. Shared immutable inputs and the source template are
  hash-checked unchanged; no retained logs/worlds/weights are committed.

For a fresh reproduction, retain a build of main at the stated baseline SHA as
`--baseline`, build this candidate/probe, then use NEW outputs:

```powershell
python scripts/verify-anchor-performance.py baseline --java <java21> --td <pinned-cpu-jar> --baseline <main-jar> --output <new-baseline>
python scripts/verify-anchor-performance.py candidate --java <java21> --td <pinned-cpu-jar> --baseline <main-jar> --candidate <candidate-jar> --output <new-candidate>
python scripts/verify-anchor-performance.py candidate --sampler-only --java <java21> --td <pinned-cpu-jar> --baseline <main-jar> --candidate <candidate-jar> --output <new-sampler>
python scripts/summarize-anchor-performance.py --baseline <new-baseline> --candidate <new-candidate> --sampler <new-sampler> --output <portable-json>
python scripts/verify-live-context.py --java <java21> --td <pinned-cpu-jar> --fixture <verified-old-world> --addon <candidate-jar> --expected-addon-sha256 6f1a143a8b117abdabdfd1c72270d5270c19e18f7920a7df3aab908d3f6ec1ae --output <new-guards>
python scripts/summarize-live-context.py <new-guards> --expected-addon-sha256 6f1a143a8b117abdabdfd1c72270d5270c19e18f7920a7df3aab908d3f6ec1ae --output <portable-guards-json>
```

This run's export additionally supplies both retained baseline directories and
`--exclude-first-baseline-trial 0` to retain three clean pairs. This exclusion
is explicit, not an automatic removal of an unfavorable measurement. Counter
brackets encompass the complete command including fingerprinting; reported
chunk-generation time excludes fingerprinting. Counter totals are not CPU time.

## Boundary for a future output-changing sampler (not adopted)

The remaining remote fine-elevation inference cannot be assumed replaceable by
coarse climate/landform values while preserving current means, relief and rock
selection. A future coarse sampler must use a distinct generator identity such
as geology-2, with immutable sampling/seed/catalog rules and the existing exact
dependency/model/backend/seed/scale/tile context. The safe initial rollout would
be an explicit new-world-only build: uninitialized worlds write its new identity;
geology-1 continuing worlds reject before new generation, with exactly generator
reported as different when all other inputs match. No snapshot is rewritten,
deleted or adopted, and no existing terrain is converted.

Recovery means stopping, retaining the rejected copy/log, restoring its exact
geology-1 addon and original context, then reopening a copy and verifying the
snapshot, region identity, complete blocks and persisted status/coverage before
exploring neighbors. Required acceptance includes generator-only startup
rejection, cached/uncached live-query behavior, dedicated/integrated lifecycle
recovery, immutable source inputs and neighboring geology after restoration.
Any migration or dual-generator dispatch requires a separate reviewed design;
the existing strict guard is not a migration mechanism. This proposed boundary
is documented before any such algorithm adoption, not claimed as implemented or
runtime-accepted here. #9's trained-weight, upgrade and remaining lifecycle gates
stay open, and #11's broader terrain-informed terranes remain future work.
