# Independent static inspection-card prototype

## Completed bounded offline selection model, 2026-11-15

Starting local HEAD, origin branch ref and live GitHub PR62 head matched
`5775f03909b25fdeb7e007117240520fae1f1768` on `codex/retained-navigation`.
Local main/origin/main and live PR base matched
`513c4ca1e950969453faf52723f7ee68c7d6c329`. No tracked changes were present.
Starting-head [CI43798281770](https://github.com/WilyJEB/geologic-variation/actions/runs/43798281770)
passed: reused remote build/offline evidence, not runtime acceptance.
PR62 was confirmed open, draft and unmerged. The earlier static-card completion
and historical failures below remain intact; its proposed selection step is now
implemented within the user's separately authorized three-file scope.

[Selection model](../scripts/td-inspection-selection.py) gives each
`InspectionSelection` instance exclusive ownership of its own selected site.
Construction reads the existing card model's hash-pinned archives through `load`;
it imports definitions without calling the builder, renderer or main entry point.
There is no global selection, UI event adapter, player/HUD state or persistence.
The two archives remain read-only. All 2,401 retained sites still abstain from
actual geological interpretation. This provides a deliberate selection contract
for a future card interface; player usefulness and interaction remain untested.

| Operation/input | State | Stored request and observation |
| --- | --- | --- |
| Construct or `reset()` | `empty` | Neither coordinates nor site; reset is idempotent. |
| `select(x,z)` at an exact retained integer site | `selected` | Exact native coordinates and existing full-precision card-model Site. |
| Integer coordinate inside the closed retained extent but off its lattice | `gap` | Requested coordinates; no site or observation. |
| Integer coordinate outside that extent | `exterior` | Requested coordinates; no site or observation. |
| Non-integer input, including bool/float | `invalid` | Neither coordinates nor site. |

The closed extent is x=2688..5760, z=10880..13952, with spacing 64 in each
axis. No rounding, interpolation, proximity radius or nearest-site inference is
used. Every selection request clears the previous card first, including invalid
and unsupported requests; a lookup exception propagates with the owner left
`invalid`, without stale observation. Constructor input errors propagate without
creating a usable owner. Returned frozen state records contain defensive copies
of the Site/history dictionaries so external mutation cannot change owner data.
Separate owners never share selections; reset does not choose a default site.
Coordinates describe retained native samples, not Minecraft positions or Y.

New verification was limited to [seven focused selection tests](../scripts/test-td-inspection-selection.py)
and document/link/diff checks:

```powershell
& 'C:/Users/digif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/test-td-inspection-selection.py
```

All seven passed. Coverage includes exact existing card records/full precision at
the three pinned example sites; every retained site's row/column and abstention;
closed edges, gap/exterior transitions without stale cards; invalid input;
idempotent reset/reselection; independent owners and defensive copies; corrupt
and missing pinned archive rejection and lookup-error clearing. No static-card
test suite, image generation/review, historical exporter or evidence rerun was
performed. Existing card PNG/JSON bytes and sources are unchanged. The completed
static review below is reused evidence; no new visual/keyboard/player/Minecraft
acceptance follows from these model tests. Final-head CI is reported separately
with the delivered commit; CI remains remote build/offline evidence only.

Only the two new selection files and this report change. Completed static cards,
blocked companion, viewer repairs and unrelated temp/ remain preserved.
Navigation-3 remains consumed, zero remaining, **INCOMPLETE**, with all 18 live
acceptance rows unverified. Historical failures and the complete #9/#11 gates
below remain unchanged. Geology-1, continuing-save safety, strict guards and
immutable inputs remain intact. No local build, historical execution, Java,
Minecraft, TD/provider/model execution, save access, new terrain/seeds, native or
process-control/preflight/socket work, monitoring, runtime roots, ledgers,
approval flags, in-game adaptation, player study, adoption or merge occurred.

Smallest next authorization: one bounded offline review of how an eventual card
interface would issue explicit select/reset operations and display these five
states, using only the existing retained examples. No interface implementation,
game integration or execution is authorized by this proposed next step.

## Completed bounded glyph-bearing correction, 2026-11-15

This section supersedes the current-status wording in the historical attempts
below; their failures remain preserved. Starting local/GitHub PR62 branch HEAD
was `aaf371076e551805b8ce9bf60ed37b3a55e0b0a7`; main/base was
`513c4ca1e950969453faf52723f7ee68c7d6c329`. No tracked changes were present.
Exact starting-head CI43656148334 passed; this is reused remote build/offline
evidence. PR62 remains open, draft and unmerged. Other untracked viewer repairs
and unrelated `temp/` are preserved.

The supplied measurement-only diagnostic found Arial 17px text
`Authored history / invented` at (40,291) had ink bounds (39,291,241,307),
outside allocation (40,58,368,646): a negative left bearing, not demonstrated
vertical overflow. The one authorized correction measures each line's actual
ink bounds at origin, subtracts its left/top bearings from the drawing origin,
and checks the resulting actual bounds with the unchanged strict predicate.
No tolerance, allocation expansion, prose removal or type reduction was used.
The 360x760 cards, minimum 16px text and reserved caveats remain intact.

Using the bundled Python, Pillow and hash-pinned Arial documented below:

```powershell
& 'C:/Users/digif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/build-td-inspection-card.py
& 'C:/Users/digif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/test-td-inspection-card.py
```

The builder passed and produced [semantic JSON](evidence/td-inspection-card.json),
[1200x900 PNG](evidence/td-inspection-card-1200.png) and
[1600x1000 PNG](evidence/td-inspection-card-1600.png). All seven focused tests
passed: exact archived semantics independently of rounded text; all 2,401 sites'
abstention and unsupported lookups; corrupt/missing input rejection; distinct
tokens/shared event and negative contact finding; PNG dimensions, strict bounds,
caveat reservation and non-overlap; missing-glyph/overflow rejection; and exact
saved-output reproduction. JSON includes complete tokens, records, provenance,
rounding, renderer identity and every text bounding box. No historical builder
or exporter was run. Only the two pinned archives were read as data inputs.

Actual static-image review: both independently authored PNGs were opened with
the local raster-image inspection tool at their native dimensions. Headings,
wrapped bodies, coordinates/rounded elevations, the regional trend/clamp,
reserved unknowns and bottom comparison/unsupported examples are legible.
No clipped text or visual overlap was observed. Cards use the same fixed size
at both canvas sizes; the larger canvas intentionally retains unused space.
The caveat divider and whitespace separate unknowns from the main narrative.
This is a static visual observation, distinct from automated layout checks.

No player study has been conducted. Whether players understand these distinctions
remains unverified. Companion presentation remains blocked/unverified; no access,
rendering, transcoding or rehosting was attempted. Minecraft fonts, GUI scale,
selection, focus, HUD coexistence and live-world linkage remain unverified.
Navigation-3 remains verbatim: consumed, zero remaining, **INCOMPLETE**.
All historical failures and every #9/#11 validation/performance/adoption/save-safety
gate below remain unmet; geology-1, continuing saves and strict guards are unchanged.
No local builds, runtime execution, in-game adaptation, adoption or merge occurred.

Smallest useful next step: separately authorize a bounded implementation of an
isolated offline selection model using these same retained records, with tests
for exact-site selection, unsupported states and explicit ownership. This would
prepare deliberate card selection for later game integration; it establishes no
interaction or gameplay acceptance. It requires new scope because the present
authorization ends at these six static prototype files. No next step is authorized
by this report or a proposed prompt.

## Historical failed attempts (preserved)

2026-11-15. The first layout gate failed. This is an incomplete implementation,
not an accepted prototype. No PNG or semantic-output JSON was written. No static
image review, player study or Minecraft acceptance occurred. Do not treat the
builder's presence as a successful card implementation.

## Authorized bounded revision: failed fit again

The user subsequently authorized one bounded text/layout revision under the same
allocation, minimum type size and reserved caveats, with another mandatory stop
on fit/visual failure. The new card prose/headings were shortened while retaining
the semantic categories and caveats. A focused seven-test file was authored.
The first execution of this revision used the same interpreter/command below and
again exited 1 with `ValueError: Text fit failed: section heading`, in
`text_block` called from `sheet`, before either sheet completed or outputs were
written. No further layout revision or execution followed. The exception does
not retain the precise offending heading or bounding box; its cause is not
established beyond the failed bounds predicate. Do not assume vertical overflow
or conclude the fixed allocation cannot fit the required semantics from this
message alone. The focused tests were not run after the mandatory stop.

The retained files are now the incomplete builder, focused tests and this report;
there is still no six-file deliverable, PNG review, commit or push. The historical
first-attempt account below remains preserved. Smallest next useful step is a
bounded diagnostic of the new layout's failing text/bounds, with no historical
execution and no relaxation of the contract, before another rendering revision.

## Reconciliation and renderer

Read [AGENTS.md](../AGENTS.md) and the
[six-file decision contract](td-inspection-workflow-decision.md).
Local branch is `codex/retained-navigation`; local HEAD, origin branch ref and
live GitHub branch/PR62 head matched
`aaf371076e551805b8ce9bf60ed37b3a55e0b0a7`. Local main, origin/main and live
GitHub main matched `513c4ca1e950969453faf52723f7ee68c7d6c329`.
No tracked changes were present initially. Existing untracked viewer repairs
and unrelated `temp/` were preserved.
[PR62](https://github.com/WilyJEB/geologic-variation/pull/62) was open, draft and
unmerged. Exact-head [CI43656148334](https://github.com/WilyJEB/geologic-variation/actions/runs/43656148334)
was completed/success: reused build/offline evidence only.

No runtime-discovery tool was exposed. Targeted inspection of the documented
primary runtime dependency location found an existing usable interpreter:
`C:/Users/digif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
Python is 3.12.14, MSC v.1944 64 bit AMD64; Pillow is 12.3.0.
No environment was created, modified or installed; no download was needed.
Font: `C:/Windows/Fonts/arial.ttf`, Arial Regular, SHA256
`edfbd22a3d088fc2f5d7c79b8c9c732df6dc878a60f0a80be0f92a3c7a634404`.
The builder checks nonzero glyph IDs in the font's Unicode cmap for every
displayed character. Font loading and the printable ASCII prerequisite passed;
all text reached before the fit failure also passed glyph checks. No claim is
made that a complete rendered prototype passed inspection.

## Inputs and actual attempt

Only these archives were opened as data; no archived executable, historical
builder/exporter or companion HTML was executed or rendered:

| Input | SHA256 |
| --- | --- |
| `td-story.zip` | `fec51d36faeb1d8b99e7624c2daab5cbd2b614227c6df9527dfe0f7c7954da47` |
| `td-region-visual.zip` | `f939c32cefe3a4e4f06320c056dcf5cb33e96ab6c50dcc76cc9640f297b1f1d8` |
| PR59 `result.json` | `9caff8648cb2165bf0d0ed7c3e9fd70ce6759d28b0c891b9fd36de1551fac650` |
| PR58 `result.json` | `d0853fba10ca350e353d9a2786a6362d99f80363aa7b12a071d470b89e56819c` |
| Shared `input/visual-data.json` | `8dc1e0a9f98edd1dc6b2ce74cc1d795c117c15feb9503b0260a5c5ef23a701d6` |

Archive/result/input digests and baseline/shared-input references passed the new
loader's checks. The three selected records were mapped from archived data, with
surface/deep history-token equality checked. Cards 2/3 retained different
identities/tokens and the same cover-preservation event. These are loader checks,
not a completed independent test suite or visual acceptance.

The only new authoring execution was:

```powershell
& 'C:/Users/digif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/build-td-inspection-card.py
```

It exited 1 with `ValueError: Text fit failed: section heading` in `text_block`,
called by `sheet` while laying out the first 1200x900 sheet. Supported cards were
allocated 360x760; content was bounded above a separately reserved caveat area.
A section-heading bounding box exceeded that content allocation. No second fit
attempt followed; the contract was not relaxed. Output writes occur only after
both sheets finish, so neither PNG nor JSON was produced. The focused test file
was not created or run before this stop. Only the incomplete builder and this
failure report are retained; there is no six-file deliverable to commit/push.

## Evidence boundaries and remaining gates

Automated evidence: the prerequisite and pinned-input/loader checks above passed;
the first layout gate failed. Document/link/diff checks apply only to these new
source/report files. No complete card-data/layout test suite passed.

Static visual evidence: none. Neither requested PNG exists or was inspected.
The companion's browser presentation remains blocked and unverified; no browser
retry, transcode, server, rehost or alternative-surface workaround occurred.

Player comprehension: no player study has been conducted. The intended benefit
of distinguishing terrain observations, seeded substrate, invented history and
unknowns remains a hypothesis. Minecraft runtime acceptance remains unverified;
no game-font/GUI-scale, selection, focus, HUD or live-world claim follows.

Navigation-3 remains verbatim, consumed, zero remaining and **INCOMPLETE**; all
18 live acceptance rows remain unverified. Historical failures remain failed,
including PR51 coarse drift, PR52 matching support, PR57 pressure reduction,
height/residual and #5 final-block failures. PR59's negative contact finding is
preserved. PR54's four launches remain exhausted; its runtime used 4a2fa1c,
final capture remains compile-only and historical arrays/indices/ULPs unknown.
Geometry/support/uncertainty, numerical reproducer and multi-field joining remain
unresolved. Previously inspected controls/seeds remain development data.

Preserve geology-1, continuing-save safety, strict guards, immutable inputs,
optional Ulti-World and every #9/#11 gate. Carried gates include fresh frozen
validation across new seeds/scales 1/6/signed coordinates/contrasting terrain and
contacts with fixed/paired coverage; alternating paired startup/cold/warm/full-
route performance; immutable versioned adoption/new-world-only selection;
bidirectional continuing-save rejection; original-artifact restoration/reopen;
full snapshot/block/persisted-container preservation. No local builds, TD/model/
provider/Java/Minecraft execution, save access, terrain generation, unrelated
evidence reruns, native/process-control/preflight/socket work, monitoring,
runtime roots, ledgers or approval flags were used. No integration, adoption,
player study or merge occurred.

Smallest useful next step: separately authorize one bounded revision of the new
card text/layout, retaining every semantic requirement, minimum 16-pixel text,
360x760 allocation and reserved caveats. Then complete focused tests and both
static-image reviews. This needs new authorization because the current slice
explicitly stops at a failed fit gate. Do not add another planning document or
change historical artifacts to resolve this layout failure.
