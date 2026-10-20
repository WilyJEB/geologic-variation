# World-persistent geology settings

Code implementation for [issue #8](https://github.com/WilyJEB/geologic-variation/issues/8).
Edit `config/geologic_variation-common.toml` before creating a new TD world.
The common config proposes settings for new worlds; each world owns a frozen
snapshot thereafter.

| Key under `[geology]` | Default | Allowed values | Units |
| --- | --- | --- | --- |
| `provinceSpacingBlocks` | 2048 | 256..65536 | Minecraft blocks at TD scale 1; multiplied by scale 1..6 |
| `oceanCeilingMetres` | -200 | -10000..10000 | TD elevation metres |
| `lowlandCeilingMetres` | 600 | -10000..10000 | TD elevation metres |
| `mountainFloorMetres` | 1800 | -10000..10000 | TD elevation metres |
| `gentleReliefMetres` | 300 | 0..20000 | Maximum minus minimum of the 25 TD anchor elevation samples, metres |
| `ruggedReliefMetres` | 600 | 0..20000 | Same relief measure, metres |

Values must be finite. Elevation thresholds require `ocean < lowland < mountain`;
relief thresholds require `gentle < rugged`. NeoForge enforces individual type
and range constraints through its normal config validation. The immutable
settings record also rejects invalid ranges and cross-field combinations.
An invalid requested combination prevents a new world's snapshot from being
created. A continuing world keeps its valid snapshot and logs the rejected
configuration. Stone-selection probabilities retain their original values.

## Snapshot lifecycle

The server's TD Overworld load event initializes the snapshot before initial
spawn generation. It is stored at:

`<world>/data/geologic_variation-geology.properties`

A new world adopts the validated config once. Creation writes and flushes a
temporary file, then renames it into place. Existing snapshots are read and
validated without rewriting them. The snapshot is published as an immutable
value to worldgen threads; province cache keys include those settings. Server
shutdown clears the active snapshot and cache before another world can load.
Vanilla Overworlds and other dimensions do not initialize this store.

On startup or config reload, differences between requested and saved settings
are logged. The saved values stay active for the continuing world. Config edits
apply to the next new world; there is no command to mutate an active snapshot.

A world created before this settings system has already used the legacy
constants. On its first load with this update, it receives those exact defaults,
even when the current common config differs. This avoids changing its geology
by adopting a new spacing or classification threshold during upgrade.

Unreadable, incomplete, non-finite, unknown-schema or oversized snapshots stop
initialization with their path in the error. They are never overwritten with
fresh defaults. Preserve this file with world backups; do not delete or edit a
continuing world's snapshot to change generation rules.

## Generation compatibility (issue #9)

New worlds now write `schema=2`, independently pinning `generator=geology-1`.
This rule version covers province hashing/anchors, sampling, classification,
stone probabilities and host replacement. Changes to these rules must bump the
generator identity; retaining an old identity requires preserving its behavior.
The default generation fingerprint remains -4340957394944646000.

The snapshot also records the TD provider seed, world scale, effective tile size,
SHA-256 of the installed TD artifact, a canonical aggregate of the names and
actual SHA-256 hashes of every asset in TD's model manifest (including pipeline
config), and resolved inference provider plus OS/architecture. Hashes use contents,
not installation paths or modification times. Models finish loading before capture;
the load listener runs at LOWEST priority after TD's normal initialization and
checks the provider seed against the world seed. Missing/unreadable context fails
initialization. Artifact hashing intentionally rejects even same-version TD forks
and backend builds with different bytes.

Continuing worlds require exact context equality. Unknown schema/rule versions,
missing fields, invalid settings, changed dependency/model/backend, seed, scale or
tile size stop initialization without changing the snapshot. There is no automatic
upgrade or fallback to current defaults. Restore the original installation and
world inputs from backup to resume. Config edits remain proposals for new worlds.
Every geology query checks live seed/scale/tile/backend before cache lookup and
again after inference, rejecting TD explorer edits that change those inputs.

**This supersedes the legacy adoption behavior described above:** schema-1 and
snapshotless continuing saves have no verifiable dependency/model provenance and
are rejected untouched. Before using this build with one, keep a backup and its
original installation. An explicit migration requires recovering its actual old
context, proving matching generation with that installation, and a reviewed tool
that writes schema 2 while preserving settings (legacy defaults for snapshotless
saves). That migration tool and runtime acceptance are not implemented here;
deleting the snapshot is not an upgrade path.

Model/dependency files must remain immutable for the process lifetime; hashes are
captured once per world load, not on every query. TD models are global and can
already be loaded before the addon runs. Runtime file replacement, simultaneous
servers, differing drivers/hardware under the same provider, and TD optimized
model cache correctness are outside this equality guard. Matching identities do
not prove bitwise native inference reproducibility. Use a fixed runtime and verify
neighboring chunks before accepting an installation change.

## Validation

`./gradlew.bat build` now includes `testSettings`. Tests capture a fingerprint
from the pre-settings implementation across three seeds, six scales, negative
coordinates and classification boundaries. The default settings retain that
fingerprint. Separate tests cover custom settings, file round-trips, unchanged
snapshot bytes on reload, ignored config edits, legacy adoption, world isolation,
invalid values, malformed snapshots and write failures.

Source inspection of the pinned Minecraft/NeoForge server lifecycle confirms
Overworld `LevelEvent.Load` occurs before `setInitialSpawn`. Full compilation
and these file/domain tests pass. Minimal-install runtime acceptance remains:
create a custom-settings TD world, save/reopen it with different common config,
confirm logged snapshot reuse and matching newly generated geology, then repeat
with a pre-settings world. This is retained under #5/#8; no in-game execution
is implied by the pure tests.
