# region-visual-1: frozen single offline design contract

Recorded before implementation/evaluation, on main 4c025b4 (merged PR57),
2026-11-07. Exactly one comparison; no search, replacement design, field
selection, fresh seeds, TD execution or terrain queries. Diagnostic only.

Input: byte-identical visual-data.json from PR57 td-pressure-visual.zip only.
Seed 8675309; half-open native [z10880,x2688,z13953,x5761], 3073 squared
original query; retained 49x49 points at spacing64 including both endpoints.
Missing original query values = 9443329-2401; exterior and between-point
geometry/error unknown. Old candidate labels are provenance, not validated
extrema. Use elevation only. Verify pinned API from retained source/bytecode;
no p5 relief, geological/tectonic layers or error bounds inferred.

## One globally anchored construction

SHA256 UTF-8 strings `region-visual-1|8675309|phase-x` and `...|phase-z`:
first eight hexadecimal digits as unsigned integer modulo2048 give phases.
Global square lattice side2048 native pixels. Seed-only ID (i,j) =
(floor((x-phaseX)/2048),floor((z-phaseZ)/2048)). Half-open cells own their
lower boundaries; floor is mathematical floor, including negative coordinates.
Finite neighborhood = the nine IDs with offsets {-1,0,1} squared. No flood
fill, discovery state, cache, runtime availability or unbounded search.
Region history is SHA256 of `region-visual-1|8675309|history|i|j`:
first byte parity names inherited substrate H0/H1, second byte parity names
later overprint O0/O1. These are abstract invented events, no rock assignment.
Surface and deep history reference the SAME ID/history, not independently
drawn values. Exact canonical decimal integers in all strings.

## The one terrain-informed illustration

For each retained row, weights = h minus that row's minimum elevation.
Compute the weighted mean native x coordinate C (if all weights zero, abstain
for that row and use zero illustrative displacement). This is a descriptive
centroid of sampled elevations above a row-relative baseline, NOT a crest,
ridge, basin, continuous terrain measurement or geological decision.
Displacement w = clamp((C-4224)/2,-256,+256) times min(r,48-r,4)/4.
This fixed authored gain/cap/taper is not calibrated. End rows have w=0.
Connect those row displacements by piecewise linear segments; use w=0
outside the retained z interval. This interpolation invents CONTACT geometry,
never elevations. At most two rows/98 retained heights determine w(z).
Terrain panel ID = (floor((x-w(z)-phaseX)/2048),floor((z-phaseZ)/2048)).
Tie rules are identical. Every horizontal boundary stays fixed; every vertical
boundary shares the same shear. The inverse shear (x,z)->(x-w(z),z)
is continuous/invertible, so whole conceptual cells stay connected without
claiming sampled or viewport-clipped pieces must be connected. Clipping may
split a cell; report actual sample-grid components rather than hiding this.
No strength threshold, class decision or confidence is accepted from this rule.

Both panels use identical retained sites, elevation/difference evidence and
histories; only this bounded x shear differs. Display actual sites, original
query box, conceptual contacts, and universal interpretation abstention.
White gaps have no retained heights; tint/line interpolation supplies no data.
Four-neighbor max absolute height difference uses a five-point cross at64;
192 edge sites lack it. Geological interpretation abstains at all2401 sites.
Observation error remains null/unknown everywhere. Expose sample values,
IDs and histories for inspection and distinguish computed descriptors from
authored gain, history names, lattice and contact geometry.

## Fixed checks and decision

Compute both ID arrays once; report ID counts, per-ID four-neighbor sample
components, changed sites, sampled adjacent-ID transitions, row centroids and
displacements. No parameter alternatives or replacement after seeing results.
Check repeatability, reverse traversal, negative/boundary conventions, finite
support, history identity, exact source hashes and corruption rejection.
Mathematical connectivity is a construction property; sample connectivity and
visual landscape relation are separate. Human visual assessment must address
recognizability, coherence, authored content and shortest next implementation
step. No metric is gameplay acceptance or geological validation.

Portable deliverables: standalone HTML viewer, exact input/results, executable
source/protocol and deterministic ZIP/hash manifest. Offline tests in CI;
strict retained/new re-export after final merged Windows checkout.
All PR54–57 validation/performance/adoption/save-safety gates apply unchanged;
PR57 reduction stays failed. #9/#11 open; geology-1/production/guards/shared
inputs/optional Ulti-World/temp untouched. Historical arrays/indices/ULPs
unknown; PR54 ran4a2fa1c, final capture mixin compile-verified only.
