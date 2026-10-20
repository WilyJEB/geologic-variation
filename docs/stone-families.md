# Stone families and asset handoff

Implementation for [issue #13](https://github.com/WilyJEB/geologic-variation/issues/13).
Final textures remain user-authored work in #12. The code can be reviewed and
built with vanilla placeholders before those assets are ready.

## Available blocks

Each of limestone, slate, quartzite and gabbro has these full blocks, plus
stairs, slabs and walls for every finish: 16 blocks per rock, 64 total.

| Finish | Limestone example | Acquisition |
| --- | --- | --- |
| Natural | `limestone` | Silk Touch mining; smelt cobbled limestone |
| Cobbled | `cobbled_limestone` | Normal natural-stone mining; shapeless natural stone -> cobbled |
| Polished | `polished_limestone` | 2x2 natural stone -> 4; stonecut natural stone |
| Bricks | `limestone_bricks` | 2x2 polished stone -> 4; stonecut natural stone |

All IDs have the `geologic_variation:` namespace. Brick shape IDs are singular,
e.g. `limestone_brick_stairs`, `limestone_brick_slab`, `limestone_brick_wall`.
The four original natural block IDs are preserved. Existing placed blocks stay
in place; natural stone now drops its cobbled form without Silk Touch.

Each finish crafts 4 stairs from 6 blocks, 6 slabs from 3 blocks, or 6 walls from
6 blocks. Stonecutting gives 1 stair/wall or 2 slabs per block, including direct
natural-stone recipes for the other finishes. Cobbled -> natural smelting uses
200 ticks and yields 0.1 XP. Recipe-book unlocks accompany every recipe.
Double slabs drop two slabs. Vanilla stair/slab/wall classes supply placement,
waterlogging and connection behavior; their runtime acceptance remains pending.

## Crafting compatibility

Both blocks and items have `c:stones`, `c:cobblestones`, finish tags, and
`geologic_variation:families/<stone>` tags. Family tags contain all 16 forms.
`c:cobblestones/normal` contains surface-family cobble and
`c:cobblestones/deepslate` is reserved for deep-family cobble.

Regional cobbled full blocks join `minecraft:stone_tool_materials` and
`minecraft:stone_crafting_materials`, so mixed families work for stone tools
and furnaces. Shapes and decorative finishes are excluded from those inputs.
Any regional natural full block can be converted shapelessly into one vanilla
stone; any regional cobbled full block into one vanilla cobblestone. These
one-way recipes cover consumers that insist on exact vanilla item IDs.

All 64 blocks have pickaxe mining tags and creative entries. Only natural
blocks are ore hosts and base stones. Surface/deep ore tags match their host
layer; crafted masonry never becomes an ore host or carver replacement.

## Surface and deep layers

`Provinces.Stone` now requires an explicit `Layer.SURFACE` or `Layer.DEEP`.
These describe the vanilla host block, not a rock's real-life formation depth.
SURFACE replaces vanilla stone, including exposed stone; DEEP replaces vanilla
deepslate and uses deepslate block properties and ore-host tags.

All four currently shipped stones remain SURFACE because that is their existing
generation contract. Their province selection, distribution and vanilla
deepslate preservation are unchanged. This update adds no new geological rock
species or active deep palette. Future stone entries must choose a layer and
have a complete family/asset plan. Selecting both a surface and deep palette
within each province needs an explicit versioned generation change under #9;
adding enum entries alone does not select them during generation.

A separate higher layer is deferred until its geological purpose and placement
rules have been researched. No elevation cutoff or new stratum is introduced.

## Assets to create

[stone-assets.json](stone-assets.json) lists 16 planned texture files: natural,
cobbled, polished and bricks for each rock. Stairs, slabs and walls share the
matching full-block texture, so they need no separate PNGs in this design.
Vanilla textures are referenced temporarily; no texture artwork is bundled.

Create tileable square PNGs (16x16 is the baseline) under
`src/main/resources/assets/geologic_variation/textures/block/` using the listed
names. Keep editable sources and authorship/license notes alongside the art
handoff. When a set is ready, replace its placeholder entries in the `TEXTURES`
map in `scripts/generate-masonry.py` with namespaced references, for example:
`geologic_variation:block/cobbled_limestone`. Regenerate resources so every
shape receives the new texture; block IDs and recipes stay stable. Avoid editing
generated models individually because regeneration replaces them.

## Build and checks

With JDK 21, after bootstrapping the pinned dependency:

```powershell
./gradlew.bat build
python scripts/generate-masonry.py --check --jar build/libs/geologic-variation-0.2.1-dev.jar
```

Regeneration uses the pinned Minecraft resource JAR materialized by Gradle:

```powershell
python scripts/generate-masonry.py
./gradlew.bat build
```

The checker verifies committed output, model/texture/loot/recipe/tag references,
vanilla furnace/tool input compatibility, exclusion of decorative inputs, and
packaged JSON completeness. CI repeats the checks. Final in-game acceptance
still needs survival mining (with/without Silk Touch), smelting, mixed-family
tools/furnaces, recipe-book discovery, every shape's placement/waterlogging,
wall connections, double-slab drops, and visual review after final art.
