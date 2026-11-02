# Live seed/scale query safety, 2026-11-01

This #9 slice tests independent live seed and scale changes before populated-cache
and empty-cache geology queries on the pinned standalone CPU dedicated runtime.
Production generation, geology-1, IDs, provenance guards and the addon JAR remain
unchanged. #5's original strict post-feature determinism failure remains open;
the 14.383-second cold-route opportunity remains #11. Ulti-World stays optional.

## Accepted results

All four independent cases pass on MC 1.21.1 / NeoForge 21.1.251 / official
TD 2.3.0 CPU / Java 21.0.6 / Windows 11 amd64, source baseline `a69ed0d`.
Eight JVM launches cover four live rejections and four exact-input reopenings.
Each rejection reports only its intended seed or scale mismatch, includes
restoration guidance, exits through the normal server shutdown path, clears the
geology cache and makes zero heightmap calls after editing. Snapshot bytes and
all stored Overworld chunk block containers/statuses/coverage are unchanged.
This includes 529 persisted records per case (one full sample and 528 surrounding
generation-stage records), with no new records after rejection.
Every reopened case returns matching settings/context, geology and complete
existing sample blocks, then saves and exits normally. No production fix was
needed. Build/domain suites, resource checks (64 blocks / 158 recipes / 711 JSON
resources), catalog checks, Python syntax and portable log-hash validation pass.
All eight test JVMs exit; no Java/Python test processes remain. Free disk space
returns to about 5.3 GB after safe stopped-case cache cleanup.

## Mechanism and scope

The pinned TD artifact exposes `LocalTerrainProvider.changeSeedFromExplorer(long)`
(the exact public API called by ExplorerServer's `/api/seed` handler), and
`WorldScaleManager.setCurrentScale(ServerLevel, int)`. Source inspection and
`javap` against the actual CPU JAR verify these APIs. The seed API serializes its
own mutation on TD's inference executor; the probe invokes it from the server
thread, then queries geology on that server thread. No probe inference is run
inside TD's inference thread. The scale API dirties the world's scale state;
restoration uses only this disposable fixture's previously captured scale bytes.
The seed API is transient and reopen initializes it from unchanged level.dat.

Four NEW directories/processes isolate the first-failure latch: seed/cached,
seed/uncached, scale/cached, scale/uncached. Each establishes matching context,
loads/generates existing regional terrain at chunk (-32,-65), queries
(-508,-1027), freezes ordinary ticks, disables random ticks/spawning and saves.
Each case copies PR #36's known-provenance saved-terrain baseline into a new
directory; that source fixture is never launched or modified.
The test command clears the geology cache, queries the real province and requires
exactly one entry. The cached arm retains it; the uncached arm explicitly clears
it. Both arms then change one live input and immediately query the same point.
This is a populated-cache query attempt, including seed/scale cache-key changes;
it does not claim the old key would match after such a change.

A test-only counter at every `fetchHeightmap` entry measures calls even if cached
or faster than the existing 1 ms logging threshold. Zero calls after the edit
proves rejection precedes this query's terrain/inference route. No Minecraft
chunk generation is requested after the edit. Persisted chunk coverage and block
containers are separately compared, so no new incompatible chunk may appear.
This does not exercise an intentionally concurrent edit during in-flight inference.

## Evidence and reproduction

Portable observations and artifact/log hashes are in
[the evidence JSON](evidence/live-context-2026-11-01.json). Raw saves, logs and
crash reports remain ignored under `runs/acceptance/live-context-2026-11-01-04`.
Use the [pinned runtime preparation](runtime-acceptance-tools.md), then:

```powershell
gradlew.bat build runtimeProbeJar
python scripts/verify-live-context.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --fixture 'runs/acceptance/context-startup-2026-11-01-02/baseline/world' `
  --output runs/acceptance/new-live-context
python scripts/summarize-live-context.py runs/acceptance/new-live-context `
  --output docs/evidence/live-context-2026-11-01.json
```

The runner refuses existing output, checks at least 2 GiB free per case, pins TD,
addon and observed model/backend identity, uses bounded startup/command/exit
waits and removes only resolved in-case ONNX optimization caches after shutdown.
These caches cost about 1.1 GB per launch. Immutable models/TD are linked; never
edit them. No user save, installed profile or unrelated temp/ material is changed.

Before/after `.mca` hashes are retained but are not the block-state assertion:
live region metadata can change after save/flush. Every persisted terrain chunk's
status and section block-state container is hashed without light/ticks/timestamps;
identical containers imply identical stored blocks. The exact persisted chunk
set must also match. Reopening additionally compares the complete sample block
hash, settings/context and geology region. This avoids calling normal region
metadata or simulation changes geology corruption.

Harness development runs are excluded from accepted evidence. Run -02 rejected
the populated-cache seed query without heightmap calls, then failed an overly
strict region-byte assertion. Run -03 passed decoded rejection preservation but
its newly generated fixture's sample differed after reopen. The accepted suite
uses the already saved PR #36 terrain to isolate that settling/reopen uncertainty;
the earlier mismatch is retained locally and is not claimed as a passing test or
attributed to geology without evidence.

Earlier #27 live-explorer failure, client error-screen recovery and dedicated
shutdown evidence is reused only as background; these four query-route tests are
new. Integrated-client presentation/same-process recovery is not rerun here.
#9 remains open for artifact/model/backend changes, generator upgrades, hot
config reload and remaining client/lifecycle cases. #18 retains broader backend
and hardware acceptance. New-world UI and unknown legacy migration are excluded.
