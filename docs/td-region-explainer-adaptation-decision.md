# Retained region explainer: adaptation decision

Decision, 2026-11-12: **2 — require one bounded presentation/readability check
before adaptation preparation.** The repaired companion supplies a credible
explanatory structure, but actual standalone browser readability and navigation
remain unverified. This is a presentation gap, not a demand for more monitoring,
new terrain or a geological reconstruction. No adaptation is implemented or
authorized by this review.

## Reconciliation and scope

Expected/local HEAD and refreshed `origin/codex/retained-navigation` agree at
`f378a0ca0239f5ab9e7ddc52baa9526bc4493932`. Local main and origin/main agree at
`513c4ca1e950969453faf52723f7ee68c7d6c329`. No unexpected tracked changes were
present. Existing untracked `docs/td-region-viewer.html`,
`scripts/build-td-region-preview.py` and unrelated `temp/` were preserved.
[Starting-head CI43330044531](https://github.com/WilyJEB/geologic-variation/actions/runs/43330044531)
completed successfully: build/offline verification, not runtime acceptance.

Read AGENTS.md, the [prototype review](td-visual-prototype-review.md), actual
[standalone companion](td-region-explainer.html), its
[builder](../scripts/build-td-region-explainer.py) and
[tests](../scripts/test-td-region-explainer.py), the current PR62 decision and
[native decision report](windows-staged-helper-native-decision.md),
[navigation-3 outcome](td-navigation-3-outcome.md),
[observation history](td-observation-history.md) and
[axis controls](td-axis-numerical-controls.md). This is not a continuation of
the numerical/performance experiment; no frozen protocol or evidence chain was
rerun. PR62's body still leads with the historical `4a0c642` native-preparation
STOP decision, whereas its branch now contains the companion and reading repair.
These are separate decisions: the native resource-contract obstacle remains;
it does not block reviewing the explanatory concept. GitHub reports PR62 open,
draft and unmerged; #9 and #11 remain open.

## What the explanation means

The following are source-based findings and editorial judgments, not browser or
player observations.

| Layer | Assessment of the repaired companion |
| --- | --- |
| Exact site observation | Each card leads with one fixed row/column, native x/z and exact retained elevation, explicitly TD elevation rather than Minecraft Y. The three markers refer to existing sites, not interpolated terrain. |
| Regional summary | A separate heading explains band mean relative to the whole-field mean, with site count. Rounded primary values are separated from exact provenance. A band average is explicitly not the marker's height. |
| Seeded identity | ID and abstract A/B substrate are described as seeded choices, not measured rock names. Full tokens and archived PR58 records are secondary. Different identities do not establish different real rocks. |
| Authored history | Inherited substrate → conceptual tilt → exposure/cover is explicitly one invented history influenced by cues. Regional mean influences event choice; broad trend influences orientation; seed fixes identity/substrate. Exposure and cover are not observed erosion or deposits. |
| Surface/deep continuity | The labelled conceptual pair shares an inherited identity/history record. Deep substrate is not a sampled subsurface layer. No depth scale, thickness or interface geometry is observed. |
| Unknowns | Real rock, age, dip, cover thickness, erosion and true history remain unconfirmed; gaps, exterior terrain and observation error remain unknown, never zero. Cards 2/3 retain the unavailable PR58 difference-mode edge stencil. |
| Geological abstention | All 2,401 sites abstain from actual geological interpretation. Conceptual contacts and tints do not fill missing observations or certify geology. |

The reading repair is useful editorially: repeated semantic headings establish
a traceable order; prose leads and hashes follow. The plain-language trend says
the fitted field falls with increasing native x and rises with increasing native
z at roughly equal rates. It distinguishes this whole-field fit from local
slopes. The ratio of about −1.01 influences conceptual orientation, but the
active ±0.5 limit fixes authored tilt at **−0.5**. Seeded phase and chosen width
also shape contacts. This is an appropriately qualified explanation of influence,
not a claim that terrain uniquely dictates the bands.

The explicit Cards 2/3 comparison is essential: ID −2 and ID −1 have distinct
identities/tokens but share cover preservation because both band means are below
the field mean. **Matching cover events do not establish geological necessity
for their contact. PR59 did not establish better landscape-related contacts.**
Its oblique bands still cross curved relief; PR58 retains an arbitrary horizontal
seam. These negative findings stay beside the maps rather than being buried in
provenance. Neither event names nor a polished explanation repairs the contacts.

Source layout suggests remaining presentation risks. Both requested widths are
above the 950px breakpoint, so three long cards remain side by side. Two maps,
legend, negative finding and trend precede the cards, creating a long reading
path. The card's exact values, PR58 comparison and unknowns may compete for
attention. SVG label density and edge markers need visual inspection. CSS
wrapping, numbered markers, focus outlines and fragment target borders are useful
intentions; their presence does not prove legibility, clipping behavior or
keyboard usability. No repair is made here.

## Browser observations and missing evidence

The available inventory exposed an in-app browser with no open tabs. A direct
attempt to open the actual standalone HTML using its local `file:` URL was
rejected by the browser's URL security policy, which permits only HTTP/HTTPS.
No HTML rendered. No server, installation, alternate browser or URL workaround
was introduced.

Consequently **both 1200×900 and 1600×1000 remain unverified**, including maps,
markers, cards, legends, wrapping, caveat placement, keyboard fragment navigation,
focus visibility, return navigation and scripts-disabled rendering. The HTML
contains static SVGs/cards and no scripts; its builder/tests describe static
content and fragment guarantees. Those source facts are not rendered acceptance.
Tests were read, not rerun. Prior CI is reused evidence only.

There is **no player-comprehension evidence and no player study**. A reader has
not demonstrated that they can distinguish a site height from a band average,
invented cover from observed cover, or shared history from measured depth. No
gameplay improvement, live inspection usability, navigation, normal shutdown,
runtime acceptance or publishability is established.

## Smallest useful eventual adaptation

The concrete player-visible purpose would be to answer, for a selected supported
site, “what was observed, what did the seed choose, what story was authored, and
what is unknown?” A compact inspection card with one selected marker and the
same semantic headings is the smallest useful concept. Preserve the Cards 2/3
comparison as an explicit comparison example, not a rule that every contact has
a terrain explanation. This could make provenance easier to inspect; usefulness
to players remains a hypothesis.

This decision does **not** recommend starting adaptation preparation yet and
does not establish an implementation file boundary. After the presentation gate,
a separately authorized preparation decision should determine a minimal boundary
from the current screen/data ownership. It must preserve exact site support,
site-versus-summary labels, active clamp, conceptual surface/deep meaning,
universal abstention and the negative-contact comparison. Unsupported space must
produce an unknown result, never a fabricated observation. Essential explanation
must be available without hover or colour alone; selection must not conceal
caveats. No production selector or geology algorithm change follows.

That later preparation can assess content mapping, retained-record equality,
unsupported-space behavior and interaction design offline. Actual Minecraft
scale, input/focus behavior, HUD coexistence, movement/site correspondence and
runtime lifecycle require separately authorized live validation. Continuing-save
adoption and player comprehension require their own evidence and authorization;
neither is a consequence of browser readability.

## Exact next authorization gate and stop

Explicitly authorize **one bounded presentation-only check of the unchanged
standalone companion**, on an existing surface permitted to open the actual file,
at 1200×900 and 1600×1000. Check all maps/markers, legends, card wrapping and
caveats; use keyboard links to all three fragments and back; inspect with scripts
disabled. Confirm exact observations and regional summaries remain distinguishable,
the active −0.5 clamp and Cards 2/3 finding remain readable, and essential text
does not depend on hover/colour. Record observations and failures in a separately
scoped report. If a permitted surface is still unavailable, retain “unverified”
and stop. This gate grants no serving infrastructure, repairs, monitoring,
in-addon work, live validation or player study. Successful presentation checking
would support another adaptation decision, not automatically authorize one.

Only this report changes. Local verification is document/link/diff checking;
no builds, tests or unrelated evidence exports were run. Report-commit CI must
be checked after push and its actual result reported in the handoff. No merge
is authorized; PR62 stays draft/unmerged.

Navigation-3's complete root, sources/artifacts, consumed slot, approvals, ledger
and partial evidence remain untouched: INCOMPLETE, zero remaining; all 18 live
rows remain unverified. Historical PR51 paired coarse drift, PR52 matching native
support, PR57 pressure reduction, height/residual and #5 final-block failures stay
failed. Geometry/support/uncertainty, numerical cause/reproducer and multi-field
joining remain unresolved. PR54's four launches are exhausted; its execution used
4a2fa1c, final capture remains compile-only, and historical arrays/indices/ULPs
remain unknown. Fresh validation still needs separately authorized new seeds,
scales 1/6, signed coordinates, contrasting terrain/multiple contacts and fixed
coverage with paired shared cells/scales. Integrated performance still needs
alternating paired CPU startup/cold/warm/full-route evidence. Adoption still needs
immutable versioned identity, explicit new-world-only selection, bidirectional
continuing-save rejection, exact original-artifact restoration/reopen and full
snapshot/block/persisted-container preservation. Geology-1, continuing saves,
strict guards, immutable inputs, optional Ulti-World and all #9/#11 gates remain.
No Java/Minecraft/TD/provider/model execution, save access, new terrain, process
control, preflight/socket work, runtime root, ledger, approval flag, infrastructure
or production change occurred. Stop after this review.
