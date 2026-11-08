# client-map-1: exact retained panel, no TD

Base: merged PR60 bdd71fd; fetched main matches. Existing untracked viewer repair
HTML and Python plus unrelated temp/ are preserved. Push this contract AND launcher
before implementing the isolated mod or starting any client. No TD run authorized.

Use a separate Gradle project with NeoForge21.1.251/Minecraft1.21.1 only. Compile
the existing RetainedMap.java and RetainedMapScreen.java directly, never the main
or runtimeProbe source set. Separate mod ID/config with only diagnostic mixins.
No production mod, TD, ONNX/model/provider classes, model files or production
mixins may enter the mod directory, classpath or module path. Launcher validates
installed profile manifest SHA1s, scans all supplied JAR entries (including nested
JARs), records SHA256s, rejects TD/ONNX and unexpected diagnostic class entries.
Installed profile manifest SHA256 is
706a7b7be2f110a87449f0ea090b6daf3882106f0d39acbe2c18b8a37d254924.
No inherited JVM injection variables, extra mods, account credentials or profile
settings. Only installed vanilla/NeoForge libraries/assets are reused read-only.

Title initialization is replaced with only retained-map entry and quit. A required
diagnostic mixin rejects LevelStorageSource world access before opening/creating
a save. A required Minecraft mixin rejects non-null setLevel and integrated-server
startup before launch. No multiplayer or world-entry UI, quickplay or arguments.
Absent TD executable bytes structurally exclude TD initialization/inference/query;
world barriers supplement that exclusion. Do not weaken any production guard.
Vanilla client startup can load registries and render its title panorama: this is
not a terrain observation. Never equate a quiet log with structural exclusion.

Reuse exact Windows bytes from PR60 (SHA256):
* RetainedMap.java 59573cb79b24c1c1526018a237cfa0d3331f9fdc59311b0afbea7c6f54b69407
* RetainedMapScreen.java e2e674602aea6004144fa18a0f30bc365475757b88cea388d378db7ca52bb3d2
* retained-map.tsv ab7168c07af32e981601d2e2fecb7a8457ec3607e68e2dec0731a6c86a67b872
* td-retained-map.zip fafa93f9a8a4865e2e2592cce3a54a1f5937822a059f23a3dfbec31981e9e05a

The TSV is immutable: 2401 sites, seven histories, 298 segments. No construction,
contact, ID, coordinate, token or history changes. If necessary repair only the
diagnostic adapter, retain original source and document exact executed bytes.
Keep old portable exports byte-identical. No saved geology selection, world
identity or continuing saves. Disposable game directories only, under the fixed
runs/acceptance/td-client-map-1 root; options are synthetic, never copied back.

Budget: at most THREE serial client attempts INCLUDING failures, no replacements
beyond those three; <=900s each, <=2700s summed. Failed launch consumes a slot.
Heap2GiB, sampled working set6GiB, output root2GiB, free disk reserve4GiB. One-second
watchdog; sampled limits may overshoot by one interval. Kill only launched process
tree on cap/error/interruption. Retain attempt ledger BEFORE spawn, command,
all source/artifact/dependency hashes, logs/class-load log, monitor samples, file
inventory, screenshots and partial failures. No models/input writes or TD launches.
No automatic retries or downloads. Stop if safety cannot be proven without major
infrastructure. Build/validation processes are not client attempts.

Actions: enter from diagnostic title; select exposure native2944,13824; toggle
PR59/58 preserving the sample; toggle display scales1/6 preserving selection;
select cover records in both remaining PR59 IDs, inspect stable IDs and BOTH full
token lines with shared surface/deep reference. Click an actual gap and exterior:
selection clears, support stays unknown. Check footprint X[2688,5761),
Z[10880,13953), side3073/18438 blocks; spacing64/384 blocks=4/24 chunks;
nominal width2048/12288 blocks=128/768 chunks ALONG X. Escape returns to title,
reopen and quit. Inspect at 1600x1000 GUI2 and 1200x900 GUI1 (bounded two sizes/
scales; resizing allowed within a launch). Actual screen interactions/screenshots
are mandatory; computed retained checks and visual judgment reported separately.
Record clipping/readability limitations honestly; no player recognition,
geological validity, performance or gameplay acceptance claim.

Archive actual client screenshots, console/latest/debug/class-load logs, manifest,
JAR entry list, exact executed sources/artifact, inputs, launcher/contract, action
record and output inventory. Vanilla may create an empty saves directory during
storage-source construction; no world/save files or world access are allowed.
Verify no world/save files, production mod, TD/model
initialization/inference/query classes. Package deterministic portable replay and
corruption checks; passing CI before merge, strict old/new re-export after final
Windows checkout. Keep #9/#11 open and all carried-forward gates in td-retained-map.md.
PR59 negative contact result stays negative. PR54 four TD launches exhausted,
executed4a2fa1c; final capture mixin compile-only; historical arrays/indices/ULPs
unavailable. All frozen failures, geology-1, production selection, strict guards,
immutable inputs and optional Ulti-World unchanged. No seeds, queries, histories,
palettes/dikes/minerals/integrations/migration or general visualization framework.
