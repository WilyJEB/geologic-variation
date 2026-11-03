# Frozen TD elongated-landform diagnostic protocol

Base: PR #50, ce91c6abdc9793bf14014fd6bf4c6ac689acd934. No production changes.
This protocol and selector must be committed and pushed before new seed inspection.
Previously examined seeds, including 20261103, are development data only.
Development: 8675309. Fresh held-out: 2026110317 and -2026110319. Scales 1/6
are paired native observations, never independent coarse observations.

Screen the existing fixed 9x9 signed native lattice (-64..64, step 16).
Four longitudinal lattice directions: x, z and both diagonals. At each center,
require both perpendicular neighbors to be at least 50 metres lower (ridge) or
higher (basin). This is an explicit morphology resolution margin, unrelated to
geology-1 cutoffs. Report both drops/depths, never curvature alone. Rank by the
smaller margin, then row, column, axis; confirm at most two distinct centers per
kind. At five longitudinal stations (-2..2 native cells), require the same
two-sided extremum and margin. Length is 1024 native pixels for axial features,
1024*sqrt(2) for diagonal features; shoulder separation is 512 or 512*sqrt(2).
Require longitudinal center range <= twice the smallest cross margin and maximum
residual from endpoint linear interpolation <= that margin. Along-axis tilt is
allowed within those bounds. Cross-axis slopes are not detrended into extrema.
Saddles failing any station abstain. Strongly curved or off-axis features can be
missed: no orientation interpolation, curved tracking or unbounded search. Retain
all failed attempts; no claim of coverage outside four orientations. Opposite-kind
winning centers coinciding abstain. Center uncertainty is a whole coarse cell
(+/-128 native pixels per axis); means do not locate a fine crest pixel.

Select at most one supported ridge and one basin per seed. If a kind has no
supported candidate, retain its highest-ranked attempted candidate as a visibly
failed diagnostic fallback, never as coverage success. Fine-validate all 15
cells of each feature: five longitudinal stations and both cross shoulders at
every station. Query native cell centers in world coordinates. Full 256x256 fine
cell means match coarse central-cell support, but remain separate model products.
Also retain 25 quantized heights from the containing 256-world-block tile at each
query and province anchor, and matched anchor native cells. Existing probe also
returns fixed-grid comparisons; those are retained, not a newly proposed policy.
Fine morphology applies the same declared 50 m/range/residual rules separately
to native-cell means and scaled-tile means. Tile support at scale 6 is smaller;
tile failures cannot be hidden by native-cell success. Coarse neighborhood range,
native fine-cell relief and tile relief remain distinct measurements.

Fixed fine coverage: screen indices 0,20,40,60,80 (diagonal transect).
Selected contrasts: existing ocean/coast/lowest/highest land plus median land;
missing strata are reported, never cause more search. Twelve existing signed
boundary points cover four coarse/grid edges and two actual province contacts.
These groups are descriptive, not a population sample. Fine observations deduplicate
locations within each fixture; group memberships remain explicit. Clear both
diagnostic LRUs and reverse all unique observations, requiring exact evidence
equality. TD/provider caches remain warm; this is not fresh-process final-block
determinism. Run the existing coarse concurrency/129-entry eviction and oracle
suite. Native cache stays <=128; do not claim eviction unless actually exercised.

Limits per fixture: 81 screen requests, <=20 station confirmations (five per
candidate), <=52 unique fine comparisons (30 feature +10 coverage/contrast +12
boundary), then <=52 reversed comparisons. Six serial JVMs, each 6 GiB heap,
startup <=360 s, each command <=300 s, fixture <=45 min, total <=4 hours.
Enforce <=12000 newly computed windows per fixture after startup, >=1 GiB free
before launch and >=512 MiB during collection. Stop on resource failure; do not
silently weaken gates or enlarge the search. Immutable TD/models are linked;
copy addon/probe. Clean only stopped new fixtures' regenerable ONNX caches.
Preserve shared inputs, original template and unrelated temp/.

Coverage acceptance requires BOTH held-out seeds to supply a distinct ridge and
basin passing coarse and matched-native fine rules, with scaled tiles passing at
both scales. Any missing/failed feature keeps TD coverage insufficient. Report
development and held-out separately, actual deduplicated public requests and new
windows, boundary jumps, shared-cell coherence and paired native hashes. No
statistical independence claim. Smallest supported policy is actual-target point
diagnostics; extend to supported straight-feature diagnostics only if this entire
coverage gate passes. Otherwise abstain from extended-feature interpretation.

No new classifier, rocks, integration or performance claim. Keep explicit seeded
synthetic-prior-1 competing hypotheses, unestablished geological confidence and
stone-selection abstention. Morphology cannot establish geological plausibility.
Reuse PR #47–#50 strict evidence and production-preservation/reopen results;
do not repeat their held-out matrix or call retained checks fresh runtime work.

Future output changes require immutable generator identity, explicit new-world-only
selection, genuine continuing-save rejection in both directions, exact original
artifact restoration/reopen, unchanged snapshots, complete sampled blocks and all
persisted terrain coverage/status/block containers. Never migrate geology-1.
Integrated candidates additionally need alternating paired CPU runs against then
current main on NEW fixtures: startup, genuinely cold tensors, warm sampling and
full chunk routes, with actual requests/new windows. Isolated-query savings do
not imply route savings. #9/#11 remain open; #5's stronger failed assertion stays
failed. Ulti-World remains optional. Palettes/dikes/minerals are out of scope.
