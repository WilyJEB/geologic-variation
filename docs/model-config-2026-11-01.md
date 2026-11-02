# Supported TD model-config substitution, 2026-11-01

Three new dedicated JVM launches pass: matching original-input control, actual
custom model-config rejection, and exact original-input restoration/reopen.
This accepts a config-only portion of #9. No production regression was reproduced;
production code/JAR, geology-1, IDs, compatibility guards and generation stay fixed.

## Reconciliation and input selection

Local main and freshly fetched origin/main matched
`2b9d07a049a62129827446f7061e2a16deeb3223` (merged PR #40). GitHub #9 remains open.
PR #37's live seed/scale cached/uncached matrix, #38's hot common-config matrix,
and #39's official artifact matrix were read and reused as prior evidence only.
PR #40 selects the compatibility-focused contract; #5's original stronger failed
post-feature determinism assertion is unchanged and is not now a passing test.
No repository/ancestor AGENTS.md was present. Untracked `temp/` was preserved.

Inspected the actual pinned CPU JAR with `javap -p -c`, its embedded manifest,
and official tag source for ModelAssetManager, PipelineModels,
WorldPipelineModelConfig, WorldPipeline and TerrainDiffusionConfig. The manifest
pins [official model revision ad2df557](https://huggingface.co/xandergos/terrain-diffusion-30m-onnx/tree/ad2df557eca5645f588766101cf3bc3682455c3e).
Its [repository history](https://huggingface.co/xandergos/terrain-diffusion-30m-onnx/commits/main)
has one five-file upload and an initial revision containing only README and
`.gitattributes`. No official alternate asset revision exists in that history;
this is not an exhaustive search of third-party trained models.

TD's [official README](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/README.md)
explicitly documents custom models/config with `validate_model=false`.
[ModelAssetManager](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/common/src/main/java/com/github/xandergos/terraindiffusionmc/pipeline/ModelAssetManager.java)
resolves fixed filenames inside the game directory's `terrain-diffusion-models`;
with validation enabled it replaces hash-mismatched files with the pinned revision.
With validation disabled it accepts pre-existing custom assets.
[WorldPipelineModelConfig](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/common/src/main/java/com/github/xandergos/terraindiffusionmc/pipeline/WorldPipelineModelConfig.java)
parses and validates the actual JSON, including array lengths and positive grid
dimensions. WorldPipeline reads `residualMean()` into its decode constant and
applies `v * RESIDUAL_STD + RESIDUAL_MEAN` to residual output.

Selected an explicitly **test-derived custom config**, not an official alternate
trained model: replace only `"residual_mean": 0.0` with
`"residual_mean": 1.0` in the exact manifest-verified `world_pipeline_config.json`.
The byte derivation and JSON semantic diff are asserted. Model weights and the
other config remain official and unchanged. This is a real consumed numeric
parameter, not whitespace, metadata, corrupted JSON or an invented provenance.
The [selection record](evidence/model-config-selection-2026-11-01.json) retains
official history, source commit and raw source/API/bytecode inspection hashes.
Raw inspection files remain under ignored `runs/acceptance/model-config-inspection`.

## Matrix and observations

Runtime stays MC 1.21.1 / NeoForge 21.1.251 / Java 21.0.6 / Windows 11 amd64.
The official TD CPU JAR stays SHA-256
`3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`;
addon stays `39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.
TD config selects CPU and `validate_model=false` before control; that same file
and every mod/probe hash remain fixed across all three launches. This supported
TD switch does not weaken the addon's independent model hashing or save guard.

The runner clones only the verified
`runs/acceptance/context-startup-2026-11-01-02/baseline/world` into a NEW case.
It detaches the writable JSON hardlink before writing any bytes. Other model
assets stay immutable. Every original manifest asset hash is checked before the
matrix and after it; the full source fixture file manifest also matches afterward.
The source fixture is never launched. No user saves or installed profiles change.

| Launch | Loaded residual mean | Result |
| --- | --- | --- |
| Original control | 0.0 | Ready, matching settings/context, actual geology and existing full sample; save/stop |
| Custom config | 1.0 | TD native CPU/model initialization succeeds; geology rejects before Ready/RCON; shutdown completes |
| Exact original restoration | 0.0 | Ready, matching settings/context/geology/blocks/snapshot/terrain; save/stop |

A passive test-only static-initializer tail injection logs the value after TD's
real parser/validator returns. It performs no inference or config mutation.
The rejection log records models loaded, CPU provider resolution, then the actual
geology diagnostic and restoration guidance. All seven saved/runtime context
fields are parsed and compared: **only `models` differs**:

- Saved/restored model/config aggregate:
  `64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`.
- Alternate actual aggregate:
  `2dcd21cae1c683ad268a35449d79cce6ec87d1ab8d010a1f1d1a4290050ed50e`.
- Fixed: geology-1, seed -1550453200536840819, scale 1, tile 256, official CPU
  dependency and resolved `CPU/Windows 11/amd64` backend.

The aggregate is independently calculated from sorted manifest asset names and
their real file hashes, matching production. All 14 snapshot fields (schema,
seven context fields and six settings) are parsed. Original/restored active and
requested settings match. The existing chunk (-32,-65) retains 15,597 slate blocks
and complete-block SHA-256
`09163724065ec1385a0c43dcdc739a3673b63c596ade17041a46fb8f20383a00`;
actual geology at (-508,-1027) matches. No neighboring generation is requested.
The rejection log contains no addon-anchor heightmap request; the guarantee here
is startup guard rejection and no persisted incompatible terrain, not a new
instrumented concurrent-inference test. Coarse provider resolution is TD's normal
public route from the server thread, never called from its inference thread.

Snapshot SHA-256 stays
`c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d`.
All 529 persisted Overworld records preserve exact coverage, status and section
block containers after rejection and restored reopen: 1 full, 8 initialize-light,
16 carvers, 24 biomes, 480 structure-starts. All nine region files are additionally
byte-identical through rejection. Reopen changes region metadata hashes, retained
separately; lighting/ticks/timestamps are excluded from block-container assertions.
Ordinary ticks are frozen, random ticks/spawning disabled, spawn radius zero.

All three JVMs exit with code 0. Post-run OS inspection finds no Java/Python test
processes or game/RCON listeners. At least 2 GiB free is required before every
launch; about 4.7 GiB remains afterward. Only stopped disposable-case ONNX caches
are removed, after resolved-path containment checks. Startup is bounded to 360 s,
commands to 300 s, normal exit to 90 s and final forced cleanup to 30 s. These are
harness bounds, not a native inference watchdog or performance acceptance.

## Reproduction, checks and limits

After the [pinned runtime preparation](runtime-acceptance-tools.md):

```powershell
gradlew.bat build runtimeProbeJar
python scripts/verify-model-config.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --fixture runs/acceptance/context-startup-2026-11-01-02/baseline/world `
  --output runs/acceptance/new-model-config
python scripts/summarize-model-config.py runs/acceptance/new-model-config `
  --output docs/evidence/model-config-2026-11-01.json
```

Accepted raw saves/logs/crash report/results remain ignored under
`runs/acceptance/model-config-2026-11-01-01`. The [portable runtime evidence](evidence/model-config-2026-11-01.json)
rechecks all raw log hashes, loaded values, contexts, retained inputs and decoded
terrain. The first runtime matrix attempt passed; no unsuccessful runtime attempt
is included. Failed preliminary source-URL/network lookups produced no acceptance
and changed no inputs. Build/domain suites, probe compilation, 64-block/158-recipe/
711-resource validation, catalog, Python syntax and evidence export pass.
CI validates build/resources/syntax; it does not run this inference matrix.

This certifies a supported custom **config-only** substitution. Different trained
weights, resolved backend/hardware changes, generator upgrades, integrated-client
presentation and same-process lifecycle recovery remain #9 gates. It does not
certify the alternate config's full decoder output or terrain quality: generation
must be rejected in this continuing save. No production fix was justified.
Ulti-World stays optional. #11's unchanged 14.383-second cold-route opportunity
and #5's original failed stronger assertion remain separate.
Next concrete step: select and independently initialize a provenance-verifiable
alternate trained-weight set or resolved backend, then run another isolated
rejection/restoration matrix; if unavailable, record that gate as blocked.
