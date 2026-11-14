# navigation-1: retained comparison while moving, NO TD

Base merged PR61 513c4ca; fetched main agrees. Push this contract and executable
scripts/launch-retained-navigation.py BEFORE adapter implementation or launch.
PR61's three attempts remain exhausted. This is a NEW two-attempt client budget,
including failures, no retries beyond it: 1200 seconds each, 2400 summed, heap
2GiB, sampled working set 6GiB, whole output root 2GiB, free reserve 4GiB.
One-second watchdog; limits can overshoot one interval. Kill only allocated PID
tree on error/cap/interruption; retain partial logs, command, sources/artifact,
dependency hashes, ledger allocated BEFORE spawn, samples and final inventory.
No automatic download. Output runs/acceptance/td-navigation-1/attempt-NN is new,
never reused. No TD launch, seed search, fresh TD observation or numerical run.

## Structural isolation and narrowly necessary changes

Reuse the PR61 independently pinned NeoForge21.1.251/Minecraft1.21.1 project and
launcher logic in a separate diagnostics/retained-navigation project. Compile
ONLY RetainedMap/RetainedMapScreen plus diagnostic adapters, never either parent
source set. Scan every supplied profile JAR and nested JAR for TD/ONNX/production
classes, whitelist display/diagnostic classes, reject inherited JVM injection.
Installed manifest SHA256 remains
706a7b7be2f110a87449f0ea090b6daf3882106f0d39acbe2c18b8a37d254924;
validate installed library SHA1 and retain their SHA256. No TD/provider/model
executable bytes or models, production mod/hooks/mixins or optional integrations.
Only installed libraries/assets are reused, read-only; no profile saves/options,
credentials or mods copied. Absence of executable TD code, not quiet logs,
structurally excludes TD initialization, inference and terrain queries.

Unchanged exact Windows source/resource SHA256:

* RetainedMap.java 59573cb79b24c1c1526018a237cfa0d3331f9fdc59311b0afbea7c6f54b69407
* RetainedMapScreen.java e2e674602aea6004144fa18a0f30bc365475757b88cea388d378db7ca52bb3d2
* retained-map.tsv ab7168c07af32e981601d2e2fecb7a8457ec3607e68e2dec0731a6c86a67b872
* td-retained-map.zip fafa93f9a8a4865e2e2592cce3a54a1f5937822a059f23a3dfbec31981e9e05a

No record, contact, ID, history, full token or drawing change. A new HUD adapter
calls the existing drawing model and adds actual player X/Z, floored block/chunk
coordinates and a marker. A diagnostic key toggles HUD; another opens unchanged
RetainedMapScreen with Escape returning to navigation. Panel cards remain exact;
HUD controls choose PR58/59 and scale1/6, with no production selection or setting.
No identity assigned by a nearest-site approximation: player position is a
retained site ONLY at an exact supported X/Z; otherwise support is unknown.
Footprint membership alone is not sampled support. Exterior marker is clipped
and labeled exterior; original absolute origin remains. X=s*x,Z=s*z; TD metres
are never Minecraft Y. No interpolation, height reconstruction or new histories.

PR61 SaveBarrier, WorldBarrier and title restriction remain unchanged in their
original project. The navigation project needs distinct diagnostic-only guards:
permit ONLY a single newly created navigation-only save beneath the launcher's
canonical new game directory; reject different names/roots, existing worlds,
symlinks, subsequent creation and world loading without a creation capability.
Integrated-server startup must use that save and fresh-world flag; attachment
must require that local server, never remote multiplayer. No normal title world
browser, quickplay, LAN publishing or continuing-world route. Production guards
are untouched. Retain positive guard logs and negative guard checks.

## Disposable navigation context

Dedicated title button invokes vanilla createFreshLevel with fixed name
navigation-only, reused seed8675309, flat vanilla preset, structures/bonus chest
off, peaceful creative, commands allowed solely for fixed route positioning.
No copied level.dat, existing seed inspection or TD observations. Fresh creation
occurs only once per attempt; no reopen. Use synthetic options at render2,
simulation5, 30fps. Vanilla flat chunks, entities and save files are navigation
context ONLY, unrelated to the retained TD landscape; label this on screen.
No terrain read is used by the HUD: player getX/getZ and retained bytes only.
Do not imply correspondence of vanilla terrain to retained elevation/history.
World/save writes allowed only beneath this new attempt; logs/options/config/
natives/screenshots and executed provenance likewise remain there. Enumerate
files and retain unexpected writes as a failed run. Shared installed dependencies
and pre-existing viewer-repair files are hash-checked after execution. No source
profile/continuing save directory is opened or enumerated by the diagnostic.

## Fixed verification route and evidence

Use real client at1600x1000 GUI2 and1200x900 GUI1, resizing/options within an
attempt allowed. Enter/exit HUD, move, open full panel, Escape back, compare
PR58/PR59, exposure/cover and both full token halves, quit cleanly. No general
teleport UI or automated exploration: fixed vanilla commands visit only these
navigation coordinates, with Y fixed100 for flight (never TD elevation):

1. scale1 native exposure2944,13824; walk/fly forward across chunk edge by
   16..32 blocks, record actual successive positions and marker movement.
2. scale1 native covers2688,10880 and5760,10880; inspect exact panel cards.
3. scale1 gap2720,10912; near/exact far edge5760,13952 and exterior5761,13953.
4. scale6 exposure17664,82944; move16..32 blocks. Scale toggle changes inverse
   coordinate interpretation, never teleports or changes retained sample identity.

Teleporting is route setup, not evidence of walking. Preserve complete action
sequence and actual positions; gaps/exterior get no inferred geology. Verify
side3073/18438 blocks, spacing64/384=4/24 chunks, nominal width2048/12288=
128/768 chunks ALONG X, floored signed block/chunk conversion separately offline.
Actual screenshots: title, moving HUD before/after, scale6, gap, exterior,
PR58/PR59 same-site panel, cover/full token, return from panel, alternate window.
Retain console/latest/debug/class-load logs, command/dependencies/JAR entries,
executed source/artifact/input bytes, monitor, final save/file inventory, PID
cleanup and partial failures. Portable archive hash replay and targeted corruptions
must reject altered records, forbidden classes, bad save path or missing guard.
Actual client observations, computed coordinate/record/log checks and visual
judgment remain separate. Assess size/contact/shared-history legibility while
moving; no player recognition, geology, gameplay acceptance or speedup claim.

## Unchanged decisions and gates

PR59 negative contact result remains negative; do not promote straight bands.
All td-retained-map.md carried gates remain, including every frozen failure,
geometry/uncertainty, numerical cause/reproducer, joining, fresh validation,
paired startup/cold/warm/full-route performance and versioned adoption/save-safety.
Geology-1, strict production guards, continuing worlds, immutable inputs and
optional Ulti-World unchanged. PR54 four TD attempts exhausted; ran4a2fa1c, final
capture mixin compile-only, historical arrays/indices/ULPs unavailable. #9/#11
remain open. No new TD seeds/observations, parameter search, numerical experiment,
replacement history, palettes/dikes/minerals/integrations or migration.
CI must pass before merge; strictly re-export old and new evidence after final
Windows checkout. If bounded isolation requires substantial infrastructure,
stop before launching and report the concrete obstacle and smallest alternative.
