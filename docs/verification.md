# User acceptance for masonry (#13)

2026-10-20: the user reported all supplied checks passed on 0.2.1-dev: survival mining and Silk Touch, cobble smelting, mixed-family tool/furnace recipes, recipe discovery, crafting/stonecutting, shape placement, waterlogging, wall connections and double-slab drops. Placeholder-backed functionality is accepted. Final user-authored textures and their visual review remain tracked under #12 and #14.

# 0.2.1 startup/backend regression fix

2026-10-20:

- User-reported 0% spawn generation/reopen stall reproduced in inspected local
  NeoForge 21.1.251 / Minecraft 1.21.1 logs with TD 2.3.0 CPU and addon 0.2.0.
- debug.log records a chunk-generation exception: the snapshot captured backend
  unknown/Windows 11/amd64, then rejected the resolved CPU/Windows 11/amd64.
  Model byte loading completed before the first lazy inference selected a backend.
- Capture now forces one coarse sample through TD's public inference accessor
  only when the provider is unresolved, then validates the resolved provider
  before any snapshot is saved. Existing unknown snapshots remain rejected;
  the runtime compatibility guard is not relaxed.
- Added regression checks for unknown-to-CPU initialization, already resolved
  providers, failed/still-unknown initialization and rejection of unresolved
  backend snapshots without rewriting them.
- Fixed the polished limestone placeholder: sandstone_top is an actual texture;
  smooth_sandstone is a block model name. Resource checks now require PNGs for
  texture slots, preventing a same-named model from masking missing textures.
- Full Gradle build, testGeology, testSettings, all 711 packaged masonry JSON
  resources and the geology catalog checks pass for 0.2.1-dev.
- User acceptance on 2026-10-20: "All checks pass; world loading didn't take long." The supplied checklist covered the repaired world, newly generated chunks, full exit/relaunch/reopen, a fresh TD world, and the polished limestone placeholder fix. This is user-reported client acceptance on the inspected CPU installation, not dedicated-server or alternate-backend certification.
- The generation-context implementation for #9 is included with this fix; its broader runtime acceptance below remains pending.

# Generation context guards for issue #9

2026-10-20, local JDK 21 / pinned standalone TD / NeoForge:

- Full Gradle build, testGeology and testSettings passed. Default fingerprint
  remains -4340957394944646000; generation formulas and palettes are unchanged.
- Schema-2 round-trip preserves tuned settings and file bytes, ignores edited
  config, and retains the sampled neighboring-province/classification fingerprint.
- Focused tests reject independent generator, seed, scale, tile, TD artifact,
  model and backend changes; malformed/unknown-schema snapshots remain untouched.
  Schema-1 and snapshotless existing worlds are rejected without adoption.
- TD source inspection confirms its normal-priority load listener initializes
  scale/provider; the addon now captures context at LOWEST priority. Compilation
  verifies installed dependency APIs; this does not constitute lifecycle runtime evidence.

Runtime acceptance still required before closing #9:

1. Create a disposable TD world; verify schema 2 contains the resolved provider,
   current seed/scale/tile and dependency/model hashes. Save/reopen with edited
   addon config and compare newly generated neighboring chunks against an
   unchanged-installation reference, including negative coordinates/scales 1/6.
2. Independently change tile size, TD artifact, model/config bytes or backend;
   verify load fails with context diagnostics and snapshot bytes stay unchanged.
   Restore original inputs and confirm successful reopen.
3. Change seed/scale through TD explorer; confirm cached and uncached geology
   queries fail instead of selecting new stone with changed inputs.
4. Confirm schema-1 and snapshotless saves fail without modification; check a
   failed load followed by another world does not reuse active settings/cache.
5. Exercise client and dedicated-server load order before spawn generation,
   vanilla/dimension gating and actual surface mixin behavior. Compare inference
   on the fixed native runtime; matching provider names cannot certify hardware
   or driver equivalence. Keep model files immutable while the process runs.

Normal client create/load/reopen acceptance is recorded above. The adversarial runtime cases listed here remain pending; no general legacy migration tool is provided.

# World settings implementation on 0.2.0-dev (historical schema 1)

2026-10-18, feature/persistent-geology-settings (stacked on stone-families):

- JDK 21 full Gradle build, testGeology and testSettings passed.
- Pre-change generation fingerprint: -4340957394944646000; defaults preserve
  province anchors/identities and classifications for three seeds, six scales,
  negative coordinates and sampled elevation/relief boundaries.
- Persistence tests cover custom snapshot round-trips, byte preservation on
  reload, config-edit isolation, pre-settings world adoption of legacy defaults,
  separate worlds, invalid field combinations, corrupt/unknown-schema/oversized
  snapshots and write failures. Failed reads never recreate the snapshot.
- NeoForge config and Overworld load/stop hooks compile against the pinned API.
  Source lifecycle inspection places Overworld load before initial spawn.
