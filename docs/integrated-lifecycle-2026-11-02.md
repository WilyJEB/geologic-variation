# Integrated client rejection and recovery, 2026-11-02

Independent packaged CPU client evidence for #9: compatible control, actual
world-seed mismatch rejection, another compatible load in the same JVM, then
exact original-input restoration and reopening of the rejected world.

**Accepted after the reproduced cleanup fix.** See
[the portable summary](evidence/integrated-lifecycle-2026-11-02.json) and
[the inspected recovery-screen capture](evidence/integrated-lifecycle-recovery-2026-11-02.png).
Raw saves/logs/crash report/executed sources/results remain under ignored
`runs/acceptance/integrated-2026-11-02-08`. The preceding post-fix run -07 also
passed; -08 adds explicit frozen-state/input-manifest assertions and LF-pinned
tool sources. The pre-fix result remains separately labeled failed for cleanup.

Final client PID 8204 uses four distinct integrated-server instances and exits
0. The fixed addon is SHA-256
`fc52ac33d226719f51a2d23dd7778e94b18a28011942e7e9719375401d07513e`;
the probe is `bd67c736caf4dd37bb6d5f740ed89a56c87e4c0cc0442b1d230da8f0207bada3`.
MC 1.21.1 / NeoForge 21.1.251 / official TD 2.3.0 CPU / isolated Java 21.0.6
remain pinned. Complete installed/isolated JDK manifests recheck against #44's
retained manifests. Launch reserve is 3,261,906,944 bytes; final free space is
3,186,413,568 bytes. Final OS inspection finds no Java/Python test process or
listener on explorer/game/RCON ports 19801/25587/25588.

All 529 records retain exact coverage/status/block containers: 1 full,
8 initialize-light, 16 carvers, 24 biomes and 480 structure-starts. Both copies'
continuing terrain and snapshots match; all nine region files are byte-identical
through rejection. Complete input manifests and exact original/restored seed-file
hashes match. Active settings/context and ownership, actual geology and complete
sample blocks match all three successful loads. Build/domain/probe, 64 blocks /
158 recipes / 711 resource JSON, geology catalog, Python syntax, diff checks,
raw-log/source hash export and visual recovery-screen inspection pass.

## Reconciliation and regression

Fetched origin; local main matched merged PR #44 at
`32ab500e99387239128b16f60d7ab9138810e734`. #9 remains open; #5 is closed for
its selected supported contract, with its original stronger assertion still
failed. #11's unchanged 14.383-second overhead remains separate. No repository
or ancestor AGENTS.md was found. Read failure handling, verification, runtime
tools, backend report/linked evidence and the packaged launcher/probe before
implementation. PR #44's dedicated CPU → real DirectML rejection → CPU reopen
is reused historical coverage, not a new integrated GPU test. CUDA dependencies
remain absent; no drivers, system PATH or toolkits were changed.

The existing client launcher only supported multiplayer quick-play. Its new
explicit `--integrated --probe` mode uses the installed manifest's pinned
libraries/assets with the same offline Dev UUID and token `0`. It never reads
account files or changes installed profiles. A property-gated, client-only
probe bridge loads through `WorldOpenFlows.openWorld`, observes actual screen
narration and joined client state, and executes acceptance queries on the
integrated server thread. It does not replace production failure handling.
Normal disconnect follows PauseScreen's level-disconnect/client-disconnect
sequence. No blocking TD accessor runs on TD's inference thread.

The pre-fix run `runs/acceptance/integrated-2026-11-02-06` completed all four loads
with the original production addon, but **failed explorer executor cleanup**.
After a real `/api/status` request, the listener and non-daemon HTTP dispatcher
closed on rejection, while daemon worker `terrain-explorer-http` remained alive
after the next compatible world joined. Exact pinned-JAR bytecode confirms
`ExplorerServer.stop()` calls `HttpServer.stop(0)` and drops the server reference
without shutting down its per-instance executor. Eventual worker disappearance
does not satisfy cleanup before the next load. The
[pre-fix evidence](evidence/integrated-lifecycle-regression-2026-11-02.json)
retains this failed result separately.

The sole production change redirects that existing HTTP stop call: capture its
executor, stop the HTTP server, and call `shutdownNow()` in `finally` when it is
an ExecutorService. This applies to normal and exceptional explorer stops and
does not wait for native inference or terminate TD's process-wide inference
executor. Strict guards, schema 2, geology-1, generation, IDs and optional
Ulti-World remain unchanged. The probe remains a separate, opt-in test artifact.

