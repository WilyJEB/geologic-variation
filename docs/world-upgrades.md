# World upgrades and recovery — schema 2

Read this before opening an existing TD world with Geologic Variation 0.2.1-dev or 0.2.2-dev.
The addon checks a world's generation identity to prevent incompatible geology
in newly explored chunks. There is no general migration tool.

| Save state | Behavior in schema-2 builds | Safe next step |
| --- | --- | --- |
| New, uninitialized TD world | Writes schema 2 with resolved generation context and validated requested settings | Keep the snapshot with world backups |
| Valid schema 2, `generator=geology-1`, exact matching context | Loads saved settings; common-config edits apply only to new worlds | Continue with the same installation and world inputs |
| Schema 2 with changed seed, scale, tile size, TD bytes, model bytes or backend identity | Rejects loading without rewriting the snapshot | Restore the exact original context from backup |
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
[controlled failure handling](failure-handling.md); see the verification record
for accepted cases and outstanding coverage under #27.
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

Accepted client evidence: Minecraft 1.21.1, NeoForge 21.1.251, TD 2.3.0 CPU,
Geologic Variation 0.2.1-dev, Java 21.0.12.1, Windows 11/amd64. The supplied
2026-10-27 crash report confirms rejection of saved tile size 256 versus runtime
512; the user reports reopening successfully after restoring 256. Before/after
snapshot byte equality was not independently measured for that runtime test.
Dedicated-server acceptance (#19), alternate backends (#18), other runtime
mismatches and broader lifecycle/reproducibility checks (#9/#5) remain open.
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
