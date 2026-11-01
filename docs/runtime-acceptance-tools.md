# Disposable production-runtime acceptance tools

These opt-in tools test the pinned Minecraft 1.21.1 / NeoForge 21.1.251 runtime.
They do not run as part of normal gameplay or change geology rules. CI compiles
the probe; it does not run inference or claim runtime acceptance.

## Preparation

1. Build with JDK 21: `gradlew.bat build runtimeProbeJar`.
2. Install the official NeoForge 21.1.251 server into an ignored directory such
   as `runs/acceptance/runtime`, using its official installer and `--installServer`.
3. Supply the exact official CPU TD artifact and its already verified model
   files. The current Windows build baseline remains unchanged. Do not substitute
   a backend into an existing test world without a new, explicit fixture.
4. Supply a disposable, provenance-verified TD save as `--template`. The default
   is the local `runs/server/world` test save. No user installation is required.

Example PowerShell invocation (replace the two machine-specific executable/JAR
paths):

```powershell
python scripts/runtime-acceptance.py reproducibility `
  --java 'C:/path/to/jdk-21/bin/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --output runs/acceptance/repro-new
```

Use a fresh output directory for each run. The harness refuses to overwrite a
case directory. It copies only level metadata to create each matrix fixture;
chunk files are not copied between scales. It explicitly prepares matching TD
scale data and geology context for those synthetic fixtures. This is controlled
test setup, not a supported continuing-world migration or new-world-creation test.
The original template is never launched or modified. Model files are hardlinked
read-only inputs on the same volume; do not edit shared assets during a run.

The server binds to loopback game port 25587 and RCON 25588, uses an ephemeral
RCON password, offline Dev identity, 2-6 GiB heap, and disables the tick watchdog
for cold CPU inference. Run one case at a time. The harness freezes normal ticks,
disables random ticks/mob spawning, and explicitly generates full chunks through
the probe. Each command has a five-minute transport timeout; it is not a benchmark
threshold. Worlds, credentials, full paths, logs and model files stay under the
ignored output folder. Stop the harness normally so saves and process cleanup run.

## Probe and measurements

`runtimeProbeJar` writes a separate `build/runtime-probe/` artifact. Never install
it in a normal world or distribute it as part of the addon. Its permission-level-4
commands are:

- `acceptance chunk <overworld|the_nether|the_end> <chunkX> <chunkZ>` generates or
  loads a full chunk, measures that operation, then separately fingerprints its
  complete block states and positioned regional blocks. Hashing is excluded from
  the reported generation time; it can still affect later JVM warmup.
- `acceptance region <blockX> <blockZ>` reports the actual addon region, query wall
  time, observed cache size and loaded addon origin, using reflection so the probe
  also loads in the TD-only arm.
- `acceptance concurrent <blockX> <blockZ>` issues four simultaneous region queries
  and requires identical results. It reports total elapsed time and cache size.
- `acceptance prepare` waits for models and requests the same public coarse sample
  used to resolve the addon's provider at startup. Both performance arms run it
  before timed chunks so this preparation is excluded consistently.
- `acceptance cache-policy` temporarily exercises the actual addon cache with 600
  synthetic keys and a previously observed region value, verifies the 512-entry
  cap and LRU retention of a touched key, then clears all synthetic entries in a
  finally block. Use only on an idle, frozen disposable server. This verifies
  eviction policy without claiming 600 real terrain inferences or cache-pressure
  performance measurements.

The probe's test-only TD mixin labels blocking heightmap calls `addon-anchor` when
the addon query is present in the call stack, otherwise `td-or-other`. It logs
requests taking at least 1 ms. Durations include queue/cache wait, instrumentation
and possible contention; they are not CPU time. Concurrent waits overlap and
must not be summed. TD's own uncached-request/window counters are needed to
distinguish extra inference from duplicate callers waiting on one shared request.

## Modes and acceptance limits

`reproducibility` uses scales 1 and 6, negative-coordinate province boundaries,
chunk edges, and a known land sample. Each pair uses opposite chunk traversal
orders. It requires nonempty regional blocks, matching positioned block hashes,
identical actual region results, stable snapshot bytes through a full process
restart, and matching newly generated neighboring chunks. Whole-terrain hashes
are also recorded, but block ticks, unrelated features and structures must be
considered before attributing a difference to geology.

`gating` compares TD-only versus addon in an ordinary vanilla Overworld, Nether
and End. It requires identical sampled complete block hashes, no regional blocks
and no geology snapshot. This is sampled runtime evidence, not every dimension,
biome or feature combination.

`order-control` runs the scale-6 opposite-order/restart sequence with TD alone.
It records full chunks for a comparison with the addon matrix when later features
change host blocks. Use `scripts/compare-runtime-chunks.py` to decode final saves
and distinguish regional palette conflicts from host-versus-ore differences.
The strict reproducibility assertion is intentionally not weakened by this control.
`scripts/summarize-runtime-acceptance.py` exports portable measurements, artifact
and log hashes while removing machine-specific addon origins. Review the exported
file before committing it; never commit the server properties, worlds or raw logs.

`performance` runs three fresh-process TD-only/addon pairs in alternating arm
order. Seed, scale, tiles, input models, JVM settings and target chunks match;
both arms run identical coarse preparation. It records cold chunk generation,
warm loaded-chunk access, cold concurrent remote-anchor queries and warm region
queries. Fresh process means empty application inference caches, not a flushed
OS filesystem cache or a fully cold machine. Keep other workloads idle. Report
per-trial results and ranges; do not infer an addon regression from combined-runtime
lag or simply subtract overlapping request durations. The synthetic cache-policy
check exercises eviction, but throughput under 512-plus real remote-province
queries remains outside this small CPU comparison.

`smoke` launches without the probe, using a copied disposable save and the actual
addon JAR under `mods/`. It waits for interactive client acceptance, then saves
and stops when a `STOP` file is created in its case directory. `scripts/launch-acceptance-client.py` can launch an isolated
matching production client from an existing launcher manifest with pinned library
hash checks. It reads existing libraries/assets but neither reads account credentials
nor changes that launcher profile. It uses the offline Dev identity and joins
only the loopback test endpoint. Supply `--manifest`, `--meta`, `--java`, `--addon`,
`--td` and a new `--output` directory. This distinguishes real packaged client/server
loading from ModDevGradle development classpaths.
