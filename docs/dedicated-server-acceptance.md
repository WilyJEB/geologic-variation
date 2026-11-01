# Dedicated server and matching-client acceptance (#19)

Verified 2026-10-27, 12:45-12:52 America/Los_Angeles, against source commit
`38b5a35546476bf0aa0be0a5526f6abeaa9ec270`.

## Exact environment

- Minecraft 1.21.1; NeoForge 21.1.251; Geologic Variation 0.2.2-dev.
- Oracle Java 21.0.6+8-LTS-188; Windows 11 amd64.
- AMD Ryzen 9 9900X3D; client renderer NVIDIA GeForce RTX 5080, driver 610.88.
- Official `NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar`, SHA-256
  `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`.
- Saved model/config context hash
  `64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`;
  startup verified all five model/config assets. Resolved inference: CPU.
- Disposable TD world: seed -1550453200536840819, scale 2, tile size 256,
  schema 2, generator geology-1; default addon settings.
- Both sides used ModDevGradle development launches from the same compiled
  sources/resources, with an uncommitted init script selecting the installed
  official CPU dependency. The mod lists contained only Minecraft, NeoForge,
  Terrain Diffusion and Geologic Variation (plus bundled library dependencies).
- Server bound to loopback, game port 25585, RCON 25586, offline Dev identity.
  This tests the game connection and registry synchronization, not online-account
  authentication, remote-network deployment or a separately installed release JAR.
- Reference packaged addon SHA-256:
  `39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.
  Launches used development classes/resources rather than loading that JAR.

## Observed acceptance

1. Server reached Done at 12:45:52.201. Matching client joined at
   12:46:55.613 and rendered the naturally generated gabbro mountain near
   (-1017, 108, -2054). Server block queries and decoded saved block states
   independently identify that coordinate as geologic_variation:gabbro.
2. Server gave all four stone items to Dev. The client displayed their distinct
   placeholder textures in its hotbar and rendered the four-block fixture:

   | Coordinate | Saved and server-confirmed block |
   | --- | --- |
   | -1017, 181, -2052 | geologic_variation:limestone |
   | -1016, 181, -2052 | geologic_variation:slate |
   | -1015, 181, -2052 | geologic_variation:quartzite |
   | -1014, 181, -2052 | geologic_variation:gabbro |

3. Save/stop at 12:49:17 saved players and all three dimensions. The server
   process exited successfully; client showed Connection Lost / Server closed.
4. Restart reached Done at 12:49:52.924. The same client process rejoined at
   12:50:02.880 with inventory and position retained. The fixture persisted;
   client debug targeting reported geologic_variation:limestone at its expected
   coordinate, agreeing with the server and decoded save.
5. Teleport into unexplored terrain near (-1800, -2055) triggered new CPU
   inference. The teleport completed at 12:50:44.318, and the client rendered
   the new savanna terrain. Saved column x=-1800/z=-2055 contains gabbro at
   y=59..64, dirt at 65..68, grass block at 69 and short grass at 70; y=55..58
   retains vanilla diorite. No commands placed regional blocks in this column.
6. Back at the fixture, client right-click placed limestone at
   (-1017, 181, -2053). Client debug targeting, server execute-if-block and the
   decoded saved block state all agreed. This exercises client-to-server block
   placement as well as server-to-client registry/chunk updates.
7. Final save/stop at 12:52:09 again completed all-dimension saves and successful
   server process exit. Client closed normally at 12:52:15. Both Gradle launch
   tasks completed successfully. No addon registry, mixin-application or
   generation-context failures appeared in either run.
8. Snapshot bytes matched before restart and after the final shutdown, SHA-256
   `9f6e5714440e2d20271f362a508f3757bc9fe948ecfdd92b28da5f9f898a98e7`.
   Normal chunk/player changes from this test are intentional; world-file byte
   equality is not claimed.

## Performance observation and remaining gates

The cold teleport requested terrain at 12:50:15.654 and completed at
12:50:44.318. The server logged 28,670 ms / 573 ticks behind. The temporary RCON
helper timed out after 15 seconds, but inference continued and the command
completed; the client stayed connected.

The five serial TD CPU request/completion pairs account for 27.744 seconds of
the 28.664-second request-to-teleport interval:

| TD request start | Duration | Newly computed windows |
| --- | --- | --- |
| 12:50:15.654 | 13.835 s | 56 |
| 12:50:29.496 | 5.983 s | 12 |
| 12:50:35.489 | 1.002 s | 2 |
| 12:50:36.495 | 0.577 s | 1 |
| 12:50:37.581 | 6.347 s | 14 |

These are TD request-to-completion intervals, including possible queue time,
not profiler measurements of addon CPU time. TD's pinned fetchHeightmap API is
blocking; cold terrain inference can stall its server/chunk-worker caller.
The warning alone does not establish an addon regression or distinguish ordinary
TD generation from extra requests caused by the addon.

Static province calculation for this seed/scale and (-1800, -2055) gives anchor
(-2045, -2865), aligned tile x=-2048/z=-3072. That matches the final logged
request. Geology.query requests an anchor tile on a province-cache miss, so this
is evidence consistent with addon-triggered TD inference. The log has no call-site
trace; 6.347 seconds must not be presented as measured incremental addon overhead.
The earlier requests cover tiles near the destination and are consistent with
ordinary TD terrain generation. Request origins and comparative costs remain
unmeasured.

This is a single combined-runtime observation, not a controlled benchmark or
performance acceptance. #7 must compare TD-only with TD-plus-addon using identical
seed, scale, tile, model/artifact/backend, JVM/hardware, chunk targets and traversal;
separate fresh-process and warm-cache trials, repeat runs, and attribute terrain
versus anchor requests with timing/call-site instrumentation. Report baseline TD
cost, additional requests and addon work separately before proposing optimization.

#19's minimal dedicated-server/matching-client gate is satisfied for this exact
CPU development environment. #5's traversal/scale/dimension matrix, #6's complete
ore/carver coverage, #9's remaining context/lifecycle cases and #18's alternate
backend/version matrix remain open. Windows native execution is still not
certified. No generation rules, block IDs, dependencies or user saves changed.

Local raw evidence is retained outside Git in temp/issue19-server-first-stop.log,
temp/issue19-server-restart-stop.log, temp/issue19-client-final.log and
temp/issue19-snapshot-before.properties. The disposable world remains under
runs/server/world. Logs/worlds/model weights and the local launch override are
not part of the PR.
