# navigation-3: frozen preparation, execution NOT authorized

Base c91c76b8ebad7d03ae8852102b33bd06d62cea0a; main513c4ca. PR62 remains
draft/unmerged. User authorized preparation only. This contract, collector,
schema, tests and exact hash manifest must be pushed and reviewed before any
separate client authorization. No installed-profile preflight, Java, Minecraft,
TD, save reopen or allocation is performed during preparation.

## Independent single-use allocation

ONE possible future client attempt INCLUDING failure; no retries, replacements,
relaunches, automatic permission changes or second world. The sole runtime root
is `runs/acceptance/td-navigation-3`, absent during preparation. Exclusive creation
of this root is the single-use tombstone. A durable ledger, charged the full1200s
with zero remaining slots, is written BEFORE any setup or spawn. Existing root,
missing ledger, interrupted finalization, spawn failure or cleanup failure all
consume the slot; reconciliation never grants another. Never delete/reset it.

Game directory is exactly `td-navigation-3/td-navigation-2/attempt-01` beneath
`runs/acceptance`. The inner suffix is required by the unchanged decimal-corrected
JAR's root guard; it is NOT the historical sibling navigation-2 root or ledger.
No adapter change or new build is needed. Reuse `raw/final-compile-only.jar` from
the supplemental archive byte-for-byte, separately from each historical executed
JAR/source/launcher. It loaded in the last historical failed entry, but decimal
setup and the route still have no runtime acceptance. Historical launchers,
contracts, archives, ledgers, attempts and failures remain unchanged.

## Authorization and immediate preflight

Exact executable: `scripts/launch-navigation-3.py`; native process helper:
`scripts/navigation-process.py`; replay: `scripts/replay-navigation-3.py`.
Exact bytes and artifact/configuration/input hashes:
`docs/td-navigation-3-hashes.json`, with portable preparation archive
`docs/evidence/td-navigation-3-preparation.zip`. Preparation archive is not a run.

Before allocation, require a fresh external authorization JSON conforming to
`docs/td-navigation-3-schema.json`: explicit approval of ONE client attempt
including failure, pushed commit/manifest SHA256, exact absolute command,
named account/computer/session/Python/Java/permission context, present human
confirmed within60s and available through captures and quit. No approval template
is issued with true authorization flags. Prior non-client readiness approval does
not qualify. Human confirms readiness again if preparation/preflight takes too long.

Proposed context: the user's interactive Windows desktop, current account/session,
Python313 at `C:/Users/digif/AppData/Local/Programs/Python/Python313/python.exe`,
Java at `C:/Program Files/Java/jdk-21/bin/java.exe`, separately approved execution
(restricted execution previously denied loopback). Actual account, session,
computer, numeric Windows session ID and permission boundary must be named and
approved at launch time (SESSIONNAME can be absent).

Command after approval, from this checkout (authorization file external to runtime):
`<absolute Python313> <absolute scripts/launch-navigation-3.py> --launch --authorization <absolute approval.json> --context <approved-context-name>`.
The authorization must contain this exact argv array. `--launch` performs the
frozen `--check-only` internally in the same process/context immediately before
allocation, retaining its full results. Separate check-only success cannot be
reused. Require fresh human confirmation, unchanged context/hashes/old ledgers,
and <=5s from completed preflight to allocation. Any failure stops without a root.
There is no automatic permission retry. Do NOT run either mode during preparation.

Preflight reuses the frozen supplemental installed manifest/library SHA1/SHA256,
nested-JAR scan, diagnostic whitelist, mixin/TSV, immutable source/resource/viewer,
JVM-injection and IPv4 port0 one-handshake checks. Additionally freeze Java bytes,
all shared assets/natives and exact portable JAR equality.
`td-navigation-3-installed-inputs.json` freezes129 reused historical dependency
hashes,4061 shared asset/native file hashes and Java bytes. Preparation only read
file bytes to compute these hashes; it did not run installed-profile preflight. Hash shared inputs again
before spawn and after termination. Never copy profile saves/options/mods or inspect
continuing saves. Shared dependencies/assets remain read-only. No downloads.

