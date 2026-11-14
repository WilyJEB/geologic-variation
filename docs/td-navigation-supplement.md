# navigation-2: human-assisted retained navigation

Supplement to frozen navigation-1, which remains exhausted with both failures
unchanged. Base ed42ef0; main 513c4ca. Push this contract, exact hash manifest and
executable launch-retained-navigation-supplement.py BEFORE implementation/launch.
No TD execution or new TD seeds/observations are authorized.

## New independent budget and safety

Two NEW client attempts including failures, 1200 seconds each, 2400 summed.
Startup to first position log must finish within180 seconds. Heap2GiB, sampled
working set6GiB, total new output2GiB, free reserve4GiB, one-second monitor.
Each new attempt directory under runs/acceptance/td-navigation-2 is allocated
once, with its own pre-spawn ledger. No old ledger reset, reuse or save reopen.
Signal handlers enter finally cleanup; cleanup ignores further interruption,
kills only allocated PID tree, waits and records PID absence, inventory and
partial logs. Hard termination/power loss cannot guarantee finalization; an
unfinalized allocation consumes its full slot and blocks another launch until
documented reconciliation. All failed partial output is retained.

Reuse installed pinned manifest/libraries/assets read-only; scan supplied and
nested JARs and whitelist diagnostic classes exactly as navigation-1. Reject JVM
injection. No TD/model/provider initialization/inference/query executable code,
production hooks/source sets or continuing-save paths. PR61 barriers remain
unchanged. Only navigation root name changes to permit this new isolated budget.
Exact reused and planned changed source/resource hashes are frozen in
td-navigation-supplement-hashes.json; launcher verifies them before spawn.
Record complete executed sources/JAR, command, dependency hashes, class logs,
guard logs, screenshots, options, monitor, inventory and partial failures.
The inventory is not universal OS filesystem tracing.

One NEW disposable vanilla flat navigation-only world per attempt: reused
seed8675309, isolated attempt save root, creative/peaceful, no structures/bonus
chest, render2/simulation5,30fps. Terrain is unrelated navigation context only.
No production guards, geology-1, immutable inputs or Ulti-World changes.

## Supported input and fixed route

Inspected Windows APIs: sky.press_key has no held duration; cua Windows explicitly
rejects durationMs. Never invent key-down/up or duration options. The user agreed
to provide held movement input. Agent uses documented window-targeted key taps
for event-based H/P/V/B/R and panel controls; user physically holds W for bounded
movement. If taps fail, ask user for the named shortcut rather than invent APIs.
Require fresh screenshots/logs before and after movement; explicitly label human
input. No teleport counts as movement. User handoff time remains inside budget.

Reuse navigation-1's exact route: R cycles exposure2944,13824; covers2688,10880
and5760,10880; gap2720,10912; last site5760,13952; exterior5761,13953;
scale6 exposure17664,82944. R commands are setup teleports at unrelated Y100.
At exposure scale1 and scale6, user holds W for <=4 seconds, stops, and waits
for inspection; target16..32 blocks, stop immediately if displacement exceeds32.
If necessary use <=1-second human holds to complete the bounded16..32 route.
Use actual vanilla walking/flying only. Record exact setup and observed positions.
Do not change native origin/drawing/records or assign identity to gaps/exterior.
X=s*x,Z=s*z, s1/6; TD elevation metres never Minecraft Y. No interpolation.

Verify H off/on; P unchanged full panel; Escape return to same live HUD; compare
PR58/59 at same exact site, exposure and both cover cards/full shared-token halves.
Use unchanged full panel for readable text. Test1600x1000 GUI2 and1200x900 GUI1
within an attempt using vanilla options/window settings or second attempt.
Capture actual title, HUD before/after human movement, return, scale6, all fixed
route sites/edges/gap/exterior, comparison/exposure/cover/token and configurations.
Actions JSON separates actual observations, computed coordinate/record/log checks
and visual judgments. Portable checks verify exact hashes, floors/chunks,
scale distances, immutable identity, forbidden-class exclusion, guard application,
save inventory, dependency preservation, server shutdown and exact PID cleanup.
Absence of acceptance leaves PR62 draft even with passing CI.

All carried gates in td-navigation.md/td-retained-map.md remain, including PR59
negative contacts, every frozen failure, validation/performance/adoption/save
safety. No new construction/history, straight-band promotion, parameter search,
numerical experiment, palette/dike/mineral/integration/migration. PR54 four TD
launches exhausted, ran4a2fa1c; final capture mixin compile-only; historical
arrays/indices/ULPs unavailable. #9/#11 remain open. CI before any merge; strict
retained/new re-export after final Windows checkout. Movement can inform diagnostic
legibility only, not player recognition, geological validity or gameplay acceptance.

## Pre-attempt2 setup correction

Attempt1 actual client showed vanilla integer teleport centering (+0.5 X/Z).
Retain that failure; never relax exact sample identity. Before attempt2, push
this amendment and planned source hash, then append .0 to both fixed X/Z
command literals (Y100.0 remains unrelated context). Same seven frozen sites,
no new route/support/history. Launcher chooses the predeclared hash for attempt2.
No additional launch slots. Human walking remains separate movement evidence.
