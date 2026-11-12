# One useful retained-landscape prototype

Decision, 2026-11-12: propose one offline **“Why this region?” walkthrough**,
with three fixed example cards beside the existing PR58/59 maps. It should let
a player trace an observed landscape cue through an explicitly invented seeded
history to a conceptual regional surface/deep relationship. Do not change the
geological construction. This report implements nothing and grants no execution
authority. More monitoring is not a prerequisite.

## Basis and reconciliation

Local HEAD, refreshed origin/codex/retained-navigation and the current PR62
decision agree at `4a0c6421bfb5e2530ccc92e79b5f94bc5599b7f8`.
Main/origin/main remains `513c4ca1e950969453faf52723f7ee68c7d6c329`.
[Starting-head CI43294437449](https://github.com/WilyJEB/geologic-variation/actions/runs/43294437449)
passed; this is reused build/offline evidence. PR62 is draft/unmerged and stays
so. The [current native decision](windows-staged-helper-native-decision.md)
stops at resource accounting; its separate infrastructure gate is not the next
product gate. [Navigation-3](td-navigation-3-outcome.md) remains consumed,
zero remaining, INCOMPLETE; its 18 live checklist rows remain unverified.

Read AGENTS.md, that decision and carried gates, [observation history](td-observation-history.md),
[axis controls](td-axis-numerical-controls.md), their portable manifests/archives
and frozen [axis](td-axis-numerical-protocol.md)/[window history](td-window-history-protocol.md)
protocols; [PR58 report](td-region-visual.md)/[protocol](td-region-visual-protocol.md),
[PR59 report](td-story.md)/[protocol](td-story-protocol.md), retained result JSON,
HTML sources and relevant rendering/build components. No new field was inspected.

New visual inspection: exact retained [PR58 PNG](evidence/td-region-visual.png),
[PR59 PNG](evidence/td-story.png) and [historical panel screenshot](evidence/td-navigation-panel-cover.jpg).
The PNGs are separate renderings, not HTML screenshots. The screenshot shows a
historical full panel over Minecraft scenery; that background is not retained TD
terrain and does not establish movement or navigation acceptance. The available
browser interface reported no in-app browser and an empty browser inventory.
Consequently HTML layout/click behavior and scripts-disabled browser rendering
were not newly observed. No local server or browser workaround was introduced.

Read-only ZIP/result inspection confirmed the three example IDs below. Source
inspection counted 4,802 pre-script circles in story HTML and the existing local
viewer repair, but zero in frozen PR58 HTML (its two SVG containers are populated
by JavaScript). That establishes a structural fallback difference, not browser
acceptance. Preserve the untracked repairs `docs/td-region-viewer.html` and
`scripts/build-td-region-preview.py` separately; do not rewrite frozen viewers.

## What the display establishes, and what a player can read

| Meaning | Retained evidence and display assessment |
| --- | --- |
| Observed terrain/data | Seed8675309, 49×49 actual elevation sites, native spacing64, x2688..5760 and z10880..13952. The point colours make the curved high/low pattern visible. They are TD elevations, not Minecraft Y. Original half-open query is [z10880,x2688,z13953,x5761]; 9,440,928 original values are unavailable. |
| Authored synthetic geology | PR58 seeded IDs/history tokens and H/O tags are invented; row centroids bend vertical contacts while horizontal seams stay fixed. PR59 uses the broad planar trend for an authored, clamped tilt and per-band elevation contrast for stripping/cover language. Neither recovers real history or assigns actual rock. Surface and deep share one inherited identity/token; no depth/interface is observed. |
| Uncertainty and abstention | White gaps/exterior have unknown heights; between-point geometry and observation error are unknown, never zero. Geological interpretation abstains at all2,401 sites. PR58 difference mode additionally lacks full stencils at192 edge sites. Contact lines and tints fill conceptual space, not missing terrain. |
| Player comprehension | A player can see where high/low sampled terrain lies and which conceptual region contains a point. The panel's MEASURED/AUTHORED/UNKNOWN labels and shared token are useful provenance. H1→O0, signed IDs, full hashes, native coordinates and dense small text do not themselves explain why the landscape affects the story or what surface/deep means. Recognition and usefulness have not been tested with players. |

Specific strengths: identical point support makes comparisons honest; dashed
contacts differ from coloured observations; stable regional identities and shared
surface/deep references give a coherent conceptual history. PR59's small lower-left
exposure band is easy to locate against the higher elevations. Its event names
are more readable than PR58's H/O tags. Story HTML already embeds both maps and
its history table before scripting, so a static-first presentation is feasible.

Specific failures: PR58's repeated top-row H1→O0 tags obscure why distinct IDs
exist. Its curved contact is locally recognizable but the fixed horizontal seam
is visibly arbitrary. PR59 removes that seam yet straight oblique bands cross
the curved elevation pattern; the active -0.5 clamp and authored phase/width
partly control their appearance. **PR59 did not establish better landscape-related
contacts.** Both lower-mean bands receive cover preservation; their contact has
no demonstrated geological necessity. These negative contacts stay negative.
Neither dense hatching nor a disclaimer explains the causal chain on its own.
The panel screenshot reserves much space for raw coordinates/tokens; the reader
must assemble evidence, seeded choice and interpretation across several lines.
Frozen PR58's script-built maps also leave blank containers without scripting.

## One proposed implementation slice

Build one separately named offline companion to the existing retained maps:
**“Why this region? Three examples from one retained landscape.”** This is a
player-facing explanation prototype for the addon's eventual inspection view,
not a production selector, new map construction or live HUD change.

Default presentation: the unchanged PR58 terrain illustration and PR59 story
map side by side, three numbered markers on actual retained sites, and all three
matching cards already visible. Optional selection only highlights the matching
marker/card in both maps; ordinary fragment links work without JavaScript.
Keep observed dots, dashed authored contacts and white gaps visually distinct.
Each card follows the same reading order:

1. **Observed here:** exact native coordinates and retained elevation, followed
   separately by the already computed whole-field trend and band mean contrast.
   Say explicitly that the band average is not this point's height.
2. **Seeded identity:** existing ID and invented substrate tag, with full token
   available in secondary provenance text. Do not invent rock names for A/B/H/O.
3. **Authored history:** inherited substrate → conceptual tilt → exposure or
   cover, explicitly labelled “one invented history influenced by these cues.”
   State that the observed trend influences orientation; relative band mean
   influences event choice; seed fixes identity/substrate. Keep clamp visible.
4. **Regional consequence:** a simple labelled conceptual surface/deep pair:
   surface exposure/cover and inherited deep substrate share the same token.
   No vertical depth scale or geological cross-section geometry.
5. **Unknown:** real rock, age, dip, cover thickness, erosion and true history
   are unconfirmed; between-site terrain is unknown. Keep PR59's negative
   contact comparison beside the maps, not hidden in provenance.

Fixed retained examples only (row/column zero-based, native coordinates):

| Card | Site | Existing PR59 result | Purpose |
| --- | --- | --- | --- |
| 1 | r46,c4; x2944,z13824 | ID-3; band contrast +2693.825260m; greater stripping/exposure | Explain a higher-mean band's authored exposure, without calling it observed erosion. |
| 2 | r0,c0; x2688,z10880 | ID-2; contrast -220.981686m; cover preservation | Show the same deep identity beneath conceptual cover; edge stencil unavailable in PR58 difference mode. |
| 3 | r0,c48; x5760,z10880 | ID-1; contrast -275.499937m; cover preservation | Show a distinct seeded region can share an event, so event names do not justify its contact. |

These are existing navigation-route examples, newly cross-checked against retained
PR59 IDs, not a new search. Copy exact PR58 membership/history at the same sites
from its result. No extra example sites, alternate interpretations or new scores.
White gaps remain part of the display and never acquire inspection records.

Likely file boundary for that later slice: add only
`scripts/build-td-region-explainer.py`, `scripts/test-td-region-explainer.py` and
generated `docs/td-region-explainer.html`; add its bounded test invocation to
`.github/workflows/build.yml`. Read immutable inputs from
`docs/evidence/td-story.zip` and `docs/evidence/td-region-visual.zip`; use
`scripts/build-td-story.py`'s embedded-SVG presentation as reference, without
editing or executing its export path. Include input/result digests and the
three-card data in the standalone output. Do not change old HTML/ZIP/JSON/images,
their builders, the preserved local viewer repair, RetainedMap/RetainedMapScreen,
navigation diagnostics, runtime resources or production sources. A later in-addon
adaptation is a separate decision after this explanatory view is reviewed.

## Offline acceptance and stop

For the proposed slice, require exact input digests and exact archived heights,
IDs, tokens, contrasts and event strings for all three cards; shared surface/deep
tokens must match. Label site values versus regional summaries separately.
Test that unsupported space cannot produce an observed record. Check no network
dependency, no interpolated heights and no new geological classification.

With scripts removed/disabled, both maps, all observed dots, contact legend,
three markers/cards, conceptual surface/deep pairs, unknowns and negative-contact
finding must remain present and readable; selection cannot hide essential content.
Perform real-browser visual checks at1200×900 and1600×1000 where available,
including keyboard fragment navigation and scripts disabled. Source/DOM checks
alone do not establish browser readability. If unavailable, report that check
unverified and stop rather than building serving infrastructure. Check text is
readable without hover or colour alone. Passing offline data checks is distinct
from subjective visual judgment, player comprehension and live addon acceptance.

Stop after that one view and three cards have been checked/reviewed. Stop earlier
on an input mismatch, required missing record, need for new terrain, changed
construction, claimed real geology, or work outside the named files; report the
gap without substituting another design. No framework or monitoring work follows.

This review changes only this report. Verification is document/link/diff checking
and read-only retained result/HTML inspection; no unrelated strict evidence chain
is rerun for guidance. New-head CI must pass before handoff (its normal remote
builds/offline tests are not local runtime execution or acceptance). Frozen
navigation-3 root, sources/artifacts, consumed slot, approvals, ledger and partial
evidence are untouched, as are viewer repairs and unrelated temp/.

All carried gates remain: PR51 Paired coarse drift, PR52 Actual matching native
support changed, PR57 pressure reduction, height/residual and #5 final-block
failures remain failed; geometry/uncertainty, numerical cause/reproducer and
multi-field joining are unresolved. PR54's four launches are exhausted; it ran
4a2fa1c and final capture instrumentation is compile-only; historical missing
arrays/indices/ULPs stay unknown. Fresh validation needs separately authorized
new seeds, scales1/6, signed coordinates, contrasting terrain/multiple contacts,
fixed coverage and paired shared cells/scales. Integrated performance needs new
alternating paired CPU startup/cold/warm/full-route evidence. Adoption needs
immutable versioned identity, explicit new-world-only selection, bidirectional
continuing-save rejection, exact original-artifact restoration/reopen and full
snapshot/block/persisted-container preservation. None is satisfied by these maps.
Geology-1, continuing worlds, production guards, immutable inputs and optional
Ulti-World remain unchanged; #9/#11 stay open. No live player recognition,
navigation, shutdown, runtime/save acceptance or publishability is claimed.

**Exact next authorization gate:** explicitly authorize ONE bounded OFFLINE
implementation of this three-card retained “Why this region?” companion within
the named file boundary and acceptance checks. That would permit only offline
presentation work using these inputs; no Java/Minecraft/TD/provider/model run,
save access, native/process-control/preflight/socket work, new runtime root,
ledger, approval flag or authorization file. It grants no later live validation,
production adoption or merge authority. This review does not supply that approval.
