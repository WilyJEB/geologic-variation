# Controlled geology failures (0.2.2-dev, #27)

Geology initialization, incompatible live context and terrain-query runtime
failures latch the first diagnostic on the affected Minecraft server. Every
subsequent geology query rejects that server, including cached queries. Spawn
and chunk waits rethrow that failure on the owning server thread through the
existing fatal-check polling point. The addon does not put its errors in
Minecraft's process-global fatal slot, so they cannot poison a later world.

The server retains its normal exception report and resource cleanup. For a
tagged geology failure only, the integrated server does not request a fatal
client crash. After its server thread finishes, the client returns to a readable
error screen with the mismatched fields and recovery guidance. This works during
the initial loading wait and after joining. Unrelated errors retain Minecraft's
normal crash handling. Client hooks are in the client-only mixin list.

On a geology failure the addon also closes TD's explorer explicitly. Minecraft's
exceptional server exit skips the normal ServerStoppingEvent used by TD to close
that listener; its HTTP dispatcher must not outlive the stopped server.

Failed servers skip chunk save/flush and the normal save-ready drain loop,
including the independent flush performed when the chunk source closes.
Individual chunk saves also reject work after failure. Resource closing still
runs. Surface replacement resolves its entire column palette before changing a
chunk, and queries carry server identity so late work cannot adopt the next
world's context. Shutdown clears active settings/context and the province cache.

The chunk-holder boundary converts tagged synchronous step failures into failed
chunk results and cancels further steps on that server. This prevents the vanilla
worker uncaught-exception handler from terminating the process. The failed step's
status future completes as an error; unrelated failures keep vanilla behavior.

This is an abort, not a transactional rollback. Unsaved play since the last
successful save can be lost. Writes already submitted before detection cannot
be undone. Keep backups and test in disposable copies. The implementation does
not edit the geology snapshot on rejection, change generation rules or migrate
existing chunks. Schema 2 and `generator=geology-1` remain unchanged.

## Verification procedure

1. Back up a disposable, working TD world and its installation/configuration.
   Record SHA-256 hashes of the geology snapshot and every region `.mca` file.
2. Close Minecraft, change only TD `tile_size` from 256 to 512, and reopen that
   world. Expect a geology error screen identifying saved 256/runtime 512,
   with Minecraft still usable. Check the full saved/runtime diagnostic in the log.
3. Compare the snapshot and region files with the baseline. Try another compatible
   world in the same client process; it must load without the prior failure.
4. Restore tile size 256, restart and reopen the original disposable world.
5. On a separate disposable copy with commands enabled, run `/td-explore`.
   Confirm the explorer belongs to this test process and its seed matches the
   world. Change its live seed, then request new chunks (for example by teleport).
   Expect prompt shutdown and the same recoverable screen, with seed identified.
   Preserve the log and compare the snapshot/region files around the failure.
   For an isolated block-state comparison, freeze normal ticks (`/tick freeze`)
   and pause to save before recording the baseline; random ticks and unloads
   otherwise introduce ordinary changes before the mismatch is detected.
6. Reopen a compatible world in that process. Separately exercise the same
   rejection on a dedicated server, checking clear logs and completed shutdown.

The CPU client evidence and outstanding coverage are recorded in
[verification](verification.md). A full TD inference call that never returns is
outside this failure latch; it is not an inference timeout or native-process
watchdog. [World upgrades](world-upgrades.md) explains restoration and unsupported
legacy saves. Do not bypass rejection by deleting or editing snapshots.
