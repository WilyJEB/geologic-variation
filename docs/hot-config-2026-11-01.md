# Actual hot common-config reload, 2026-11-01

Both independent populated-cache and empty-cache cases pass in a continuing
dedicated world on the pinned standalone CPU environment. Four JVM launches
cover two live reloads and their fresh-process reopenings. No production
regression was reproduced; production code, addon JAR, geology-1, IDs and
provenance guards are unchanged. Ulti-World stays optional. This accepts only
the hot common-config portion of #9, which remains open.

## Runtime and fixture

Source baseline is merged PR #37, `127e36f8f35718916b56deae1712086909f54168`.
Minecraft 1.21.1 / NeoForge 21.1.251 / FML loader 4.0.44 / TD 2.3.0 CPU /
Java 21.0.6 / Windows 11 amd64 match the earlier acceptance environment.
The runner clones PR #36's verified, already saved scale-1 regional terrain
into two NEW directories. It never launches or edits the source fixture.
A complete source-file hash manifest matches after each case.

The production addon SHA-256 remains
`39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`;
TD is `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`;
model/config aggregate is
`64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`.
The separate probe SHA-256 is
`1f2a99fe21e5b5fcdfc6a02e8657d955445ae78d5589f0b0f758fab0c8077b64`.
Seed -1550453200536840819, scale 1, tile 256, resolved CPU backend and
generation context remain fixed throughout.

## Trigger and observation

Before implementation, `javap -p -c` against the installed loader JAR verified
`ConfigTracker.openConfig` registers a NightConfig `FileWatcher` callback unless
disabled. `ConfigWatcher.run` invokes `ConfigTracker.loadConfig` with the
`ModConfigEvent.Reloading` constructor; `ModConfig.setConfig` accepts the new
spec data and dispatches the event through the owning mod container. The
constructor reference was also verified in `javap -p -c -v` bootstrap metadata.
The actual loader JAR SHA-256 is
`f2096cd86d605c0484971fc712208e0dc6cecfe53e056db61d44a98cadc19499`;
NightConfig core 3.8.3 is
`971dc88c1c22085611ee1c300f5bbf8595938178e819befbb5e98c3cbd272b79`.

The probe attaches a passive LOWEST-priority listener to the addon's own mod
event bus at command registration. It neither constructs/dispatches an event
nor calls the production reload handler. The Python runner writes the actual
common TOML while the original server PID is alive, then polls observed events.
Both cases report the real `ModConfigEvent$Reloading`, COMMON type, correct file,
identical spec object, changed requested settings, `FileWatcher-1-thread-1`, and
an actual `ConfigWatcher.run` stack frame. The production saved-settings warning
is required in the log suffix after the external edit. One case logs two watcher
callbacks with identical proposals, the other one; all logged callbacks are
retained and checked. The test does not assume exactly one OS file event.

All six proposals change together:

| Setting | Saved/active | Requested after hot reload |
| --- | --- | --- |
| Province spacing | 2048 | 4096 |
| Ocean ceiling | -200 | -300 |
| Lowland ceiling | 600 | 700 |
| Mountain floor | 1800 | 1900 |
| Gentle relief | 300 | 350 |
| Rugged relief | 600 | 650 |

Active settings, owner identity and generation context remain unchanged. The
warning says saved world settings remain active and edits apply only to new
worlds. Reopening retains the edited proposals and original saved settings.

## Query and preservation assertions

Normal ticks are frozen, random ticks/spawning disabled, spawn radius zero.
The existing full chunk (-32,-65) contains 15,597 regional slate blocks.
Before editing, each case clears the real geology cache and queries
(-508,-1027), requiring exactly one real province entry and matching geology.
The populated arm keeps that entry; the empty arm clears it again.

After the actual reload, the first query observes respectively one or zero
entries, then returns the same complete region record and one cached entry.
The populated query makes zero heightmap calls. The empty query makes one
heightmap call, proving a genuine geology-cache miss; this does not claim TD's
own inference caches are empty. Both execute on the server thread. Region
queries do not request Minecraft chunks; block checks only load the existing
saved sample. No new neighboring Minecraft chunk is deliberately generated.

The live sample, saved sample and reopened complete block hashes match:
`09163724065ec1385a0c43dcdc739a3673b63c596ade17041a46fb8f20383a00`.
Snapshot bytes match before the edit, live, after save/stop and after reopen:
SHA-256 `c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d`.
All 529 persisted Overworld terrain records retain their section block-state
containers, status and exact coverage after save and reopen: one full record,
8 initialize-light, 16 carvers, 24 biomes and 480 structure-starts records.
This separately compares stored blocks and chunk coverage; it excludes light,
ticks and timestamps. Region `.mca` byte hashes are retained as metadata evidence,
but are not used as the block-state acceptance assertion.

All four servers save/stop normally with exit code 0. No Java/Python test process
remains. Free space returned to about 5.3 GB. Each launch requires at least 2 GiB
free; transient ONNX optimizations cost about 1.1 GB. Cleanup removes only the
resolved `terrain-diffusion-models/onnx-cache` inside each stopped disposable
case. Models and TD are immutable links; addon/probe outputs are copied.

## Reproduction and limits

Prepare the [pinned production environment](runtime-acceptance-tools.md), then:

```powershell
gradlew.bat build runtimeProbeJar
python scripts/verify-hot-config.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --fixture 'runs/acceptance/context-startup-2026-11-01-02/baseline/world' `
  --output runs/acceptance/new-hot-config
python scripts/summarize-hot-config.py runs/acceptance/new-hot-config `
  --output docs/evidence/hot-config-2026-11-01.json
```

The runner refuses existing output and uses bounded waits: startup 360 seconds,
RCON transport 300 seconds per command, reload polling 30 seconds, clean exit
90 seconds, forced cleanup 30 seconds. These are tooling bounds, not performance
thresholds or a native inference watchdog. The exporter rechecks observations,
artifact/context pins, preservation and raw log hashes. Portable evidence is
[committed here](evidence/hot-config-2026-11-01.json); raw saves/logs/results remain
ignored under `runs/acceptance/hot-config-2026-11-01-02`. Attempt -01 stopped
before launch because sandbox permissions denied an immutable input hardlink;
it contributes no runtime acceptance. Unrelated `temp/` material is untouched.

Local build/domain suites, resource validation (64 blocks / 158 recipes /
711 JSON resources), catalog validation, Python syntax and evidence export pass.
CI compiles the opt-in probe and syntax-checks the new runners; it does not
execute this CPU runtime matrix.

#9 remains open for actual artifact/model/backend substitutions, generator
upgrades and remaining integrated-client/same-process lifecycle gates. Invalid
or concurrently edited config, edits during in-flight inference, custom-settings
new-world creation, scale-6 reloads and broad neighboring-chunk generation are
outside this slice. The original #5 strict post-feature determinism failure is
unchanged; #11 retains the unchanged 14.383-second cold-route opportunity.
Next concrete slice: an independent incompatible TD artifact substitution at
startup, with exact context diagnostics, snapshot/terrain preservation and
restoration/reopen on another known-provenance disposable copy.
