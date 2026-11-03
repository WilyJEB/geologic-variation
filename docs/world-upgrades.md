# World upgrades and recovery — schema 2

Read this before opening an existing TD world with Geologic Variation 0.2.1-dev or 0.2.2-dev.
The addon checks a world's generation identity to prevent incompatible geology
in newly explored chunks. There is no general migration tool.

| Save state | Behavior in schema-2 builds | Safe next step |
| --- | --- | --- |
| New, uninitialized TD world | Writes schema 2 with resolved generation context and validated requested settings | Keep the snapshot with world backups |
| Valid schema 2, `generator=geology-1`, exact matching context | Loads saved settings; common-config edits apply only to new worlds | Continue with the same installation and world inputs |
| Schema 2 with changed generator, seed, scale, tile size, TD bytes, model bytes or backend identity | Rejects loading without rewriting the snapshot | Restore the exact original context from backup |
| Schema 1 or a continuing world without a snapshot | Rejects unverifiable provenance | Use its original installation; a separately designed and reviewed migration is required |
| Snapshot with an unresolved `unknown` backend | Rejects loading | Preserve evidence and request provenance review; see the narrow historical recovery below |
| Malformed, incomplete, oversized or unsupported-schema snapshot | Rejects loading | Restore a known valid backup together with its matching installation |

## Back up before changing the installation

1. Fully stop Minecraft and any dedicated server.
2. Copy the entire world outside the active `saves` directory. Preserve
   `data/geologic_variation-geology.properties` exactly as it is.
3. Preserve the installed addon and TD JARs, TD model assets and pipeline config,
   both mods' configuration files, Java version and backend/OS/architecture.
   Keep artifact checksums and the original startup log with that backup.
4. Try upgrades only on a disposable copy. Keep the original backup untouched.

Exact version labels are insufficient: schema 2 compares the TD artifact's
SHA-256, aggregate model/config content hashes, resolved backend/OS/architecture,
world seed, TD scale, effective tile size and generator identity. Common geology
config edits do not change an existing world's saved geology settings.

## Recover a rejected world

Stop the game, preserve the failed run's log and crash report, and compare the
saved/runtime context in the diagnostic. Restore the original addon, TD artifact,
model assets, backend environment and world inputs from the same known working
backup. Reopen a copy first and check existing terrain and newly explored neighbors.
If the matching environment is unavailable, keep the save for a future reviewed
migration; a fresh disposable world can be used for testing the new installation.

Do not delete snapshots, copy one from another world, change its schema number,
guess hashes or edit context values to force acceptance. These actions discard
the evidence needed to keep future generation consistent. Matching identities
also do not guarantee bitwise native inference across different hardware/drivers.

In 0.2.1-dev, a deliberate mismatch can crash the whole client during
world initialization; worker failures can also leave loading stalled. 0.2.2-dev adds
[controlled failure handling](failure-handling.md). #27's client/dedicated failure
presentation and recovery acceptance is recorded in [verification](verification.md);
the broader context/lifecycle coverage remains under #9.
Rejection is not permission to bypass the guard.

## Historical unknown-backend recovery (#25)

The one-time local recovery preserved the original 0.2.0-dev JAR and snapshot,
verified the world's seed, scale, tile size, generator, TD artifact hash and
model/config hashes, and established CPU as the actual original provider from
the inspected installation/logs. Only the unresolved backend field was repaired
to the verified CPU/Windows 11/amd64 identity; world blocks were not modified.
The replacement 0.2.1-dev JAR resolves the lazy provider before creating snapshots.
The user then reported successful loading, exploration and exit/relaunch/reopen.

This is not a reusable repair recipe. An unknown field does not establish which
provider originally generated a different world. Any similar repair requires
independent provenance evidence, backups of the original snapshot/artifact,
unchanged remaining context, a recorded minimal change and explicit review.
Schema-1/snapshotless worlds lack more context and need a separate migration design.

## Evidence and reporting

The [bounded coarse prototype](coarse-prototype-2026-11-02.md) remains an
unclassified diagnostic; it does not replace geology-1. A generator-only
test-derived addon is rejected before Ready with only the generator context
field differing. Exact original-addon restoration reopens the continuing
fixture with unchanged snapshot bytes, complete sampled blocks and all 529
persisted terrain records. This verifies the version boundary and restoration,
not migration or acceptance of a new geological algorithm. #9 remains open.

The [multi-seed diagnostic classifier](terrain-diagnostics-2026-11-03.md) also
leaves geology-1 unchanged. Its offline terrain-tendency identity is never saved
as a generator and is not a new-world option. Output-changing adoption still
requires an immutable generator identity, explicit new-world selection and real
continuing-save rejection/restoration in both version directions. No geology-1
snapshot migration or rewrite is authorized by these diagnostics.

The [official artifact substitution test](td-artifact-2026-11-01.md) independently
confirms startup rejection when a CPU-resolved official CUDA distribution replaces
the original CPU JAR. Only the artifact hash differs. Restoring the exact original
JAR reopens the fixture with matching settings/context/geology and existing blocks;
snapshot bytes and all 529 persisted terrain records remain unchanged. This does
not establish a migration path or CUDA inference compatibility.

Current dedicated CPU evidence includes the
[2026-11-01 startup matrix](context-startup-2026-11-01.md): independent seed/scale,
schema-1, missing and malformed-snapshot rejection before Ready, exact existing
snapshot/region-file preservation, and successful restoration of each verified
fixture. Continuing config edits preserve active settings and existing blocks.
Those controlled backup-restoration tests are not legacy migration recipes;
unknown saves still require provenance review and the broader #9 matrix remains.

Historical supplied client evidence: Minecraft 1.21.1, NeoForge 21.1.251, TD 2.3.0 CPU,
Geologic Variation 0.2.1-dev, Java 21.0.12.1, Windows 11/amd64. The supplied
2026-10-27 crash report confirms rejection of saved tile size 256 versus runtime
512; the user reports reopening successfully after restoring 256. Before/after
snapshot byte equality was not independently measured for that runtime test.
Later matching-client dedicated-server acceptance (#19) and separate packaged
CPU loading/rejoin evidence are recorded in [verification](verification.md).
Alternate backends (#18) and the remaining context/lifecycle/reproducibility
checks (#9/#5) retain their separate gates.
Compilation and domain tests are separate evidence, not runtime certification.

For diagnosis, provide addon/TD artifact names and checksums, Minecraft/NeoForge/
Java versions, backend/OS/architecture, the saved/runtime mismatch, and relevant
log/crash excerpts. Include whether restoration allowed reopening and whether
snapshot checksums match before/after. Redact account identifiers, tokens, server
addresses and personal path segments from shared copies; retain originals privately.
Never upload whole worlds, model weights or private logs to the repository.

See [compatibility](compatibility.md), [settings](geology-settings.md) and
[verification/release notes](verification.md) for the implementation contract
and historical evidence.
