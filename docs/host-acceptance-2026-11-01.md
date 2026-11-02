# Ore hosts, carving and generation-stage verification, 2026-11-01

## Decision

Issue #6's current four-rock CPU-baseline acceptance is satisfied by production
runtime stage comparisons and controlled survival/feature fixtures. No production
regression requiring a generation-rule change was identified. Issue #5 remains
open: exact final regional-block positions still differ after feature population.
The original strict assertion in `runtime-acceptance.py` is unchanged.

This does not certify alternate backends, all biomes/features, global ore yields,
or the proposed eight-rock/deep palette. It does not reduce the measured cold
anchor-inference cost; optimization remains #11 after #9's save-version gates.

Portable measurements, artifact hashes and raw-log hashes are in
[the evidence JSON](evidence/host-acceptance-2026-11-01.json). Full disposable
worlds/logs remain ignored under `runs/acceptance/hosts-2026-11-01-*`.

## Environment and isolation

- Production Minecraft 1.21.1 / NeoForge 21.1.251, official TD 2.3.0 CPU,
  Oracle Java 21.0.6, Windows 11 amd64. Source baseline: `7099e44`.
- Seed -1550453200536840819, tile 256, same verified models/context as the
  [previous matrix](runtime-matrix-2026-10-28.md). Metadata-only new scale-1/6
  fixtures; no copied chunks between scales and no migration claim.