## Resource and isolation limits

Startup to first actual position <=180s; entire allocated attempt including setup,
handoffs and cleanup <=1200s; heap2GiB; sampled sum of job working sets6GiB;
whole new output2GiB; free reserve4GiB; one-second monitor target, OS/query latency
can delay samples. Individual identity queries have1s timeouts; record full sample
times, never claim instantaneous peaks or guaranteed one-second detection. Any
observed overshoot is a failure. Cleanup has a15s bounded wait inside the wall
budget, not additional runtime entitlement. Begin normal shutdown at960s, leaving
240s reserve. `SHUTDOWN-REQUIRED` signals the deadline; `STOP` requests immediate
failure cleanup. Neither file triggers input, permission changes or a relaunch.

TD requests, startup/model/provider initialization, inference and computed windows
caps all ZERO. Zero entries in monitor are structural deductions from executable
exclusion, not observed TD counters. No TD/provider/model/production code, models,
hooks or optional integration bytes. Retain nested-JAR/class whitelist checks,
fresh-save/one-create/local-attachment/LAN/title/disconnect barriers. No new seed
or TD terrain observation, no geological construction or source-set changes.

Use only a NEW unrelated vanilla flat navigation-only world, reused seed8675309,
peaceful creative, no structures/bonus chest, render2/simulation5/30fps. Save name
`navigation-only`; no reuse/reopen. The installed unchanged adapter checks canonical
game root and fresh creation capability. Reject redirected/symlink paths and any
other save. Inventory is not universal filesystem-write tracing.

## Frozen route, human handoffs and full unchanged panel

R setup route, exact decimal X/Z (Y100.0 unrelated to TD metres):

1. exposure2944.0,13824.0 at scale1;
2. west cover2688.0,10880.0;
3. east cover5760.0,10880.0;
4. gap2720.0,10912.0;
5. last site5760.0,13952.0;
6. exterior5761.0,13953.0;
7. exposure17664.0,82944.0 at scale6.

Verify exact actual decimal setup before assigning support; +0.5 fails. X=s*x,
Z=s*z for scales1/6, no nearest-site/interpolation identity. Gap/exterior unknown;
clipped marker stays labeled exterior. B changes interpretation only, no teleport.
Do not change origin, records, synthetic histories, marker or full panel drawing.

At each exposure explicitly hand control to the present human for W <=4s, release
and wait for capture. Target16..32 blocks, stop immediately beyond32; only <=1s
additional holds if needed inside that bound. Record all holds and releases,
successive logged positions and before/after actual HUD captures. No agent inputs
during holds. Teleport is setup, never movement. If taps fail, request the named
shortcut from the human; never invent held-key APIs. Missing human before launch
defers without allocation; loss after spawn ends the attempt, clock keeps running.

H off/on; P opens unchanged readable full panel; Escape returns to same live HUD.
Panel creates an INDEPENDENT RetainedMap: explicitly select exact native exposure,
PR58/59 and scale with existing mouse controls; retain visible coordinate/ID/token
selection. Do not infer panel selection from HUD/player position. Inspect exposure,
both named covers, distinct deep identities and both FULL unchanged shared-token
halves. Displaced player is not claimed to remain at the fixed retained site.

Test actual1600x1000 GUI2 and1200x900 GUI1 within this sole attempt; capture HUD,
full panel and return in each with settings visible/retained. All seven route
statuses/edges, scale6, marker, controls, same-site comparison and full readable
cards are required. Schedule: entry0..180s, scale1/route/panel to600s, scale6/controls
to780s, alternate configuration to960s, then normal server and client shutdown.
Any setup/input/capture failure or human stop ends inspection and starts shutdown;
no same-attempt world recreation, repair/relaunch or save reopening.

## Evidence and acceptance: every row required

