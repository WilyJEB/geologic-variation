# Dedicated startup context guards, 2026-11-01

## Accepted slice and remaining gates

Five independent dedicated-server startup rejection/restoration cases pass on
the pinned CPU baseline: changed seed, changed scale, schema 1, missing snapshot
and a malformed setting. A continuing world also retains its saved settings,
context, region identity and existing blocks when all six common-config proposals
are changed before a fresh-process reopen. No production regression was found;
the addon JAR and generation rules remain unchanged.

This is partial #9 acceptance, not closure. Actual TD artifact/model/backend
changes, generator-upgrade cases, live seed/scale changes before cached and
uncached queries, live config reload, and the remaining integrated-client/lifecycle
cases keep their separate runtime gates. Earlier tile-size/live-seed and
client/dedicated failure evidence remains in [verification](verification.md).
#18 retains alternate-backend/hardware support. #5's strict post-feature failure
and contract decision are unchanged; #11 remains the cold-sampling optimization.

Portable observations, exact artifact hashes, snapshot/region hashes and raw-log
hashes are in [the evidence JSON](evidence/context-startup-2026-11-01.json).

## Environment and fixture provenance

- Source baseline `85b4907`, Minecraft 1.21.1 / NeoForge 21.1.251 / official TD
  2.3.0 CPU / Java 21.0.6 / Windows 11 amd64.
- Unchanged production addon 0.2.2-dev / geology-1, SHA-256
  `39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.
- TD SHA-256 `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`;
  aggregate model/config hash
  `64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`.
- Seed -1550453200536840819, scale 1, tile 256. The initial metadata-only fixture
  supplies a matching schema-2 context, then actually generates and saves regional
  terrain. This does not certify world-creation UI or a new-snapshot migration.
- Each negative case clones that verified baseline's entire world, including
  existing chunks, into a NEW directory. Only the named file in that copy is
  changed. No user world, installed profile, original template or model input is
  modified. Restoring the test copy's own captured bytes is backup restoration,
  not migration of a genuinely unknown legacy/snapshotless save.
- Six disposable directories and twelve separate JVM launches: two baseline
  control launches, five deliberately rejected launches, five restored launches.
  Production server launch targets use actual TD/addon/test-probe JARs in mods/.
  Offline loopback identity, frozen normal ticks, disabled random ticks/spawning
  and zero spawn-chunk radius isolate ordinary block changes.

## Continuing common-config isolation

The control generates full chunk (-32,-65), queries geology at (-508,-1027),
saves/stops, edits the common config and starts a new process on that same world.
The test-only `acceptance settings` command independently reports active and
requested settings, saved context, and server ownership.

| Setting | Saved/active | New requested proposal |
| --- | --- | --- |
| Province spacing | 2048 | 4096 |
| Ocean ceiling | -200 | -300 |
| Lowland ceiling | 600 | 700 |
| Mountain floor | 1800 | 1900 |
| Gentle relief | 300 | 350 |
| Rugged relief | 600 | 650 |

The second process sees the new proposals while all saved values stay active.
It logs that saved settings remain active and edits apply only to new worlds.
The complete existing-chunk block hash and actual region record match the first
process; the snapshot bytes remain unchanged. Every restored negative case also
retains these edited proposals while using the original saved values.

Snapshot SHA-256:
`c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d`.
The existing sample contains regional blocks; this is not an empty-ocean check.
This exercises restart with edited config, not a hot `ModConfigEvent.Reloading`
or acceptance of custom settings during new-world creation.

## Independent rejection and restoration

| Case | Deliberate change in the disposable copy | Observed rejection |
| --- | --- | --- |
| Seed | `level.dat` world-generation seed plus one | Saved/runtime context differs ONLY in seed |
| Scale | TD world-settings data scale 1 to 6 | Saved/runtime context differs ONLY in scale |
| Schema 1 | Remove context fields and set schema 1 | Unverified legacy context; no adoption |
| Missing | Remove the copied geology snapshot | Existing world has no verified context; no recreation |
| Malformed | Province spacing replaced by a noninteger value | Cannot continue geology; invalid snapshot retained |

Every rejected process:

- Logs the intended geology guard and restoration guidance. Seed/scale checks
  parse the full logged saved/runtime records and require exactly the intended
  field to differ; matching a generic crash message is insufficient.
- Exits before the server's Done/Ready message and RCON startup. The controlled
  dedicated rejection produces diagnostics/crash-report output and exit code 0;
  that code alone is not an acceptance signal. No client process runs here.
- Preserves all nine existing region files byte-for-byte, with no new `.mca`
  files. The snapshot remains byte-identical, or remains absent for the missing
  case. Intentional input edits in `level.dat`/TD scale data are outside this
  snapshot/region-file equality claim; full-world byte equality is not asserted.

After rejection, the harness restores exactly the changed file's original bytes
from that same verified fixture and starts another process. Every copy reaches
Ready, returns the original active settings/context and region record, retains
the complete existing-block hash and original snapshot bytes, and saves/stops
normally. These are full-process dedicated restorations, not proof of recovery
between worlds in one integrated-client process.

## Reproduction and evidence handling

Prepare the [pinned production runtime](runtime-acceptance-tools.md), then:

```powershell
gradlew.bat build runtimeProbeJar
python scripts/verify-context-startup.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --output runs/acceptance/new-context-startup
python scripts/summarize-context-startup.py runs/acceptance/new-context-startup `
  --output runs/acceptance/new-context-evidence.json
```

The runner refuses existing output directories, requires 2 GiB free for each
transient ONNX optimization, links the immutable TD/model inputs, and copies the
addon/probe artifacts. It checks storage errors and removes only its resolved
in-case optimization cache after the process exits. Never edit linked inputs.
The exporter requires all five cases, nonempty regional/existing-file samples,
matching artifacts, independent seed/scale diagnostics, preservation/restoration
assertions, and unchanged raw-log hashes before publishing portable JSON.

The accepted raw suite is ignored under
`runs/acceptance/context-startup-2026-11-01-02`. Initial harness development is not
part of accepted evidence. Logs, crash reports, credentials, saves and model
weights stay local; only hashes and portable observations are committed. All
final processes exit; no Java/Python test processes remain. Build/domain/resource
checks are separate from these runtime results.
