# Production runtime verification, 2026-10-27–28

This report covers #5 reproducibility, #7 performance attribution, dimension
gating and a separate packaged client/server smoke test. The shipped addon is
unchanged: 0.2.2-dev, generator geology-1, SHA-256
`39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.
Runtime source baseline is commit `f6be304` (production code matches `38b5a35`).

Portable results, per-case artifact hashes and raw-log hashes are committed in
[the evidence JSON](evidence/runtime-acceptance-2026-10-28.json).
[Tool instructions](runtime-acceptance-tools.md) describe reproduction and limits.
Full logs, prepared worlds and models remain locally under ignored runs/acceptance/.
The suite was resumed across sessions; it is not one uninterrupted benchmark run.

## Pinned environment and isolation

- Minecraft 1.21.1, production NeoForge 21.1.251 installed with its official
  installer; production `forgeserver` and `forgeclient` launch targets.
- Official TD 2.3.0 CPU NeoForge artifact, SHA-256
  `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`.
- Model/config context SHA-256
  `64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`;
  startup validates the five official assets. Tile size 256.
- Windows 11 amd64, Oracle Java 21.0.6; AMD Ryzen 9 9900X3D. JVM reports six
  available processors; both performance arms use 2 GiB initial / 6 GiB maximum
  heap. Client renderer is RTX 5080, driver 610.88; inference remains CPU.
- Seed -1550453200536840819. Matrix cases use metadata-only disposable fixtures
  with matching explicit schema-2 context and scale; no existing chunks are copied
  between scales. This does not certify a new migration path or world-creation UI.
- Matrix/benchmark arms contain TD plus the separate test-only probe, with or
  without the addon JAR. Probe hashes are recorded per case because tooling was
  extended between stages. The final interactive smoke test contains no probe.
- Loopback/offline Dev identity; no account credentials or user profile changes.
  Each server runs separately. Normal/random ticks and mob spawning are disabled
  for matrix samples. A disabled watchdog permits long CPU inference to finish.

## Reproducibility: mixed result, #5 remains open

The strengthened matrix uses actual land and nearby province contacts. Each pair
generates the same chunks in opposite orders, exits the process, reopens, checks
existing chunks and generates a new neighboring chunk. The initial exploratory
deep-ocean-only samples are excluded from accepted block evidence because their
regional-block hashes were empty. The final samples contain tens of thousands of
regional blocks per chunk.

| Scale | Sample chunks | Contact block coordinates | Actual choices on either side |
| --- | --- | --- | --- |
| 1 | (-32,-65), (-20,-64), (-19,-64), (-18,-64) | (-290,-1024) / (-289,-1024) | Slate / quartzite |
| 6 | (-191,-386), (-110,-384), (-109,-384), (-108,-384) | (-1732,-6144) / (-1731,-6144) | Gabbro / slate |

Passed:

- Actual region records (province identity, anchor, selected stone, elevation and
  relief) match across traversal orders at both scales, including negative axes
  and contacts. The runtime reports the addon origin under mods/, not dev classes.
- Scale-1 positioned regional-block hashes match in all four sampled chunks.
- All four cases retain their regional-block hashes through a full process
  restart. Snapshot bytes remain unchanged in every case.
- Newly generated neighbors (-32,-66) at scale 1 and (-191,-387) at scale 6 have
  matching regional-block hashes across the respective opposite-order worlds.

The strict scale-6 positioned regional-block assertion **fails** in three of four
initial chunk samples. The suite preserves that failure rather than weakening
the assertion. Decoding the final saved chunks finds 1,444 differences involving
regional blocks: every one is regional stone versus vanilla coal ore. There are
zero gabbro-versus-slate conflicts at common positions. Complete chunk hashes also
vary in non-geology features; the final scale-1 saves have 625 differing blocks,
none involving regional blocks.

A separate production TD-only scale-6 control repeats the same opposite traversal,
restart and neighboring generation. It has 1,023 vanilla stone-versus-coal-ore
differences in the final samples, with no addon installed. This establishes that
the *kind* of order variation exists without the addon. It does not prove that
the addon has no effect on the magnitude or identify an upstream root cause.

Consequently this is evidence for stable palette identity and recovery, **not**
a passing exact final-block determinism matrix. No production palette fix is
identified. Keep #5 open until the expected contract for post-feature differences
is explicitly resolved; coordinate ore/host investigation with #6. Do not change
generation rules or hide the difference by broadly converting ores/features.

## Dimension gating: passed for the samples

Production TD-only and addon arms generated chunk (0,0) in an ordinary vanilla
Overworld, Nether and End. Each pair has an identical complete block-state hash.
The addon arm creates no regional blocks and no geology snapshot. This supports
the current TD-Overworld-only gate; it is not certification of every biome,
dimension provider, feature or mod combination.

## Performance: separate ordinary TD work from additional anchor requests

Three fresh-process pairs use identical seed, scale 1, tile/model/backend/JVM
settings, targets and chunk order. Arm order alternates. Both arms perform the
same public coarse-model preparation before timing. Fresh process means empty
application inference caches, not a flushed OS filesystem cache or an idle-machine
guarantee. Chunk times exclude the subsequent block hashing and RPC overhead.

| Pair | TD-only route | TD + addon route | Paired difference |
| --- | --- | --- | --- |
| 1 | 37.943 s | 51.757 s | 13.814 s |
| 2 | 36.882 s | 51.265 s | 14.383 s |
| 3 | 35.567 s | 53.757 s | 18.190 s |

The median paired difference is 14.383 seconds for this workload. Each TD-only
route makes six uncached heightmap-region requests; each addon route makes eight.
The stack-based probe directly labels the two extra anchor locations:

- x=-1024/z=-1536: caller wait approximately 6.09–6.18 seconds.
- x=512/z=-1024: caller wait approximately 9.78–10.00 seconds.

These are TD work requested by our sampler, not evidence that our build slowed
TD's inference implementation. Caller waits include queue/cache effects and can
overlap; do not add them to derive incremental overhead. The paired route
comparison measures the net difference under the stated conditions. It cannot
retroactively decompose the earlier #19 scale-2 teleport or establish a general
slowdown percentage.

Later neighboring-chunk completion calls, after the surrounding TD tiles have
been requested, take 68.9–76.3 ms in TD-only and 77.1–86.6 ms with the addon.
Earlier requests may already have partially generated those neighboring chunks;
these are warmed-neighborhood completion timings, not isolated fresh-chunk or
scanner CPU benchmarks. Warm loaded-chunk reads take 0.04–0.17 ms. Those are reads,
not warm generation.
Four simultaneous cold queries for one remote province complete with identical
results in 13.08–13.54 seconds; subsequent cached region queries take
0.0265–0.0289 ms. No deadlock occurs in these trials. The actual cache's synthetic
600-key policy check retains exactly 512 entries, preserves a touched LRU key,
evicts an older key and clears the injected entries afterward. This tests policy,
not throughput under 600 real remote inference requests.

#7 now has exact baseline/addon, cold/cached, concurrent and bounded-cache evidence
for this CPU environment. The dominant additional cold cost here is requesting
remote anchor inference. No inference-speed regression or scanner bottleneck is
established. Do not change the current generation contract on these timings;
evaluate sampler/coarse-data alternatives under #11 with #9 versioning and new
paired benchmarks before adopting an optimization. Other hardware/backends remain
under #18 and are not implied by this result.

## Packaged client/server smoke: passed

On 2026-10-28 the production server and production client loaded only Minecraft,
NeoForge, TD and the actual addon JAR under their separate mods/ directories.
There were no dev-class directories and no test probe in this run. The isolated
client reused pinned installed launcher libraries/assets and the offline Dev
identity without changing that launcher profile.

- First server reached Done at 14:51:35; client joined at 14:52:51. All four
  regional stone items and the fixture rendered correctly.
- Client placed limestone at (-1017,181,-2054), confirmed by the server. The
  first server saved and stopped normally through RCON. Its initial controller
  had encountered EOF on noninteractive input; the controller was corrected to
  use an explicit STOP file. This was a harness error, not an addon/server crash.
- A fresh server process reopened a copy of that saved world at 14:54:31. The
  same client process rejoined at 14:54:43. Client debug targeting and server
  queries confirmed the placed limestone; natural gabbro at (-1017,108,-2054)
  remained present. Inventory and fixture persisted.
- The corrected controller saved and exited successfully on STOP; the client
  closed normally. Snapshot SHA-256 remains
  `9f6e5714440e2d20271f362a508f3757bc9fe948ecfdd92b28da5f9f898a98e7`.

This closes the earlier distinction between development launches and a separately
installed packaged JAR on the recorded CPU baseline. It does not certify online
authentication, remote networking, Windows native/CUDA inference or arbitrary
modpacks. Build/resource/domain checks remain separate from these runtime results.
