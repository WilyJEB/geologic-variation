# Compatibility contract

Standalone baseline, revised 2026-10-18:

- Minecraft 1.21.1, NeoForge 21.1.251, Java 21, Gradle 9.2.1.
- Official xandergos/terrain-diffusion-mc release 2.3.0-preview, declared
  NeoForge mod ID terrain_diffusion_mc, version 2.3.0.
- Source tag: 8acd2b680ee248334637f8cf13f6c78ac20003da.
- Official release:
  https://github.com/xandergos/terrain-diffusion-mc/releases/tag/2.3.0-preview
- Bootstrap pins the official NeoForge Windows +1.21.1 artifact by SHA-512.
- The official 2.3.0 NeoForge CPU/CUDA variants share the declared version and
  common Java API; native backend execution has not been tested here.
- No Ulti-World, Living Cities, Terralith or pack-owned fork dependency.
- Fabric, Forge, Minecraft 1.21.11 and arbitrary TD forks are not certified.
- Ulti-World's terra_diffusion_compat fork is deliberately outside this
  standalone build's dependency contract. A future adapter can support it.

Core integration uses LocalTerrainProvider.getSeed/getInstance/fetchHeightmap,
HeightmapData.heightmap/width/height, TerrainDiffusionConfig.tileSize and
WorldScaleManager.getCurrentScale. These exist in the official release.
Heightmap bounds are Z then X, end-exclusive. SurfaceMixin injects one exact
NoiseBasedChunkGenerator.buildSurface descriptor at RETURN, gated to a TD
Overworld. This hook is independent of any pack configuration.

Cache includes seed/scale/settings and clears at server stop. Schema-2 snapshots
pin generation rules, TD artifact/model hashes, seed/scale/tile and backend context;
incompatible or unverified continuing saves are rejected (see geology-settings.md).
The provider is global in TD; multiple
independent simultaneous servers in one JVM are outside this contract.

Both client and server require the addon for block registration. No models,
native DLLs or dependency binaries are bundled in the addon JAR.
