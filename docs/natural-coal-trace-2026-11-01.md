# Natural cross-chunk ore-order trace, 2026-11-01

Subsequent policy resolution: see the [supported reproducibility contract](reproducibility-contract.md).
It selects stable geology/save continuity while retaining the strict failure
reported below. The investigation's pending-decision statements are historical.

## Result and acceptance boundary

The remaining #5 final-position failure has a demonstrated natural feature-order
cause in both production arms: a neighboring chunk's gravel or ore write can
remove coal-host eligibility, skip a random draw, shift a later vein's origin,
and produce coal-versus-host differences in the final saved blocks. This extends
the earlier controlled fixture to actual natural decoration, with complete
example chains recorded in [portable evidence](evidence/natural-coal-trace-2026-11-01.json).

The traced causes occur after palette assignment; no geology-1 palette fix is
identified. This does not prove identical variation magnitude between arms, explain every
feature difference, or certify globally deterministic final terrain. #5 stays
open with its original strict assertion unchanged. The next decision is whether
the supported contract promises deterministic regional identity/host assignment
or also requires exact final post-feature positions. Achieving the stronger
promise would require deliberate feature/RNG/order work and #9 versioning; it
must not silently alter continuing worlds or globally convert ores to host rock.

PR #34 is merged and #6 is closed for the previously recorded four-rock CPU
acceptance. No production code, dependency pin, block ID, snapshot or release JAR
changes in this follow-up. The 14.383-second cold-route sampling cost is unchanged
and remains the separate #11 optimization opportunity.

## Exact scope

- Source baseline `268c4ac`, Minecraft 1.21.1, NeoForge 21.1.251, official TD
  2.3.0 CPU, Java 21.0.6, Windows 11 amd64. Same seed
  -1550453200536840819, scale 6, tile 256 and pinned models as the
  [previous host matrix](host-acceptance-2026-11-01.md).
- Actual addon 0.2.2-dev / geology-1 SHA-256
  `39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.
- Four fresh, metadata-only disposable production worlds: TD-only/addon, each
  with forward/reverse FULL-chunk requests for (-191,-386), (-110,-384),
  (-109,-384), (-108,-384). No pre-staging, copied chunks or user saves.
- Separate opt-in test probe in both arms. Permission-level-4 commands select
  up to 16 watched chunks; this run uses four. The trace records natural
  `OreFeature` calls from `WorldGenRegion`, a bounded two-chunk source halo,
  and at most 500,000 events per process. Overflow or unmatched writes invalidate
  acceptance. All final cases are below the cap, with zero unmatched writes.
- The tracer observes feature-seed inputs and `WorldgenRandom.getCount()` without
  drawing random values. It forwards the original section write once and records
  the returned previous state. Source chunk, feature origin, target, eligibility
  result and per-check random counts link decisions to actual writes.
- Coal checks and coal/eligibility-removing ore-feature writes are captured.
  Host-to-host replacements such as granite/diorite/andesite are omitted; this
  is not a universal feature-write trace. The collector can change scheduling
  timing, so these runs are diagnostic evidence, not latency or frequency
  benchmarks. Sequence numbers order recorded callbacks, not every engine action.

## Natural chains

In the TD-only pair, chunk (-110,-384) writes gravel at
(-1743,80,-6133). When chunk (-109,-384)'s buried-coal placement encounters it,
the coal target rejects gravel and its random counter stays 4102. In the other
order, the same seeded placement starts at the same origin, encounters vanilla
stone at that position, accepts it and advances 4102 to 4103.

The next coal-placement origin differs: (-1736,9,-6131) versus
(-1743,116,-6133). Actual writes from that next placement account for final saved
coal-versus-stone differences, including (-1736,6,-6130). The evidence contains
the blocking write, matching feature seed/origin, both checks and downstream
saved-position examples together.

The addon pair independently contains an emerald-ore example: chunk (-110,-384)
writes emerald ore at (-1754,103,-6130), replacing gabbro. Buried coal from
(-110,-383) later rejects that ore without a draw, counter 4628 to 4628. In the
other traversal, the same placement encounters gabbro, accepts it and advances
4628 to 4629. Its next origin shifts from (-1755,92,-6128) to
(-1760,98,-6116); recorded writes produce saved coal-versus-gabbro differences
including (-1756,89,-6129).

These examples show ordinary feature interactions in both arms. Coal itself can
also block later host checks, but the first traced cross-chunk blocker need not
be coal. This is why recording only coal writes was insufficient to identify
the earlier cause.

## Coverage and retained failure

| Arm/order | Final coal positions in watched chunks | Cross-chunk coal writes into watched chunks | Final coal positions without an observed coal write |
| --- | --- | --- | --- |
| TD-only forward | 2943 | 305 | 0 |
| TD-only reverse | 2976 | 325 | 0 |
| Addon forward | 2942 | 304 | 0 |
| Addon reverse | 2978 | 327 | 0 |

All coal-valued sides of final host/coal differences have observed natural coal
writes. The analyzer retains two complete downstream-difference chains for the
TD-only pair and three for the addon pair. No observed coal write changes its
state between the eligibility check and the actual mutation; these samples do
not require a simultaneous section-write race to explain the variation.

Final saves still have 1,006 stone/coal differences in TD-only and 1,026
regional-stone/coal differences with the addon. The addon has zero conflicts
between distinct regional rock types. Complete saved-block differences also
include non-coal features (1,959 TD-only / 1,883 addon total differences). Do not
interpret changed counts versus earlier runs as improvement or regression.

Region identity, pre-feature/carver preservation, scale-1/6 boundaries and
restart evidence remain as previously recorded; this trace does not rerun those
separate gates. It specifically resolves a natural cause behind the remaining
post-feature comparison failure, not the final determinism-policy decision.

## Storage, process cleanup and reproducibility

Raw traces/logs/worlds remain ignored under
`runs/acceptance/natural-coal-2026-11-01-05`. Case artifact, raw trace and log hashes
are committed in the portable evidence. Only the final clean four-world run is
accepted. Earlier exploratory runs established the needed trace scope; attempts
with disk/optimization-cache write failures are excluded entirely.

Per-case ONNX optimization outputs used about 1.1 GB each and exhausted the local
drive during exploration. Only regenerable optimization caches and redundant
copied TD JARs from this turn's stopped exploratory worlds were removed. Original
five model inputs, saves, logs and traces were retained. The final runner requires
2 GiB free before starting another process, hardlinks the immutable TD dependency,
copies addon/probe outputs, and removes only its own resolved in-case optimization
cache AFTER process exit. It rejects storage-failed cases. All four final servers
saved/stopped normally; no Java/Python test processes remain. Cleanup affects
diagnostic artifacts, not a user's gameplay installation or world.

With the [production runtime prerequisites](runtime-acceptance-tools.md) prepared:

```powershell
gradlew.bat build runtimeProbeJar
python scripts/trace-natural-coal.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --output runs/acceptance/new-natural-coal
python scripts/summarize-natural-coal.py runs/acceptance/new-natural-coal `
  --output runs/acceptance/new-natural-coal-evidence.json
```

Run one test server at a time. The analyzer rejects missing final coal writes,
trace overflow, unmatched writes, changed trace hashes, or absence of a complete
natural cross-chunk/check/draw/next-origin/final-difference example in either arm.
It reports the saved-state failure; it does not relax the original strict
reproducibility assertion or modify generation to force a passing hash.
