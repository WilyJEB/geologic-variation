# Geologic Variation

Independent NeoForge 1.21.1 addon for official Terrain Diffusion 2.3.0. Adds four
mineable, placeable common Earth rocks: limestone, slate, quartzite and gabbro.
Their broad, seeded provinces provide a stable local material identity that
future Living Cities architecture can query.

## Build and install

Use JDK 21. Run PowerShell from this directory:

    powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/bootstrap.ps1
    ./gradlew.bat build

Install build/libs/geologic-variation-0.2.2-dev.jar on BOTH client and server
alongside official Terrain Diffusion 2.3.0 (NeoForge, Minecraft 1.21.1).
The dependency is downloaded separately, SHA-512 verified, and never bundled.
The Windows artifact is the build baseline. Official matching NeoForge 1.21.1 CUDA/CPU variants share the common Java API.

No modpack, Living Cities, Terralith or Ulti-World installation is required.
Ulti-World integration is deferred. Fabric and other Minecraft versions are not
supported by this build.

Use a fresh disposable Terrain Diffusion Overworld for acceptance. Only newly
generated chunks change. Existing chunks and player builds are not migrated.
Keep this addon installed once its blocks are present in a save.

## Region behavior

Province sites are spaced approximately 2,048 blocks at scale 1 and 12,288 at
scale 6, with seed-based jitter. Their nearest-site boundaries are independent
of chunk traversal. Adjacent provinces can share a stone and form larger belts.
One aligned Terrain Diffusion tile around each province's anchor supplies 25
height samples. Mean elevation and local relief bias its palette:

| Terrain context | Preferred rock | Appearance placeholder |
| --- | --- | --- |
| Low, gentle terrain | Limestone | Pale calcite |
| Intermediate uplands | Slate | Dark gray deepslate |
| High or rugged terrain | Quartzite | Light diorite |
| Deep oceanic terrain, some uplands | Gabbro | Near-black polished blackstone |

This is a plausible artistic geology heuristic, not a tectonic reconstruction.
TD predicts terrain, not rock composition. The province layout is seeded;
the province material is conditioned by TD's generated terrain. Contacts are
sharp vertical boundaries without strata, folds, faults or contact blending.
Surface rules run first, then exact vanilla stone is replaced, before carvers
and features. Soil, sand, water, bedrock, deepslate and specialized Terralith
surface materials are preserved. Existing granite/diorite/andesite feature
patches can still appear within a province. Tag-based stone ores and carvers
recognize the new blocks; other mods using exact-block checks need adapters.

A bounded 512-province cache avoids repeated sampling. A first visit can request
an anchor tile beyond explored chunks and add inference latency. It does not
generate or load Minecraft chunks there. Concurrent misses use TD's request
deduplication. Do not call the region API from TD's own inference thread.

## Future city integration

On a server with initialized TD terrain, call:

    Geology.Region local = Geology.regionAt(blockX, blockZ);
    Provinces.Stone material = local.stone();

The result also supplies province cell coordinates, identity, anchor, elevation
and relief. Persist the province coordinates plus the palette in a city's
founding data so its architecture remains stable if the city expands.
The API is read-only but can block for inference. Living Cities is not a
runtime dependency, and automatic cultural/style assignment is not included.

## Assets and extensions

Each stone now has natural, cobbled, polished and brick blocks, each with stairs,
slabs and walls (64 blocks total). Craft or stonecut masonry, smelt cobbled rock
back to its natural form, and use regional cobblestone for ordinary tools and
furnaces. One-way conversions to vanilla stone/cobblestone cover exact-item
recipes. See [stone families and asset handoff](docs/stone-families.md).

The four original block IDs are geologic_variation:limestone, :slate, :quartzite and
:gabbro. All use vanilla textures temporarily, have block items, creative
entries, cobbled drops (natural blocks with Silk Touch), and stone mining properties. Replace the textures
referenced in assets/geologic_variation/models/block/*.json later, or override
them with a resource pack. IDs need not change when art is added.

The pure domain/Provinces.java owns region partition and classification;
Geology.java owns the standalone TD adapter; mixin/SurfaceMixin.java applies it.
Freeze seed, scale, model versions, tile size and these rules for a continuing
world. Altering them can create contacts at old/new chunk borders.
See docs/compatibility.md and docs/verification.md. Version 0.2.2 adds
[controlled geology errors](docs/failure-handling.md). Before updating an existing
save, read the [world upgrade and recovery guide](docs/world-upgrades.md).



## Project tracking

Repository: https://github.com/WilyJEB/geologic-variation
Milestones: https://github.com/WilyJEB/geologic-variation/milestones
Issues: https://github.com/WilyJEB/geologic-variation/issues

See docs/roadmap.md for milestone gates and docs/workflow.md for contribution
and validation expectations. Minimal standalone testing precedes optional pack
or city-mod integration.

## World settings

Province spacing and terrain classification thresholds can be set for new TD
worlds in `config/geologic_variation-common.toml`. Each world saves its own
settings and keeps them when the common config changes. Pre-settings worlds
are rejected unless they have verified schema-2 provenance. See [settings and persistence](docs/geology-settings.md)
for units, validation, snapshot location and remaining runtime acceptance.

## Researched next palette

The next versioned design has four regional stones per layer alongside vanilla,
plus a sourced library of future mineral-enrichment systems. This catalog does
not yet change the running four-rock generator. See
[geology research and implementation issues](docs/geology-research.md).
