# Trained-weight/backend gate feasibility, 2026-11-01

**Blocked; no new save-safety acceptance.** The official CUDA and Windows
distributions cannot initialize a GPU model session in this environment. The
official model catalog supplies no second directly loadable ONNX weight set.
Issue #9 remains open. No production regression was reproduced or production
code changed. No Minecraft world was launched, substituted, edited or restored
in this slice; a passing rejection/restoration matrix is not claimed.

## Reconciliation and reused evidence

Freshly fetched local/origin main both matched merged PR #41,
`d234016b3790daf059e430ca0924349727e0b633`. GitHub #9 is open; PR #41 merged with
[passing CI](https://github.com/WilyJEB/geologic-variation/actions/runs/41402359533).
No repository/ancestor AGENTS.md was present. Untracked `temp/` remains untouched.
The startup, live-context, hot-config, artifact and model-config reports, evidence,
runners/summarizers, save-contract/failure docs and production/probe APIs were
inspected. PRs #37–#39 and #41 are reused prior evidence, not rerun or expanded:
CUDA packaging with CPU selected is artifact-only coverage; residual_mean 0→1
is config-only coverage. Neither demonstrates different weights or backend.

## Official inputs and supported mechanisms

The [official release API](https://api.github.com/repos/xandergos/terrain-diffusion-mc/releases/tags/2.3.0-preview)
provides NeoForge 1.21.1 CPU, CUDA and Windows variants. The three retained files
match its SHA-256 digests:

| Variant | SHA-256 |
| --- | --- |
| CPU | `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8` |
| CUDA | `97ff25936fdf79b9cabbf8b68dc5d02fd15938437e08069c4005619f695161ad` |
| Windows | `64422a53d395666ed0774a8904823b7c96688b5ce82a0026326c3e823f7e99dd` |

All 58 TD classes and the model manifest match across these artifacts. Native
runtimes differ: CPU ONNX Runtime 1.20.0, CUDA onnxruntime_gpu 1.20.0, and the
Windows custom onnxruntime-dml-1.0.jar. Embedded Windows DLLs are actual x64 PE
files (machine 0x8664); hashes and sizes are retained in the evidence. No native
libraries were replaced, patched or downloaded from an unofficial source.

Inspected official tag `2.3.0-preview`, source commit
`8acd2b680ee248334637f8cf13f6c78ac20003da`, and actual pinned OnnxModel bytecode.
[TerrainDiffusionConfig](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/common/src/main/java/com/github/xandergos/terraindiffusionmc/config/TerrainDiffusionConfig.java)
supports inference.device=cpu/gpu/auto; CPU packaging forces auto, and on Windows
has no dedicated GPU provider. [OnnxModel](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/common/src/main/java/com/github/xandergos/terraindiffusionmc/pipeline/OnnxModel.java)
tries CUDA, DirectML, then CoreML; gpu requires a provider, while auto may fall
back to CPU. With offload enabled, session/provider resolution is lazy. Merely
seeing a GPU request, an available-provider list or a provider-selection log
does not establish a working session/inference route.

A real Windows GPU change therefore requires an official distribution change
as well as supported device selection. A future matrix must require exactly
**dependency and backend** context differences; generator, seed, scale, tile and
model/config aggregate must stay fixed. Changing CPU packaging alone is already
covered. Production capture waits for real models/provider resolution, hashes
the loaded artifact and manifest assets, then compares all seven context fields
before adopting settings. Its public coarse resolution route runs from the
server thread; never call it from TD's inference thread.

The [official ONNX repository](https://huggingface.co/xandergos/terrain-diffusion-30m-onnx/tree/ad2df557eca5645f588766101cf3bc3682455c3e)
still has one uploaded five-asset revision, `ad2df557eca5645f588766101cf3bc3682455c3e`;
its other historical revision has only README/.gitattributes, as established in
PR #41. Fresh history/current-revision checks agree. Fresh inspection of all eight
repositories in the [official author's catalog](https://huggingface.co/xandergos/models),
including recursive 30m/90m/90m-pool2 listings, finds:

- The single ONNX repository contains coarse/base/decoder .onnx plus pipeline
  data and world config, matching the pinned manifest and all five shared hashes.
- 30m, 90m and 90m-pool2 contain PyTorch Safetensors weights/configs in subfolders.
- The older coarse/base/decoder repositories and autoencoder also contain
  Safetensors/configs, without ready-to-load .onnx assets.

[PipelineModels](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/common/src/main/java/com/github/xandergos/terraindiffusionmc/pipeline/PipelineModels.java)
loads fixed coarse_model.onnx, base_model.onnx and decoder_model.onnx filenames;
ModelAssetManager resolves them in terrain-diffusion-models. The documented
validate_model=false supports custom pre-existing assets, but it does not convert
Safetensors into the required graphs, tensor names/shapes and pipeline data.
No renamed weights, corrupt assets, numeric JSON edit or invented identity was
used. This is an official-catalog search, not proof that no compatible third-party
model or independently verified export could exist.

## New native feasibility evidence

Three bounded JVM preflights use Java 21.0.6 / Windows 11 amd64 and the untouched
manifest-verified coarse model. This is direct initialization through each
distribution's embedded ONNX Java/native API, not TD/Minecraft initialization or
terrain generation. The CUDA options match TD's arena, cuDNN search and stream
options; DirectML uses its supported device-0 API. No fallback is accepted.

Hardware query: **NVIDIA GeForce RTX 5080, driver 610.88, 16,303 MiB**. Hardware
support alone is insufficient. Native tests were also run outside the restricted
process environment; failures persisted.

| Preflight | Actual result | Interpretation |
| --- | --- | --- |
| Official CPU | Native environment initializes; official coarse model session creates and closes; exit 0 | Positive native/model control, no new gameplay acceptance |
| Official CUDA | Native environment enumerates CPU/CUDA/TensorRT; addCUDA fails with LoadLibrary error 126 for onnxruntime_providers_cuda.dll; exit 1 | No CUDA provider added or model session created |
| Official Windows/DirectML | UnsatisfiedLinkError: onnxruntime.dll DLL initialization routine failed; exit 1 | Native environment fails before provider addition/model session |

Explicit search of the inherited executable search directories finds none of
cudart64_12.dll, cublas64_12.dll or cudnn64_9.dll. This is a PATH observation, not
an exhaustive disk search or proof of the precise missing transitive dependency.
The official [CUDA setup guide](https://github.com/xandergos/terrain-diffusion-mc/blob/2.3.0-preview/CUDA_INSTALL.md)
requires CUDA 12.x and cuDNN 9.x, correctly visible to the launching process.
No system toolkit/driver installation or PATH modification was attempted.
DirectML's specific DLL-initialization root cause remains undiagnosed; x64 PE
headers rule out only a simple architecture-label mismatch. Do not infer a
geology guard result from either native failure.

The [portable evidence](evidence/backend-feasibility-2026-11-01.json) rechecks raw
logs, compiler logs, extracted runtime hashes, release digests, source pins and
official model listings. Raw inputs/logs stay ignored under
`runs/acceptance/backend-inspection` and
`runs/acceptance/backend-feasibility-2026-11-01-02`.
Preliminary native attempts/logs and run -01 remain retained. Run -01's DLL PATH
check used executable-oriented lookup; run -02 corrects that to explicit file
checks. Only -02 supplies the final preflight observations. Neither run is a
successful save-safety matrix.

Each native launch requires at least 2 GiB free, compilation is bounded to 30 s,
hardware query to 15 s, native processes to 120 s and forced exit to 30 s. All
three final JVMs exit, with no timeout. About 3.6 GiB free remains. No inference
optimization cache was generated or cleaned by this slice; extracted runtimes
and logs remain preserved. No game/RCON listener is started. The source fixture's
complete file manifest and all shared model/artifact hashes match before/after.
The original addon remains SHA-256
`39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.

## Reproduction and checks

```powershell
python scripts/inspect-backend-feasibility.py `
  --java 'C:/path/to/jdk-21/bin/java.exe' `
  --cpu 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --cuda 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cuda+1.21.1.jar' `
  --directml libs/terrain-diffusion-standalone.jar `
  --models runs/server/terrain-diffusion-models `
  --fixture runs/acceptance/context-startup-2026-11-01-02/baseline/world `
  --output runs/acceptance/new-backend-feasibility
python scripts/summarize-backend-feasibility.py runs/acceptance/new-backend-feasibility `
  --inspection runs/acceptance/backend-inspection `
  --output docs/evidence/backend-feasibility-2026-11-01.json
```

The inspection directory contains the linked release API JSON, source-tag JSON,
OnnxModel/PipelineModels source, CUDA_INSTALL.md, OnnxModel bytecode, official
author catalog, repository tree JSON and ONNX history/current model API JSON;
individual raw hashes are in the evidence. Refresh them from the linked official
sources if reproducing later. The exporter intentionally fails if history,
artifacts or backend feasibility changes; a usable alternate must proceed to
the real save-safety matrix instead of exporting this blocked decision.

Build/domain suites and runtimeProbeJar pass. Packaged resource checks pass
(64 blocks / 158 recipes / 711 JSON); catalog and Python syntax checks pass.
CI checks build/resources/syntax, not GPU initialization or save safety.

## Remaining gate and concrete unblock

First provide a working CUDA 12.x/cuDNN 9.x runtime visible to this Java process,
or resolve the official Windows native initialization failure. Rerun native
preflight, then independently prove real TD pipeline initialization and resolved
GPU execution. Alternatively provide a provenance-pinned compatible alternate
ONNX weight set with verified graph/pipeline compatibility; an independently
validated export of official alternate weights could qualify.

Then run control → alternate rejection → exact original restoration/reopen in a
NEW copy of the known-provenance saved-terrain fixture. Require all saved/runtime
context fields, geology/settings, complete sample blocks, snapshot bytes, and
decoded persisted coverage/status/block containers, with region hashes separate.
Detach writable assets, keep geology-1/seed/scale/tile/addon and unrelated inputs
fixed, require models/native initialization before the guard and before Ready or
incompatible generation, and require bounded completed shutdown and unchanged
original fixture/shared inputs. Do not edit the saved snapshot to enable this.

#9 stays open for trained-weight/resolved-backend substitutions, generator
upgrades and integrated-client/same-process lifecycle gates. Ulti-World stays
optional; IDs, generation and strict provenance guards stay unchanged. #5's
original stronger failed determinism assertion remains failed despite its
documented contract decision. #11's unchanged 14.383-second cold-route overhead
remains later optimization work.