- All 711 masonry JSON resources still match the combined development JAR.
- Actual TD world load, save/reopen and runtime config-reload acceptance remain
  pending under #5/#8. Generator/dependency context versioning remains #9.
- Masonry PR #20 also passed GitHub Actions:
  https://github.com/WilyJEB/geologic-variation/actions/runs/39192373812

# Stone families revision 0.2.0-dev

2026-10-18, local JDK 21.0.6; NeoForge 21.1.251 / Minecraft 1.21.1 and
pinned official Terrain Diffusion 2.3.0 dependency.

- Full Gradle build and testGeology passed on feature/stone-families.
- Registered 64 block/item entries: four rocks x four finishes x four forms
  (full block, stairs, slab, wall). This adds 60 entries to the original four.
- Checked 158 recipes and matching recipe-book advancements; all 711 generated
  JSON resources match the packaged JAR.
- Checked model, vanilla texture, local loot/recipe/tag references and version
  consistency between build metadata and packaged mod metadata.
- Resolved the pinned vanilla furnace and stone-pickaxe recipe tag inputs with
  addon tags; all regional cobbled full blocks are accepted, with decoration
  inputs excluded. One-way conversion recipes cover exact vanilla stone and
  cobblestone consumers.
- Resources derive stair/slab/wall states and natural/Silk Touch/double-slab
  loot from pinned Minecraft templates; wall properties use forceSolidOn like
  vanilla walls. Runtime placement and drops still require in-game acceptance.
- Original block IDs, province classifier and four SURFACE assignments remain
  stable. No active deep palette or higher layer was introduced.
- Final artwork remains pending; docs/stone-assets.json specifies 16 textures.

Artifact: build/libs/geologic-variation-0.2.0-dev.jar. SHA-256 is recorded in
build/libs/geologic-variation-0.2.0-dev.jar.sha256 after the final build.

Pending for #13: in-game mining/Silk Touch, smelting, mixed stone crafting,
recipe discovery, shape placement/waterlogging, wall connections, double-slab
loot and final-art review. No runtime acceptance or issue closure is claimed.

# Standalone revision 0.1.1-dev

2026-10-18:
- Removed the Ulti-World fork dependency and changed required mod metadata to
  official terrain_diffusion_mc version 2.3.0.
- Rebuilt successfully against the official NeoForge 1.21.1 Windows artifact
  from xandergos/terrain-diffusion-mc release 2.3.0-preview.
- Official artifact SHA-512 matched the updated bootstrap pin.
- Full Gradle build and testGeology passed.
- Result: build/libs/geologic-variation-0.1.1-dev.jar.
- No pack, Living Cities, Terralith or Ulti-World configuration is required.
- In-game testing is pending and will be performed by the user in a minimal
  Terrain Diffusion plus addon installation.

The previous 0.1.0 pack-fork verification is retained below as historical context;
use 0.1.1 for standalone testing.

# Verification record

2026-10-18, local Oracle JDK 21.0.6, Gradle 9.2.1.

Passed:
- Full Gradle build against NeoForge 21.1.251 and the SHA-512-verified
  Ulti-World TD_m1.6 Windows dependency.
- Rebuild after exact mixin descriptor, server-stop cache cleanup and
  ore/carver tag additions.
- Standalone Java province tests and Gradle testGeology: deterministic results,
  seed separation, anchor stability, negative coordinates, reverse traversal,
  six world scales, all four rock outcomes, invalid-input rejection.
- All 24 JSON resources parsed, including blockstates with empty variant keys.
- JAR inventory confirms compiled addon, mixin config, metadata, four block and
  item models, self-drop loot, translations, and ore/carver/mining tags.
- Dependency is external and is not included inside the addon JAR.

Result: build/libs/geologic-variation-0.1.0-dev.jar

Not yet performed:
- Client or dedicated-server launch, actual mixin application at runtime.
- Fresh TD Overworld generation, visual checks or full Ulti-World acceptance.
- Ore yield, cave carving, loot, survival mining and save/reopen checks in game.
- Inference latency or generation-throughput measurements.

Suggested disposable-world acceptance:
1. Install the addon on server and client with the pinned TD fork.
2. Generate a new TD Overworld with the pack's fixed models and scale.
3. Check broad stone contacts, then regenerate identical coordinates in a
   second world with the same seed, exploring in reverse order.
4. Mine all four stones in survival; check drops and block placement.
5. Inspect caves and ores in each host stone and specialized Terralith surfaces.
6. Save/reopen; confirm existing chunks and newly generated neighbors agree.
7. Repeat at scale 1 and scale 6, including negative coordinates.
8. Verify ordinary Overworld, Nether and End generation are unchanged.
9. Record cold-anchor inference timing before integrating into a playable pack.

No inference or worldgen quality certification is implied by compilation.
