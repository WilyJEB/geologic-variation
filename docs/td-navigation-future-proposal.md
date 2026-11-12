# Future retained-display attempt: proposal only, no authorization

Navigation-1 and navigation-2 remain exhausted. This proposal allocates nothing,
does not change their launchers/ledgers and cannot be used to launch a client.
It must be separately reviewed and explicitly authorized before implementation.

## Review and authorization conditions

Reviewed against [navigation-1](td-navigation-protocol.md),
[navigation-2 and its decimal amendment](td-navigation-supplement.md), the
[frozen hashes](td-navigation-supplement-hashes.json), portable actions/replay,
readiness records and [remaining gates](td-navigation.md). Fetched main remains
513c4ca; local/remote branch and GitHub PR62 head agree at c57ca8a. PR62 is open,
draft and unmerged. Build/offline CI run42574078432 passed at that head; this is
current verification of historical CI, not a new client or readiness result.

Decision proposed: permit preparation of ONE future attempt to inspect the
existing visible terrain-aware prototype. No geological construction. Preparation
and execution are distinct approvals: approval to prepare is not permission to
launch. Before any allocation/spawn, all of these must be recorded:

1. A human is present, understands the two bounded physical W holds below,
   can release immediately, and confirms availability through capture and quit.
   If absent before launch, defer without allocation. If unavailable after spawn,
   release input and end the attempt normally where possible; time keeps running.
2. The user explicitly approves a client launch in a named Windows execution
   context (account/session, restricted or approved execution, Java path and exact
   command). Prior approval of non-client --check-only does not authorize this.
   The retained label "approved" alone is insufficient to identify that context.
3. The separately reviewed protocol, executable launcher/collector/replay and
   manifest of exact source, built JAR, configuration and immutable input hashes
   are committed and pushed before launch. Review the resulting commit/hashes;
   do not copy historical planned hashes over changed bytes. Restrict any adapter
   change to the new canonical root/single slot; retain the decimal correction.
   Offline checks must prove one-slot accounting, isolation, cap/stop/finalization
   and PID-tree evidence before asking for execution approval. No such new
   executable or budget exists in this proposal revision.
4. Immediately before allocation, the frozen executable's --check-only passes in
   that same approved context, with its command, context and hashes retained and
   both old ledgers/directory lists unchanged. Any context/byte change invalidates
   that preflight. Failure stops without allocation; no automatic retry or switch
   of permissions. Success still requires the explicit client authorization.

## Proposed single-attempt contract

Proposed budget: ONE new attempt including failure, no retries; a separately named
navigation-3 root and pre-spawn ledger, never reuse/reopen any disposable save.
Before that attempt, push the approved contract, executable collector and exact
source/artifact/input hashes. Keep the current supplemental launcher exhausted.
Run --check-only in the exact approved execution context immediately before any
allocation. A Python IPv4 handshake is necessary only; it cannot prove Java/Netty,
IPv6, selector, integrated-server, UI or shutdown readiness. A failed readiness
check allocates nothing. No automatic permission changes, retries or relaunches.

Resource contract: startup to first position <=180s; wall <=1200s including human
handoffs; heap2GiB, sampled working set6GiB, whole new output2GiB, free reserve4GiB,
one-second watchdog (one-interval overshoot possible). No TD/model/provider bytes,
initialization, requests or windows: caps ZERO; no downloads or new observations.
Reuse installed pinned dependencies read-only; retain all current hash, nested-JAR,
class whitelist, injection and isolated fresh-save/local-attachment/LAN guards.
Use only a new vanilla flat navigation-only world, reused seed8675309, peaceful
creative, no structures/bonus chest, render2/simulation5,30fps; unrelated terrain.

Frozen route, exact decimal commands (Y100.0 is unrelated context): exposure
2944.0,13824.0; covers2688.0,10880.0 and5760.0,10880.0; gap2720.0,10912.0;
last site5760.0,13952.0; exterior5761.0,13953.0; scale6 exposure17664.0,82944.0.
Verify actual exact positions before assigning retained identity. No nearest-site
or interpolated identity; gaps/exterior unknown; X=s*x,Z=s*z, scales1/6.
Do not change origin, records, drawing, panel or synthetic geological histories.

At both exposure scales, explicitly hand off to the present human: hold W <=4s,
then release and wait for capture. Target16..32 blocks, stop immediately beyond32;
only <=1s additional human holds if needed within that bound. Capture before and
after positions and actual screenshots. Teleport is setup, never movement evidence.
Use documented short key taps only; if unavailable/ineffective ask human for the
named shortcut, never invent held-key APIs. H off/on, P full unchanged readable
panel and Escape to same live HUD; PR58/59 same-site comparison, exposure, both
cover cards and both full shared-token halves. Test1600x1000 GUI2 and1200x900 GUI1
within the one attempt. Capture route sites/edges/gap/exterior, scale6, return and
both configurations. All these unmet checks remain required, not waived by readiness.

The panel creates its own RetainedMap model: P does not inherit the HUD selection,
mode or scale. Use its existing mouse controls to select the exact named native
site and PR58/59/scale, recording the visible selected coordinates, ID and tokens.
Do not infer same-site comparison from the player's position alone or add panel
synchronization. After each movement capture, opening the panel may inspect that
fixed retained site without claiming the displaced player is still on it.

