# Eight-rock palette, geological history and regional mineral systems

Research date: 2026-10-18; palette revised 2026-10-19. This is a sourced design/library deliverable, not a
runtime palette switch. Implementation is tracked in #22 (layers/materials),
#11 (terrane mapping), #23 (mineral systems), #12 (art) and #9 (world versioning).
The previous four-rock prototype remains the running generator.

## Selected palette

The revised surface palette has light limestone, charcoal slate, gray-green
phyllite and dark-brown ironstone. The phyllite selection supersedes the earlier
second-dark-gray greywacke slot. Deep varieties retain dark bases with distinct mineral accents.
Swatches in the catalog are art targets, not measured colors or a claim that all
specimens have the same appearance.

| Host layer | Rock | Art direction | Geological rationale |
| --- | --- | --- | --- |
| Surface | Limestone | Cream, ivory, warm buff | Carbonate-platform/basin sediment, potentially uplifted later |
| Surface | Slate | Charcoal gray, fine cleavage | Low-grade metamorphism of mud-rich sediment |
| Surface | Phyllite | Gray-green with silver/sage highlights and wavy foliation | Fine-grained metamorphic rock with silky cleavage |
| Surface | Ironstone | Dark umber with rust/ochre detail | Iron-bearing sedimentary horizons |
| Deep | Gabbro | Blue-black with subdued feldspar grains | Mafic intrusive domains, including oceanic crust and continental intrusions |
| Deep | Blueschist | Navy with blue-gray foliation | High-pressure, relatively cool subduction metamorphism |
| Deep | Serpentinite | Dark olive/forest green, pale veins | Hydrated ultramafic parent rock |
| Deep | Minette | Near-black reddish brown with sparse mica flecks | Narrow steep/vertical intrusive dikes |