- Unchanged packaged addon 0.2.2-dev / geology-1, SHA-256
  `39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.
- Eight separate server processes: two scales, two traversal orders, TD-only
  and TD-plus-addon. Both arms include the separate test-only probe. Looped-back
  offline identity, frozen ticks, disabled random ticks/mob spawning.
- A ninth separate process exercises the final destructive fixtures. No user
  installation, account credentials or user saves are changed. Every server
  saves/stops and exits normally; no Java/Python test processes remain.
- Stage and final-fixture probes have different hashes, recorded per case.
  The final probe narrows normalization to the four exact natural IDs and adds
  broader fixture checks. Stage samples contain only those four regional IDs,
  so the earlier normalization has identical meaning for these samples.

## Surface replacement and cave preservation

The new `acceptance stage` command requests an exact generation status and
rejects an already advanced chunk. Each world captures four chunks at SURFACE,
then CARVERS, then FULL: 96 stage measurements overall. Targets and contacts:

| Scale | Chunks | Contact columns | Regional choices |
| --- | --- | --- | --- |
| 1 | (-32,-65), (-20,-64), (-19,-64), (-18,-64) | (-290,-1024) / (-289,-1024) | Slate / quartzite |
| 6 | (-191,-386), (-110,-384), (-109,-384), (-108,-384) | (-1732,-6144) / (-1731,-6144) | Gabbro / slate |

At both SURFACE and CARVERS, complete block-state hashes match across reversed
traversals within each arm, at both scales. Normalizing only the four natural
regional hosts to vanilla stone also makes addon and TD-only hashes identical
for every surface/carver sample. Carving changes the full-state hash in all 32
chunk samples, so the preservation result is not based on an inactive stage.
All addon surface samples contain regional rock;
empty ocean hashes cannot satisfy the check.

Thus the sampled geology hook changes only the intended host identity. Positioned
soil, water, bedrock, deepslate, air and all other states match the control at
these stages. Actual generated carving produces matching states after this same
normalization. No surface-hook or sampled carver-geometry regression is found.

FULL measurements vary in both arms. Initial FULL hashes are snapshots at each
request, before all neighboring feature writes necessarily finish. Final saved
scale-6 comparisons separately find 1,439 regional-stone-versus-coal differences
and zero regional-rock-versus-other-regional-rock conflicts. TD-only final saves
contain 1,004 stone-versus-coal differences. Other feature-state differences also
exist; final saves are not globally identical. Neither these counts nor the older
1,444/1,023 counts prove equal variation magnitude between arms.

The first scale-1 addon world also hosted an early destructive fixture AFTER its
stage measurements. Its recorded stages remain valid, but its subsequently
modified save is deliberately excluded from final natural-terrain comparisons.
The final fixture run is in its own disposable world.

## Survival, placement and host fixtures

The final `acceptance hosts` fixture uses all four registered natural rocks:
limestone, slate, quartzite and gabbro. For each:

- A survival fake player invokes the server's real `destroyBlock` path. Hand
  breaking produces no drop; an iron pickaxe produces one matching cobbled block;
  Silk Touch produces one matching natural block. Correct-tool requirements and
  destroy speed agree with the vanilla-stone material contract. This does not
  measure player input latency or timed breaking animations.
- The actual block item's placement path places the expected natural block.
- Vanilla `Feature.ORE` places 20 coal blocks in a contained uniform host fixture,
  with exactly the same positions as a vanilla-stone reference under the same seed.
  This is a controlled feature test, not a claim about natural ore abundance.
- The real cave carver's `carveBlock` path, with the loaded vanilla cave config
  and a controlled air aquifer, removes the natural host. This single-block path
  check complements the natural CARVERS stage comparisons; it is not a complete
  cave-biome survey for every rock.
- All 24 loaded `OreConfiguration` entries that accept vanilla stone also accept
  each regional natural host, including ordinary ores, infested hosts and the
  stone/dirt/gravel/tuff feature families. The check uses loaded rule predicates;
  only the coal fixture above performs full vein placement.
- All 60 crafted finishes/shapes are excluded from both the surface ore-host
  rule and cave replaceables. No current regional block enters the deep ore-host
  tag: all four shipped families still replace stone, not deepslate.

These scripted server fixtures supplement the earlier user-reported mining and
masonry acceptance; they do not replace packaged client rendering evidence.

## A concrete vanilla coal-order mechanism

`acceptance ore-order` fills the same contained volume with vanilla stone, then
runs two independently seeded groups of eight actual vanilla ore placements.
It repeats with the group order reversed. Configuration matches buried coal's
size 17 and air-exposure discard probability 0.5; owner seeds are 10 and 11.
Origins are deliberately clustered so the features overlap. These are synthetic
feature groups, not replayed natural chunk decoration streams.

Vanilla stone yields 247 coal positions forward and 191 reverse, with a symmetric
difference of 148 positions. Every regional host reproduces the corresponding
vanilla positions exactly in BOTH orders.

The pinned vanilla `OreFeature.canPlaceOre` tests the host before consuming the
air-exposure random draw. A position already changed to ore fails the host test,
skipping that draw. Reusing each group's random stream for subsequent placement
attempts allows overlapping earlier writes to alter subsequent random choices.
The fixture demonstrates order dependence in the vanilla placement path without
needing TD inference or a special regional-host rule.

This is a concrete explanation for how coal variation can arise, not a trace
establishing the origin of every changed position in the production matrix.
Do not turn it into a claim that the addon cannot influence feature scheduling
or variation magnitude. #5's exact final-state assertion remains failed/open.

## Feature limitations and follow-up

`audit-host-feature-rules.py` inventories the exact installed Minecraft resource
JAR followed by TD overrides. It finds 24 relevant configured host-rule features;
their relevant targets use tags, not exact stone/deepslate block-match predicates.
The runtime also checks that an artificial exact `BlockMatchTest(STONE)` does
not accept regional hosts: third-party exact-block rules still require deliberate
compatibility work, rather than broadening vanilla matching globally.

The audit separately finds `minecraft:lake_lava` explicitly configures a
`minecraft:stone` barrier state. That material is placed during later feature
generation, after the current hook, and remains the bounded feature-replacement
work in #29. The audit establishes its configuration, not a lava-pool runtime
acceptance or permission to change fluids, obsidian, player generators or saves.

Next #5 work must either trace natural cross-chunk feature writes and address
their ordering under an explicit versioned contract, or explicitly decide that
the supported promise covers regional palette identity rather than exact final
post-feature positions. Keep the stronger failed matrix visible in either case;
do not change generation, mask ore differences or silently weaken its assertion.

## Reproduction

Build `gradlew.bat build runtimeProbeJar` with JDK 21. Follow the
[runtime setup instructions](runtime-acceptance-tools.md) and supply the exact
CPU TD artifact, installed runtime and immutable models. Run one server at a time:

```powershell
python scripts/verify-ore-hosts.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --output runs/acceptance/new-host-stages
python scripts/verify-ore-hosts.py --fixture-only --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --output runs/acceptance/new-host-fixtures
python scripts/audit-host-feature-rules.py 'C:/path/to/minecraft-extra.jar' `
  'C:/path/to/TD-cpu.jar' --output runs/acceptance/host-rules.json
python scripts/summarize-host-acceptance.py runs/acceptance/new-host-stages `
  runs/acceptance/new-host-fixtures runs/acceptance/host-rules.json `
  --output runs/acceptance/new-host-evidence.json
```

The stage runner enforces surface/carver invariants and nonempty regional
samples, but records FULL failures without claiming they pass. The original
`runtime-acceptance.py reproducibility` mode retains its stronger strict failure.
Never run destructive `hosts`/`ore-order` commands in a normal world, and never
ship the probe with the addon. Build/domain/resource/catalog checks are separate
from the runtime results above.