Required evidence checklist for this one attempt (all rows required):

| Check | Actual evidence and acceptance condition |
| --- | --- |
| Entry/setup | Title, fresh-save/local-server/attachment guard logs, first position within180s; each R destination matches the exact decimal X/Z above before assigning support. A +0.5 offset fails setup. |
| Movement at scales1 and6 | Human handoff/release in actions; successive logged positions, before/after real HUD images,16..32-block displacement, scale1 chunk-edge crossing, coherent marker motion. No teleport counted. |
| HUD and return | H off/on images and logs; P from live world, full readable panel, Escape back to the live HUD with position/scale checked. |
| Fixed route/support | All seven destinations, exact last site, gap and exterior images/status; clipped exterior marker remains labeled unknown. B changes interpretation only; position unchanged. |
| Panel comparison | Same selected native exposure in PR58/59; both named cover cards, exposure interpretation, distinct deep identities and both unchanged full shared-token halves actually readable. |
| Configurations | Actual1600x1000 GUI2 and1200x900 GUI1 settings plus HUD/panel/return captures in each; record any clipping or illegibility as unmet. |
| Scale arithmetic | Offline exact floors/chunks, inverse conversion, side3073/18438, spacing64/384 (4/24 chunks), nominal along-X width2048/12288 (128/768 chunks), separate from visual judgment. |
| Shutdown/isolation | Normal integrated-server stop then client quit, exact PID/tree absence, complete inventories, shared dependency/input/viewer hashes unchanged and no forbidden executable bytes/classes. |

Record visual judgment separately: whether movement clarifies regional size,
contacts and shared history, and where it does not. A negative legibility judgment
must remain negative; completing captures does not justify a favorable claim.
Historical PR61 panel evidence and navigation-1 shutdown remain reused evidence,
not replacements for the required live route/return/configuration/shutdown checks.

Suggested time allocation inside the unchanged1200s cap: startup/entry0..180s;
scale1 movement and route/panel captures to600s; scale6 movement and controls to
780s; alternate configuration/panel/return to960s; normal shutdown from960s,
leaving240s for quit, capture and cleanup. These are workflow targets, not extra
time or retry allowances. On setup/input/capture failure, human stop, or a cap,
retain the failure and begin shutdown; no same-attempt world recreation, repair
relaunch, second seed or save reopening. Missing evidence leaves acceptance
incomplete even if the process exits normally.

Retain complete executed launcher/source/JAR/input bytes, command, dependencies,
class/guard/position logs, all action sequences, screenshots, options, monitor,
save/file inventories and partial failures. Separate human observations, computed
checks and visual judgment. Attempt normal save/quit and client quit within budget;
require server-stop evidence AND exact allocated PID/tree absence. Error/cap/stop
cleanup kills only allocated PID tree, waits and inventories; forced cleanup or
exit0 cannot substitute for normal shutdown. Missing finalization consumes the full
slot and blocks further launch pending documented reconciliation. No universal
filesystem-write tracing claim. Hash recheck shared inputs/viewer repairs afterward.

The future collector must retain timestamped parent/child PID identities and
command/creation identity while alive, normal server-stop/client-stop logs, exit
status and post-exit queries for every allocated descendant (including a child
that outlives the parent). A parent poll/pid_absent flag alone is insufficient.
Record forced cleanup separately, wait for the exact allocated tree and record
absence; never kill all Java processes. An allocated slot consumes the sole
attempt even if spawn fails; no remaining-slot inference from elapsed time.
Hard-stop/missing-finalization reconciliation cannot grant another slot.

Portable strict replay and corruption tests, passing CI and final Windows checkout
audit required. PR62 remains draft until the actual navigation acceptance is met;
even acceptance would establish diagnostic legibility only. Preserve PR59 negative
contacts, every historical failure and all report/retained-map carried validation,
performance, geology-1, continuing-save/adoption, production and optional Ulti-World
gates; #9/#11 remain open. No merge authorization is implied.

## Feasibility and explicit decision

One attempt can reasonably finish this narrow retained-display gate if entry,
exact setup, captures and human handoffs work: the frozen seven-site route and
two configurations fit the20-minute cap, without TD or new construction. This
is a conditional feasibility judgment, not a runtime prediction. Python IPv4
success has not tested Java/Netty/IPv6 selectors; the revised launcher has never
launched a client; decimal setup, complete controls/marker/panel return, alternate
configuration readability and normal shutdown remain unverified. The crowded
capture schedule and human/tool interruptions can still consume the only slot.
If it fails, publish the partial outcome, keep PR62 draft/unmerged and stop;
no replacement attempt is authorized. Even a full pass establishes diagnostic
legibility only and leaves PR59 and all production/adoption gates unchanged.

Authorization requested for later decision: approve or decline preparation of
this single-attempt contract and executable collector. After preparation is
reviewable and pushed, separately approve or decline exactly ONE client attempt
including failure, naming the execution context and confirming the present human
and same-context preflight. Neither decision has been granted by this review.