`docs/td-navigation-3-schema.json` and replay CHECKS enumerate the complete checklist:
entry/setup; movement at BOTH scales; H off/on; panel/live return; seven exact
route sites/statuses; same native PR58/59 panel comparison; exposure; west/east
cover cards; first/second full token halves; BOTH configuration HUD/panel/return
sets; scale arithmetic; normal shutdown; isolation; exact PID-tree cleanup.
Each row needs actual observation, pass/unmet result and hash-addressed evidence.
`record-navigation-3.py` records ordered external event JSON, checks and human
review only after allocation; it cannot allocate or spawn. `--evidence` accepts
`role=relative/path.png`. Movement needs before/after, H needs off/on, panel return
needs hud-before/panel/hud-return, comparison needs pr58/pr59, and each configuration
needs distinct settings/hud/panel/return images plus `--configuration WIDTH HEIGHT GUI`.
Replay requires all named capture roles, not a generic screenshot for every row.
Visual rows require real images and named human review. No reconstructed images,
historical substitutes or waived rows. A negative legibility result remains unmet.

Actions contain complete ordered timestamped sequences, separate actual observations,
computed checks and visual judgment. Movement includes every hold/release, position
indices and before/after real images. Offline replay verifies exact positions,
signed floors/chunks, inverse scales, side3073/18438, spacing64/384=4/24 chunks,
along-X width2048/12288=128/768 chunks, movement bounds/chunk crossing and absence
of a route teleport in each movement interval. Human judges marker coherence,
readability, independent selection, token completeness and whether movement helps
understand regional size, contacts and shared history. Computation cannot certify
image content. Readiness, log presence, exit0 and CI cannot complete acceptance.

Retain ALL partial bytes: ledger, approval/preflight/context/command, full executed
source/configuration/input/artifact bytes, supplied dependency hashes, all logs,
class loads, guard/position sequences, actions/screenshots/options, monitor,
complete output/save inventory, shared input post-hashes and cleanup. No deletion
on failures. `replay-navigation-3.py <runtime-root> --export-runtime <external.zip>` packages
the complete root. `replay-navigation-3.py <external.zip> --runtime` audits it;
partial/missing-finalization packages stay INCOMPLETE. Archive outside runtime root. Interrupted/missing finalization is INCOMPLETE and consumes the slot.

Process control uses documented Windows CreateProcessW CREATE_SUSPENDED, assigns
a non-breakaway KILL_ON_JOB_CLOSE job BEFORE resuming Java, records parent identity
while suspended, then timestamped job PID lists/commands/creation identities.
Query failure or a disappearing unidentifiable sampled PID fails closed. Job
membership enforces containment for descendants between samples; short-lived
descendants may not have individual command records, so never claim a universal
process trace. Detect a child outliving its parent, mark failure, terminate only
the allocated job. Query every observed exact identity after termination and
require job-empty evidence; parent poll alone is insufficient. PID reuse is not
absence of query evidence and never authorizes killing an unrelated process.
Forced cleanup cannot prove normal server shutdown. Normal acceptance requires
`Stopping server`, `Stopping!`, exit0, no forced cleanup, complete identities and
all other checklist evidence. Native helper is offline mock-tested ONLY; actual
Windows job assignment/query/cleanup remains a future runtime uncertainty.

## Carried gates

Preparation tests/replay/CI and strict retained/new exports must pass after final
Windows checkout. Keep PR62 draft/unmerged. Even full later acceptance establishes
diagnostic legibility only. PR59 negative contact result, PR57 reduction, PR51
Paired coarse drift, PR52 Actual matching native support changed, old height/
residual and #5 strict final-block failures remain. Preserve geometry/uncertainty,
historical numerical reproducer, joining, fresh validation, paired startup/cold/
warm/full-route performance and versioned adoption/save-safety gates. Geology-1,
continuing saves, production guards, immutable inputs, optional Ulti-World and
unrelated temp/viewer repairs unchanged. PR54 four launches exhausted, executed
4a2fa1c; final capture mixin compile-only; old arrays/indices/ULPs unavailable.
#9/#11 remain open. No migration or new geological construction.
