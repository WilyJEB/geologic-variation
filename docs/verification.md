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