BGS documents [green-gray phyllite](https://earthwise.bgs.ac.uk/index.php/Fraochaidh_prograde_sequence,_Ballachulish_Igneous_Complex_-_an_excursion)
and [brown ironstone](https://webapps.bgs.ac.uk/lexicon/lexicon.cfm?pub=RDLI).
USGS describes the [silky cleavage of phyllite](https://ngmdb.usgs.gov/Info/standards/datamodel/model41.pdf).
For minette, [BGS mica lamprophyres](https://webapps.bgs.ac.uk/Memoirs/docs/B07321.html)
include reddish-brown matrices and brown mica; [USGS minette-province examples](https://pubs.usgs.gov/pp/0521d/report.pdf)
include vertical dikes. The chosen near-black red-brown texture is an art target
within that geological direction, not a universal specimen color.
[The rock catalog](../planning/geology/rock-catalog.json) links every entry to
its evidence and describes its texture. Distinguish planar slate from wavy,
silky-looking phyllite; actual reflective shader support is not required.

## Metamorphism is a history, not a vertical paint gradient

Temperature, pressure, fluids and parent composition all matter. Mudstone can
become slate and, under appropriate further metamorphism, schist/gneiss.
Quartz-rich sandstone can become quartzite; limestone can become marble.
Mafic rocks can develop different metamorphic assemblages depending on their
pressure-temperature path. Blueschist and eclogite are useful high-pressure
associations, while serpentinite specifically requires hydration of ultramafic
material. These are not an inevitable single ladder that every rock follows.
See [BGS rock processes](https://www.bgs.ac.uk/discovering-geology/rocks-and-minerals/),
[USGS metamorphism](https://pubs.usgs.gov/gip/collect1/collectgip.html), and
[USGS high-pressure rock assemblages](https://www.usgs.gov/publications/garnet-types-cazadero-area-california).

Erosion and uplift expose rocks that formed at depth. The two Minecraft layers
therefore describe host replacement, not real crustal depths or a claim that a
mountain's current height reveals its rock's origin. Surface rocks can occur
underwater and formerly marine rocks can occur in mountains. The new classifier
should model inherited geological history in coherent terranes.

## Runtime framework contract for #22

Each region needs independent surface and deep background selections sharing one
terrane identity, plus a structural dike pass for minette. Each layer includes vanilla plus four regional material types. Minette occupies
its deep slot as intrusive sheets rather than a blanket background province. Retain a
nonzero configurable share of vanilla stone/deepslate regions; the present
blanket stone replacement is not the target design.

Use existing vanilla host identity to choose the layer: replace only natural
stone or natural deepslate as appropriate, retaining TD's transition rather than
adding a guessed fixed-Y boundary. Keep bedrock, soil, sand, water, placed blocks
and existing ore blocks outside that substitution.

Use central material presets copied from `Blocks.STONE` and `Blocks.DEEPSLATE`
for the respective families, including hardness, resistance, tools and sound.
Shape classes still supply geometry and waterlogging, and forms retain their
own drops/recipes. These game properties deliberately do not follow real Mohs
hardness. In particular, surface cobble should not accidentally inherit the
harder cobblestone preset when the chosen contract is stone-like behavior.

Each active rock has four finishes and four forms, yielding 128 active block
forms and 32 shared textures. Preserve the existing quartzite family as a
legacy registered material outside the new eight-rock generation palette;
retaining its 16 forms gives 144 registered forms. Its optional four legacy
textures are separate from the 32 active textures. No shipped ID is deleted.

Gabbro's new-layer assignment requires two distinct upgrade decisions. Keep the
old generator's surface distribution for continuing worlds under #9. Also note
that changing the shared block's physical preset affects already placed gabbro
in every world: explicitly document that material change before release, or use
a distinct deep ID if old physical behavior must be preserved. Generator
versioning alone cannot give one block ID two different material presets.

## Minette occurrence contract

Minette is the selected short registry name (`minette`), referring to the
igneous mica-lamprophyre rock, not the iron-ore use of the same word.
Generate narrow steep-to-vertical sheets along seeded intrusion/fracture
corridors. Let them cut across eligible natural deep background rocks rather
than track horizontal height bands or fill whole provinces. Finite thickness,
height and along-strike extent should be bounded game controls.

Dike identity/orientation must be defined in global coordinates so neighboring
chunks agree, including negative coordinates and reversed exploration. The
placement pass must preserve ore blocks, bedrock, fluids and player construction.
The material retains the deep deepslate preset and complete masonry family.
The catalog records the geometry now; no runtime dike generator is implemented.

## Which Terrain Diffusion layer to use

Use the **learned coarse elevation stage**, rather than per-block biome noise,
as the primary landmass signal. The inspected source is pinned to
[8acd2b680ee248334637f8cf13f6c78ac20003da](https://github.com/xandergos/terrain-diffusion-mc/tree/8acd2b680ee248334637f8cf13f6c78ac20003da).
The compiled official 2.3.0 NeoForge 1.21.1 JAR also exposes the required
`LocalTerrainProvider.getPipelineCoarse(int,int,int,int)` method, confirmed with
JDK 21 `javap`. No model inference was run for this research.

The source contract provides a `[7,H,W]` FloatTensor. Channels 0..5 are weighted
signals; channel 6 is blend weight. Explorer labels the signals elevation, p5,
temperature, temperature seasonality, precipitation and precipitation variability.
Decode exactly as
[ExplorerServer.coarseChannel](https://github.com/xandergos/terrain-diffusion-mc/blob/8acd2b680ee248334637f8cf13f6c78ac20003da/common/src/main/java/com/github/xandergos/terraindiffusionmc/explorer/ExplorerServer.java):

1. Divide each signal by its pixel's positive finite blend weight.
2. Decode channels 0 and 1 using `sign(value) * value * value`.
3. Treat missing/zero/non-finite weight as unavailable evidence, not ocean.
4. Use row = z and column = x. At the pinned contract, coarse index units span
   256 native pixels, or `256 * worldScale` Minecraft blocks. Use floor division
   for negative coordinates, never truncation toward zero.

The shipped native resolution is described as 30 m/pixel; one coarse index
therefore corresponds to about 7.68 km of modeled terrain and 256..1536 game
blocks at scale 1..6. Read and validate model metadata rather than assuming
this conversion for every future model. Validate p5's training definition and
pooling mode before interpreting it as a calibrated relief percentile.
A broad elevation neighborhood already supplies a separate relief proxy.

[LocalTerrainProvider](https://github.com/xandergos/terrain-diffusion-mc/blob/8acd2b680ee248334637f8cf13f6c78ac20003da/common/src/main/java/com/github/xandergos/terraindiffusionmc/pipeline/LocalTerrainProvider.java)
serializes these calls onto TD's inference thread. Do not invoke its blocking
accessors from that thread. A coarse request can still trigger a model window:
this is not a free lookup or a performance certification.

There is **no plate ID, crustal age, fault, pressure, rock or ore output** in the
inspected coarse contract. The synthetic conditioning factory generates climate/
elevation statistics, not a plate simulation. Our tectonic-like map must be an
inference that combines terrain morphology with a deterministic seeded history.
Current relief cannot uniquely recover geology; report confidence and reasons.

Proposed pipeline for #11:

- Sample bounded coarse neighborhoods on a fixed global grid; derive ocean/land
  tendency, coast proximity, broad basins and elongated relief belts.
- Combine those observations with correlated seeded history to propose basin/
  platform, fold/accretionary, mafic intrusive/oceanic and high-pressure/ultramafic
  terranes. These are synthetic hypotheses, not observed plates.
- Select layer palettes from the shared terrane with separate seeded draws;
  avoid independent per-block noise and equal-area rare high-pressure rocks.
- Refine exposure/contacts with limited fine elevation sampling. Climate may
  inform weathering only after distinguishing modern climate from ancient history.
- Give the future mineralizer terrane, lithology, contacts and structural proxies,
  not only a current height or biome. Bound all halos/caches and preserve seed,
  scale, model, catalog and generator versions across saves.

Export terrain-evidence, terrane and layer-material maps for visual evaluation.
Test opposite exploration orders, negative coordinates, coarse/province/chunk
boundaries and scales 1/6. Benchmark cold and cached requests before replacing
the prototype's existing 25-sample anchor inference. No realistic map or cost
measurement is claimed until those experiments are performed.

## Mineral enrichment library

[Eleven mineral-system profiles](../planning/geology/mineral-systems.json) now
record host rocks, representative minerals, target elements, enrichment process,
context, candidate geometry, limitations and source IDs. They cover ironstone,
banded iron formation, mafic sulfides, chromitite, porphyry copper, MVT lead-zinc,
skarn, sediment-hosted copper, LCT pegmatite, bauxite and phosphorite.

Bulk major-element abundance, a permissive host, and ore enrichment are separate
concepts. A green ultramafic rock is not automatically nickel ore. Ironstone used
as a building block must not grant unrestricted iron without a separate enriched
state and yield budget. Eclogite's garnet grains do not imply diamonds or redstone.
Unsupported elements remain metadata rather than new mandatory ore mods.

The library intentionally has no numeric grades or universal ppm claims. Large
concentrations can be beds, lenses, pods, contact replacements or stockworks as
well as veins. Future #23 must choose bounded game grades/footprints, maintain
canonical deposits across chunk borders, and budget coexistence with vanilla ores.

Representative primary models: [USGS mafic/ultramafic systems](https://pubs.usgs.gov/pp/2005/1654/pdf/P1654.pdf),
[porphyry copper](https://www.usgs.gov/publications/porphyry-copper-deposit-model),
[MVT Pb-Zn](https://pubs.usgs.gov/sir/2010/5070/a/),
[skarn](https://pubs.usgs.gov/bul/1878/report.pdf),
and [LCT pegmatites](https://www.usgs.gov/publications/mineral-deposit-model-lithium-cesium-tantalum-pegmatites).
The [source register](../planning/geology/sources.json) supplies all 24 primary
references and explicitly distinguishes full page access from indexed excerpts.
No report text, photographs or texture artwork are copied.

## Delivery and implementation order

The catalog/library and issue definitions are delivered now. No Java registration,
block properties, generation rules, existing snapshots, recipes or texture files
are changed by this research branch. Implement #9, then #11/#22, then validate
#12/#14 and proceed to #23. The exact generation algorithm and ore yields still
need implementation and evidence; the saved catalog is not an executable mod.

Run `python scripts/check-geology-library.py` to check palette cardinality,
material presets, family counts, source references and mineral profile structure.
