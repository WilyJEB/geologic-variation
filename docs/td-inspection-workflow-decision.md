# Repository-first inspection workflow decision

Decision, 2026-11-14: **choose option 2: replace the companion presentation
prerequisite with a separately scoped, smaller offline inspection-card prototype.**
Keep the companion as retained explanatory material. Do not repair it or wait
for browser access before specifying and testing a card-shaped design. This
decision implements nothing and authorizes no adaptation preparation or execution.

## Reconciliation and capabilities

Starting local HEAD, origin/codex/retained-navigation and GitHub PR62 head agree
at `25253286c15408cbe86e98c8d165624439285105`; branch is
`codex/retained-navigation`. Local main/origin/main and live GitHub main agree
at `513c4ca1e950969453faf52723f7ee68c7d6c329`. Git network access in the restricted
shell failed; connected GitHub PR/commit reads supplied remote confirmation,
without assuming local remote-tracking refs were freshly fetched. There were no
tracked worktree/index changes. Existing untracked `docs/td-region-viewer.html`,
`scripts/build-td-region-preview.py` and unrelated `temp/` remain untouched.
[PR62](https://github.com/WilyJEB/geologic-variation/pull/62) is open, draft and
unmerged. Its native-preparation STOP is a separate unresolved scope.
[Exact starting-head build CI43633997669](https://github.com/WilyJEB/geologic-variation/actions/runs/43633997669)
completed successfully; it is reused build/offline evidence.

Read AGENTS.md, the [adaptation decision](td-region-explainer-adaptation-decision.md),
[blocked presentation report](td-region-explainer-presentation-check.md),
[prototype review](td-visual-prototype-review.md), [companion source](td-region-explainer.html),
its [builder](../scripts/build-td-region-explainer.py) and
[tests](../scripts/test-td-region-explainer.py), relevant retained-map sources,
resource builder/tests, navigation ownership and build configuration. Also read
the [observation history](td-observation-history.md),
[axis controls](td-axis-numerical-controls.md) and frozen
[window-history](td-window-history-protocol.md)/[axis](td-axis-numerical-protocol.md)
protocols. No portable evidence was rerun or re-exported for this guidance change.

This VS Code session exposes repository file/shell tools, connected GitHub reads
and writes, local raster-image inspection, and computer/browser automation APIs.
The connected document-control inventory returned **no connected document
sessions**. No dedicated VS Code webview-rendering or screenshot API is exposed.
The presence of automation APIs or a VS Code extension is not evidence of
permission to render the local HTML. Per the supplied history, Chrome connected
but rejected the local `file:` action and explicitly prohibited workarounds;
the earlier reports also record blocked in-app-browser access. No blocked action
was retried, browser launched, HTML injected, page served/rehosted, or alternative
surface used to evade that restriction. No rendered presentation check passed.
Local image inspection is a capability for future independently authored raster
artifacts, not authorization to screenshot or transcode the blocked companion.

## Options and evidence gaps

| Option | Value and limitation | Decision |
| --- | --- | --- |
| 1. Retain companion gate | Existing checks cover retained records, static content and links. A real visual/keyboard gate remains, and resolving browser access does not test the intended small game card. | Retain the artifact, retire this prerequisite for the new route. |
| 2. Smaller card prototype | One selected site's explanation, bounded text layout and unknown states can be checked using repository data and independently generated card images. No browser or game launch is needed. | Choose; separate scope and explicit static visual gate. |
| 3. Prerequisite blocks both | Neither terrain generation nor native monitoring is needed for an offline card. A usable local raster renderer/font is a future implementation prerequisite, not currently verified. | No demonstrated prerequisite blocks the design route. Stop that later slice if unavailable; do not install infrastructure or switch to browser troubleshooting. |

Evidence must stay separated:

* **Source checks now:** HTML has static SVG/cards, semantic headings, fragments,
  focus styling and caveats. The screen draws fixed lines. These are source facts.
* **Automated checks:** existing tests were read, not executed. Companion tests
  cover pinned archive/result hashes, exact sites/records, shared tokens, active
  clamp, Cards 2/3 comparison, unchanged maps, fragment targets, unsupported-space
  rejection, corruption rejection and canonical rebuild. They cannot prove pixels,
  keyboard behavior or comprehension. Starting-head CI is separate reused evidence.
* **Rendered presentation:** the companion remains unverified at both requested
  sizes, including scripts-disabled rendering and keyboard/focus/return behavior.
  Historical standalone PNGs and old Minecraft captures do not render this HTML
  or a future card. No new rendered evidence was collected here.
* **Player comprehension:** no player study has been conducted. Neither source
  clarity nor a future image review proves players understand observation versus
  invention, site height versus regional mean, or conceptual versus measured depth.
* **Minecraft acceptance:** previous retained-panel evidence applies to its exact
  historical artifact/configurations. It cannot establish a redesigned card's
  GUI scale, font metrics, selection, focus, HUD coexistence, movement correspondence,
  normal shutdown, performance or continuing-save acceptance.

## Ownership and proposed file boundary

[RetainedMapScreen](../src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMapScreen.java)
owns a private new `RetainedMap`, scales a 1200x900 logical canvas to the viewport,
maps mouse clicks back to it and returns to its parent on close.
[RetainedMap](../src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMap.java)
loads the hash-pinned TSV, owns mode/scale/selection, hit testing and drawing through
`Ink`. Its card uses preformatted measured/authored strings, rounds height to
three decimals and draws unwrapped 13-pixel-spaced lines; richer companion
precision/semantics must be mapped from archived records, not reverse-parsed
from these strings. Its six-pixel hit radius selects a nearby *retained site*;
that is not an observation at the click coordinate.
[Navigation](../diagnostics/retained-navigation/src/main/java/dev/wilyjeb/retainedclient/Navigation.java)
owns a separate static model for HUD/route state. Opening the full panel creates
a fresh screen/model; player position and HUD selection are not shared card state.
The diagnostic build explicitly whitelists the map/screen and retained resource.
None of these owners, whitelists, frozen sources or resources should change in
the proposed offline slice. Later integration must deliberately choose selection
ownership rather than silently coupling HUD, player position and panel selection.

**Proposed next slice, requiring separate authorization:** implement an independent
static card model and raster contact sheet, using only the existing PR58/59
archives as read-only inputs. Exactly these new files may be written:

1. `scripts/build-td-inspection-card.py` — bounded archive reader, exact-site
   lookup, typed semantic record, wrapping/layout and PNG generation; no import
   or execution of old builders/exporters.
2. `scripts/test-td-inspection-card.py` — focused data, corruption, support and
   text-bound checks for this model.
3. `docs/td-inspection-card-review.md` — provenance, renderer/font identity,
   commands, actual checks and visual observations/unverified items.
4. `docs/evidence/td-inspection-card.json` — exact semantic records, digests,
   displayed rounding, image dimensions and text bounding boxes.
5. `docs/evidence/td-inspection-card-1200.png` — 1200x900 contact sheet.
6. `docs/evidence/td-inspection-card-1600.png` — 1600x1000 contact sheet.

No existing files, CI/workflows, companion, tests/builders, Java, frozen resource
or launcher changes. Reuse a locally available Pillow/font only after checking
availability; pin/report their identities, fail on missing glyphs/dependencies,
and do not install/download. Existing repository plotting code uses Pillow, but
that does not establish this session's installed renderer or font availability.
These are new card illustrations, not a rendering or replacement screenshot of
the restricted HTML and not screenshots of Minecraft.

## Acceptance for that slice and what players could gain

Limit input to `docs/evidence/td-story.zip` and
`docs/evidence/td-region-visual.zip`, pinned to the existing companion builder's
archive/result/input digests. Read archive members as data only. Use the three
already inspected sites r46,c4 (2944,13824), r0,c0 (2688,10880), r0,c48
(5760,10880), plus one gap (2689,10880) and one exterior (5761,13953).
No new seed, terrain, field fitting, contact construction or geological taxonomy.

Each contact sheet shows three single-site cards and one compact unsupported
state example, with a visible Cards 2/3 comparison. The JSON retains both gap
and exterior cases. Keep each supported card within a 360x760-pixel allocation
at both sizes, minimum 16-pixel body text, explicit wrapping and no clipped or
ellipsized essential text. Leave unused canvas space instead of shrinking type.
This is a fixed mock allocation, not a Minecraft GUI-scale specification. If
essential content cannot fit, report failure and stop; do not expand the surface
or remove caveats. Exact hashes/full tokens may be secondary JSON provenance;
the card must state shared identity/history without pretending measured depth.

Require all of the following:

* Match exact heights, coordinates, PR58/59 identities, full tokens, event strings,
  site counts and regional contrasts to archived records; compare surface/deep
  tokens exactly. Keep full precision in JSON and label display rounding.
* Separate observed site elevation (TD metres, never Minecraft Y), regional mean,
  seeded abstract substrate, authored history, conceptual surface/deep consequence
  and unknowns. Describe the broad trend as regional; retain the active -0.5
  clamp and distinguish it from the approximately -1.01 trend ratio.
* Exact lookup returns no observation for gaps/exterior. An explicit chosen site
  remains a site selection, never an inferred height at a nearby cursor/player.
  All 2,401 retained sites continue to abstain from actual geological interpretation.
* Cards 2/3 have different identities/tokens but the same cover-preservation event.
  Display that this does not establish geological necessity for their contact.
  Preserve PR59's negative contact finding. No real rock, age, erosion, cover
  thickness, interface geometry or recovered true history is asserted.
* Test corrupt/missing inputs and unsupported coordinates fail closed; retain
  exact semantic equality independently of rounded display strings. Check every
  text bounding box is inside its card, without overlapping reserved caveats.
  No network, hover, colour-only information, interpolation or hidden text.
* Inspect both new PNGs through the local raster-image tool at native size.
  Record whether headings, wrapping, caveats and comparison are actually legible.
  Bounds tests alone are insufficient. If that permitted image tool is unavailable,
  retain the visual gate as unverified and stop, with no browser fallback.

A pass would establish faithful retained-record mapping and a visually reviewable
compact explanatory hierarchy. It could help players answer "what was observed,
what did the seed choose, what story was invented, and what remains unknown?"
That usefulness remains a hypothesis until comprehension is assessed. Static
cards cannot test keyboard/focus, selectable states, Minecraft fonts/scales,
HUD coexistence or any live-world linkage. No interaction success is claimed.

## Gate replacement, preserved limits and stop

This decision **supersedes the earlier requirement to pass the full companion's
browser presentation gate before undertaking this independently scoped card
prototype**. It does not satisfy, waive retroactively or mark that gate passed.
The [blocked presentation report](td-region-explainer-presentation-check.md)
remains the historical result: no rendered checks passed. If the companion later
becomes a delivered player-facing surface, its original visual/keyboard/scripts-
disabled gate still applies under separately established permitted access.
For the new route, replace it with exact card-data/layout checks plus the two
new static-image reviews above. A subsequent explicitly authorized integration
decision is required before editing the game screen; actual runtime and player
comprehension gates remain separate. This is a scope change toward the intended
card, not a workaround for accessing the restricted page.

Navigation-3 remains verbatim, slot consumed, zero remaining, **INCOMPLETE**;
all 18 live acceptance rows remain unverified. Its roots, sources/artifacts,
approvals, ledger and partial evidence are untouched. Historical PR51 paired
coarse drift, PR52 matching native support, PR57 pressure reduction, height/residual
and #5 final-block failures remain failed. PR54's four launches are exhausted;
runtime used 4a2fa1c, final capture is compile-only, historical arrays/indices/ULPs
remain unknown. Geometry/support/uncertainty, numerical cause/reproducer and
multi-field joining remain unresolved. All previously inspected controls/seeds
remain development data. No recovery of real geological history is required.

Carry forward fresh validation gates (separately frozen new seeds, scales 1/6,
signed coordinates, contrasting terrain/multiple contacts, fixed coverage and
paired shared cells/scales); alternating paired CPU startup/cold/warm/full-route
performance; immutable versioned adoption/new-world-only selection; bidirectional
continuing-save rejection; original-artifact restoration/reopen; and full
snapshot/block/persisted-container preservation. Preserve geology-1, continuing
saves, strict guards, immutable inputs, optional Ulti-World, viewer repairs and
unrelated temp/. #9/#11 stay open. Palettes/dikes/minerals/integrations remain
outside this slice. No publication, gameplay improvement or save migration follows.

Only this decision document changes now. Newly run local verification is limited
to document/link/diff checks; existing tests were read only. No builds, evidence
reruns, Java/Minecraft/TD/provider/model execution, save access, new seeds/terrain,
native/process-control/preflight/socket work, monitoring, runtime roots, ledgers
or approval flags. Push only this document, inspect exact final-head CI and report
its actual result in the handoff; normal remote CI builds/offline checks are
separate evidence. Keep PR62 draft/unmerged. Stop after the decision.

## Ready-to-run next-slice prompt (not authorization from this task)

> Work in this repository on codex/retained-navigation. Read AGENTS.md and
> docs/td-inspection-workflow-decision.md; reconcile local/GitHub/main/branch and
> exact-head CI, stopping on unexpected tracked changes or scope conflicts.
> I authorize only the independent OFFLINE static inspection-card prototype
> within the six-new-file boundary and acceptance checks in that decision.
> Check local Pillow/font availability first; do not install/download or build
> infrastructure. Read only the two named pinned archives; do not execute old
> builders/exporters. Run only the new card tests and document/link/diff checks;
> generate and inspect the two new card PNGs using local raster-image inspection.
> This authorizes neither access/rendering/transcoding of the blocked companion
> nor a browser retry, server, rehost or alternative-surface workaround. Preserve
> every existing file, frozen navigation-3 byte/status/consumed slot, historical
> failures, PR59 negative contacts, geology-1, save safety, strict guards, immutable
> inputs, optional Ulti-World, temp/ and all #9/#11 gates. No Java/Minecraft/TD/
> provider/model execution, save access, new seed/terrain, native/process-control/
> preflight/socket work, monitoring, runtime roots, ledgers or approval flags.
> Record data tests, static visual observations, comprehension and runtime unknowns
> separately. Stop on input mismatch, missing renderer/font, failed fit/visual
> gate or scope expansion; do not repair old artifacts or proceed to integration.
> Commit/push only the six named files, check exact final-head CI, keep PR62 draft
> and unmerged, and stop after reporting this prototype's actual result. No player
> study, in-game adaptation, runtime validation, adoption or merge is authorized.
