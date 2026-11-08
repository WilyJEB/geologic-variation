# Retained navigation attempt: acceptance failed (#11)

**The no-TD client creates a disposable vanilla world and draws the exact retained
comparison, but the requested movement inspection is NOT verified.** Two launches
consumed the new budget, including failures. No further client or TD launch is
allowed under navigation-1. This work is a draft, not ready to merge as completed
navigation tooling. No gameplay improvement or adoption is claimed.

Reconciled fetched main and GitHub PR61 at513c4ca; #9/#11 remain open. Read AGENTS,
client-map/report/contract/portable evidence, retained-map/story and carried
observation/numerical protocols. Existing viewer repairs and unrelated temp/
preserved. [Contract and executable launcher](td-navigation-protocol.md) pushed
at9bafdec before implementation; first adapterc17f2a1 and login correctionbf85d6f
pushed before their respective launches.

## Implementation and isolation

Separate diagnostics/retained-navigation reuses the isolated PR61 project with
Minecraft1.21.1/NeoForge21.1.251 only. Original retained-client and production
code remain unchanged. It compiles the exact RetainedMap/RetainedMapScreen and
immutable TSV; no contact, sample, token, authored history or drawing changes.
The HUD adds player X/Z, floored blocks/chunks, inverse scale1/6 coordinates,
exact-site/gap/exterior labels and a magenta position marker. Outside markers
are explicitly clamped to the retained rectangle. No nearest-site identity,
height interpolation, Minecraft-Y conversion or production selection.

New diagnostic guards narrowly permit createFreshLevel for navigation-only
under the canonical newly allocated game directory, only while a creation
capability is active. Existing save, alternate name/root, redirected root and
subsequent creation reject. Startup requires fresh flag and the exact save;
world attachment requires the local integrated server. Title omits world browser
and multiplayer; after creation it omits creation/reopen. LAN publishing rejects.
The second build restricts disconnect UI as well. These replace barriers only
in the NEW project; PR61's original unconditional barriers are preserved.

The launcher checks installed manifest/library hashes, scans supplied/nested JARs,
whitelists diagnostic classes and rejects inherited JVM injection. No TD/ONNX,
provider/model files, production addon/hooks or source profile saves/options enter
the launch. Shared libraries/assets are read-only inputs; hash rechecks match.
Absence of executable TD bytes is the structural exclusion; class-load and guard
logs supplement it. No continuing save root is supplied or inspected by this mod.
The monitor inventories this run and rejects other save names; this is not an
OS-wide filesystem write trace, so do not claim universal external-write proof.

Vanilla flat preset, reused seed8675309, structures/bonus chest off, peaceful
creative, spawn radius0, render2/simulation5 and30fps. Vanilla chunks are unrelated
navigation context, NEVER retained TD terrain evidence. The HUD reads player
X/Z only; terrain heights and block states are not used. Fixed route teleports
use Y100 purely for navigation; they were NOT successfully invoked.

## Actual client evidence and failures

![Actual Minecraft HUD; navigation controls failed](evidence/td-navigation-hud-controls-failed.jpg)

[Portable archive](evidence/td-navigation.zip) · [hashes/results](evidence/td-navigation.json)
· [exact action record](evidence/td-navigation-actions.json)
· [unchanged cover panel](evidence/td-navigation-panel-cover.jpg)

Attempt1 failed local login: reused display-only username RetainedDiagnostic has
18 characters, while login permits16. It created only its new disposable flat
save. Screenshot/logs retain the error. Ctrl-C interrupted the launcher; both
processes were confirmed absent, but finalization did not run. Original allocated
ledger is retained, final inventory was collected afterward, and the FULL1200s
slot is conservatively charged. Exact completion duration is unknown; monitor
samples are retained. This is a launcher cleanup limitation, not a passed case.

Attempt2 used RetainedNav and reached the world at1600x1000 GUI2. HUD showed
actual playerX7.5,Z-0.5, blocks7,-1, chunks0,-1 and EXTERIOR UNKNOWN, matching
signed floor ownership. Short R/P tool inputs did not trigger diagnostic actions;
P instead displayed vanilla social-interaction text. Short W produced no recorded
X/Z change. No fixed-route or overlay-toggle log exists. Escape/pause, save/quit
to title, unchanged default cover panel with both token halves, panel Escape and
normal quit worked. Server-stop logs, absent exact PIDs16300/29536 and no remaining
Minecraft window confirm cleanup. Exit0 is NOT movement acceptance.

Source diagnosis: render-time GLFW polling can miss press/release between frames.
Final adapter handles KeyboardHandler.keyPress events instead and consumes its
diagnostic shortcuts. **This correction builds, but was never run.** Do not
substitute final source for the separately archived executed polling source/JAR.
Short vanilla W also failed to move in this automation, so the input diagnosis
does not establish a fully solved movement route.

Unverified: HUD entry/exit/return controls, actual movement and marker coherence,
all retained route sites/edges/gaps, scale1/6 in-world behavior, same-site comparison,
exposure/cover inspection from a loaded world and alternate GUI/window settings.
PR61 panel interactions are reused evidence, not new navigation acceptance.

Visual judgment: the unrelated-world label and coordinate lines are readable;
shrinking the entire unchanged drawing makes HUD labels too small. The map renders
contacts, but **movement's benefit for regional size, contacts and shared history
cannot be assessed**. No player recognition, geological validity or gameplay claim.
PR59 remains negative: authored terrain-dependent history and connected straight
bands did not establish better landscape-related contacts.

## Verification, disposition and next step

Both attempts consumed, charged1338.391s/2400 (first1200 conservative, second138.391
measured), each within1200. Heap2GiB; sampled working-set/disk/free-space caps are
checked by portable replay, not claimed instantaneous bounds. New raw evidence
retains screenshots, complete logs/class loads, manifest/dependency hashes,
executed source/JAR, save/file inventories, samples, original and finalized ledgers.
Post-run dependency and viewer-repair hashes match. No TD execution or new TD data.

New checks: isolated final compile and unchanged Java retained coordinate/record
check; five portable evidence/corruption tests reject forbidden classes, alternate
save paths, modified records and missing guards. CI compiles/replays; no client.
Strict retained/new exports must pass after the final branch Windows checkout.
No final merged checkout exists because runtime acceptance failed; keep PR draft.

Smallest remaining step: verify the event-based controls and the already frozen
route in this same isolated world harness under a separately authorized finite
client budget; first address reliable held movement input and use the full panel
for text. No new regional construction or TD observations are needed to resolve
that UI question. Do not expand to another map framework or promote straight bands.

All carried gates in td-retained-map.md remain. PR57 reduction, PR51 `Paired
coarse drift`, PR52 `Actual matching native support changed`, old height/residual
criteria and #5's stronger final-block assertion stay failed. Geometry/uncertainty,
historical numerical cause/reproducer, multi-field joining, fresh validation and
paired startup/cold/warm/full-route performance remain unresolved. Adoption needs
versioned identity, explicit new-world choice, bidirectional continuing-save
rejection, exact restoration/reopen and snapshot/block/persisted-container safety.
PR54 four TD attempts exhausted, ran4a2fa1c; final capture mixin compile-only;
historical arrays/indices/ULPs unavailable. Geology-1, production guards/selection,
immutable inputs, optional Ulti-World unchanged. No new TD seeds/observations,
replacement histories, parameter search, numerical experiments, palettes, dikes,
minerals, integrations or migration. **#9/#11 remain open.**