## Matrix and preservation contract

Both saves are NEW ordinary copies of PR #36's verified baseline, never writable
hardlinks. Model assets and the CPU distribution are immutable links; addon and
probe are copied. No linked input is edited. The copied metadata places a
non-generating spectator at the existing sample and disables spectator chunk
generation; random ticks/spawning are disabled, spawn radius is zero, and the
server is frozen before its first tick. The first control must independently
preserve the source's stored terrain before its frozen saved bytes become the
rejection/restoration input. This metadata setup is confined to test copies.

Only `WorldGenSettings.seed` in the rejected copy's `level.dat` changes, from
`-1550453200536840819` to `-1550453200536840818`. TD actually initializes that
alternate seed before geology rejects; all seven parsed context fields must
differ only in seed. Its geology snapshot is never modified. A real explorer
listener/request is active before rejection, so cleanup is exercised rather
than inferred from an unopened explorer.

| Load in one JVM | Required result |
| --- | --- |
| Compatible control | Client joined; active settings/context, actual geology and complete sample recorded |
| Seed mismatch | Before joining or addon-anchor generation; production recovery screen; server thread finished |
| Compatible world | Joins while rejected copy is still incompatible; fresh owner, no stale failure/settings/cache |
| Original seed bytes restored | Rejected copy joins; matching context/settings/geology/sample and persisted terrain |

Each stop requires every prior server thread dead, client server reference null,
active settings/context/owner null, empty geology cache, no pending TD requests,
closed explorer listener and no explorer worker/HTTP dispatcher before proceeding.
TD deliberately retains its single daemon inference executor and model sessions
for the JVM; it must be idle between loads. TD's heightmap cache can retain a
completed entry while stopped, but is empty at each next joined-world observation.
The initialized seed is checked against the saved context on successful queries.

Snapshot bytes and all 14 fields, complete existing chunk (-32,-65), actual region
at (-508,-1027), all 529 Overworld persisted records' exact coverage/status/section
block containers, and separate region byte hashes are compared. The expected
sample hash is `09163724065ec1385a0c43dcdc739a3673b63c596ade17041a46fb8f20383a00`,
including 15,597 slate blocks. Snapshot SHA-256 remains
`c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d`.
Nine region files must remain byte-identical through rejection. Reopen region
metadata hashes are recorded separately from the block-container assertion.
Full source-fixture and shared-input manifests must remain unchanged.

## Bounds, reproduction and limits

Launch requires at least 2 GiB free, checked both before preparation and immediately
before Java. Model optimization temporarily consumes about 1.1 GiB. Client lifetime
is bounded to 1,800 seconds; startup to 180 seconds, world open/join to 360 seconds,
commands to 300 seconds, explorer HTTP to 10 seconds, resource cleanup to 30 seconds,
normal shutdown to 90 seconds and exact-child forced cleanup to 30 seconds.
Only resolved stopped disposable ONNX caches are removed. Prior
`packaged-client-01`'s regenerable ONNX cache was removed after an OS process check
to restore disk reserve; its saves, logs and inputs remain. Unrelated temp/ is untouched.

Build `build runtimeProbeJar` with Java 21. Invoke:

```powershell
python scripts/verify-integrated-lifecycle.py --java C:/path/to/isolated-jdk/bin/java.exe `
  --td C:/path/to/official-cpu.jar --manifest C:/path/to/installed-version.json `
  --meta C:/path/to/launcher/meta --output runs/acceptance/NEW-integrated-case `
  --expected-addon-sha256 SHA256-OF-THE-BUILT-ADDON
python scripts/summarize-integrated-lifecycle.py runs/acceptance/NEW-integrated-case `
  --output docs/evidence/NEW-integrated-summary.json
```

Exploratory attempts are retained: -01 hardlink denied before Java; -02 onboarding;
-03 incorrect harness disconnect sequence bounded and forcibly stopped; -04 correct
recovery UI but overly literal probe wording; -05 overly short bridge startup wait.
They are not passing matrices. -06 is the explicit pre-fix executor regression.

This slice does not certify alternate trained weights, generator upgrades,
integrated GPU/CUDA, non-idle explorer shutdown or concurrent in-flight edits,
scale 6, every lifecycle permutation or broad new-chunk generation. #9 stays open
for those remaining gates. The original stronger #5 assertion remains failed;
#11's 14.383-second overhead remains unchanged. CI builds and checks resources
and syntax; runtime acceptance comes from the retained packaged-client runs.
