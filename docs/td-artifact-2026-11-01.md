# Actual TD artifact substitution, 2026-11-01

One independent dedicated startup artifact rejection and exact restoration/reopen
passes in three JVM launches. Production code and the addon JAR are unchanged.
This accepts the artifact-only startup portion of #9; the issue remains open.

## Selection and isolation

Reconciled local/origin main at merged PR #38,
`236ee9420ae0df923792107266be600963964e79`, its successful CI and open #9.
The earlier startup, live-context and actual hot-reload reports remain separate
evidence. Runtime is MC 1.21.1 / NeoForge 21.1.251 / FML 4.0.44 / Java 21.0.6 /
Windows 11 amd64, using the retained standalone CPU environment.

The [official release](https://github.com/xandergos/terrain-diffusion-mc/releases/tag/2.3.0-preview)
offers CPU, CUDA and Windows variants for NeoForge 1.21.1. Earlier 2.2 artifacts
are Fabric builds; other loader/MC targets do not isolate this environment.
Selected the unmodified official `NeoForge-terrain-diffusion-mc-2.3.0-cuda+1.21.1.jar`:

- Original CPU SHA-256: `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`.
- Alternate CUDA SHA-256: `97ff25936fdf79b9cabbf8b68dc5d02fd15938437e08069c4005619f695161ad`.
- Both match GitHub release API asset digests. Alternate download size: 547,142,899 bytes.
- All 58 TD class files and `model-assets-manifest.json` are byte-identical.
  `javap` confirms required OnnxModel, LocalTerrainProvider and WorldScaleManager APIs.
- The actual differences include build-variant metadata and the bundled ONNX
  runtime: `onnxruntime_gpu` versus `onnxruntime`, both 1.20.0. This is a real
  official distribution substitution, not a repacked hash-only JAR.
- Before the control launch, only the NEW disposable case's TD config selects
  `inference.device=cpu`. This identical file stays fixed across all three launches.
  The retained source config requests GPU (ignored by the CPU distribution).
  Source/API inspection confirms the CUDA distribution honors explicit CPU;
  the runtime diagnostic independently confirms CPU resolution. No CUDA inference
  or CUDA hardware support is certified here.

TerrainGenerationContext.capture awaits model loading/provider resolution,
hashes the actual loaded TD file, and independently hashes every manifest model/
config asset. SettingsStore compares the complete saved context before returning
active settings. GenerationContext requires exact equality. The diagnostic therefore
tests the actual artifact guard after loader and native CPU initialization succeed.

## Results and preservation

The runner clones only the verified saved-terrain fixture
`runs/acceptance/context-startup-2026-11-01-02/baseline/world` into a NEW case.
The source is never launched or modified; its complete file manifest matches afterward.
The saved snapshot is never edited. Baseline settings/context, real region at
(-508,-1027), and existing full chunk (-32,-65) match after reopening.
That chunk contains 15,597 slate blocks and complete block SHA-256
`09163724065ec1385a0c43dcdc739a3673b63c596ade17041a46fb8f20383a00`.

The substituted process reports the intended incompatible-generation-context
diagnostic, restoration guidance and normal server shutdown before Ready/RCON.
All seven saved/runtime fields are parsed; only `dependency` differs. Generator
geology-1, seed -1550453200536840819, scale 1, tile 256, model/config aggregate
`64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`
and backend `CPU/Windows 11/amd64` match. This is not a loader/dependency failure.

Snapshot SHA-256 remains
`c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d`.
All nine region files are byte-identical through rejection. Separately, all 529
persisted Overworld chunk records retain exact coverage, status and section
block-state containers through rejection and restored reopen: one full,
8 initialize-light, 16 carvers, 24 biomes, 480 structure-starts records.
Region metadata hashes are retained separately; light/ticks/timestamps are excluded
from block-container assertions. Ordinary ticks are frozen, random ticks/spawning
disabled, spawn radius zero. Only the existing sample chunk is requested; geology
queries do not request Minecraft chunks. No neighboring generation is requested.

Only the linked TD file is substituted between stopped launches. Original config,
addon/probe and model inputs remain fixed. Exact original runtime file hashes are
required before reopening. Both successful launches save/stop with exit code 0;
the rejected process also exits. All test processes are confirmed stopped.

## Reproduction and limits

After the [runtime preparation](runtime-acceptance-tools.md):

```powershell
gradlew.bat build runtimeProbeJar
python scripts/verify-td-artifact.py --java 'C:/path/to/java.exe' `
  --td 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cpu+1.21.1.jar' `
  --alternate 'C:/path/to/NeoForge-terrain-diffusion-mc-2.3.0-cuda+1.21.1.jar' `
  --fixture runs/acceptance/context-startup-2026-11-01-02/baseline/world `
  --output runs/acceptance/new-td-artifact
python scripts/summarize-td-artifact.py runs/acceptance/new-td-artifact `
  --output docs/evidence/td-artifact-2026-11-01.json
```

Raw logs/crash report/results remain under ignored
`runs/acceptance/td-artifact-2026-11-01-02`; [portable evidence](evidence/td-artifact-2026-11-01.json)
rechecks raw log hashes, full diagnostic fields, immutable inputs and preservation.
Attempt -01 failed at a sandbox-denied hardlink before launch and supplies no runtime
acceptance. No unrelated `temp/` material was changed.

At least 2 GiB free is required before each launch. Approximately 1.1 GB of transient
ONNX optimizations is removed only inside the stopped disposable case. Startup is
bounded to 360 seconds, RCON commands to 300 seconds, normal exit to 90 seconds and
forced process cleanup to 30 seconds. These bounds are not inference performance
thresholds or a native inference watchdog.

Build/domain suites, opt-in probe compilation, resource validation (64 blocks /
158 recipes / 711 JSON resources), catalog validation, Python syntax and evidence
export pass. CI checks build/resources/syntax; it does not execute this runtime matrix.
No production regression was reproduced. Addon SHA-256 remains
`39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226`.

#9 remains open for actual model/config and resolved-backend substitutions,
generator upgrades and integrated-client/same-process lifecycle gates. This small
scale-1 dedicated case does not certify changed TD algorithms, CUDA inference,
other hardware, unknown legacy migration or concurrent changes during inference.
Next concrete step: independently substitute a provenance-verifiable model/config
input that successfully initializes, require its exact context difference, then
restore and reopen another fresh fixture copy. Ulti-World stays optional; geology-1,
IDs and provenance guards are unchanged. #5's original failed strict determinism
assertion and #11's unchanged 14.383-second cold-route opportunity are preserved.
