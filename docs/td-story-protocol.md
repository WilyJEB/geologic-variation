# story-1: one frozen offline comparison

Base: merged PR58 8aa21cc. Commit and push this contract before implementation
or evaluation. Diagnostic only; no TD execution, queries, new seeds, parameter
search, alternate field or replacement construction, even if this fails.

Use only PR57 visual-data.json SHA256
8dc1e0a9f98edd1dc6b2ce74cc1d795c117c15feb9503b0260a5c5ef23a701d6.
Compare exactly against PR58 terrain_illustration_ids and its exact contacts,
not its seed-only panel. Preserve all PR58 archive/HTML/image bytes separately.
Retained elevation only: 49x49 sites, spacing64, x2688..5760,z10880..13952.
Original query half-open [z10880,x2688,z13953,x5761]. Missing 9440928 values;
between-point/exterior geometry and observation error unknown, never zero.
Pinned provider bytecode/source must be inspected: optional climate/coarse
conditioning is not geological evidence. No p5 relief or confirmed extrema.

Separate four records: stable seed identity; descriptive elevation summaries;
authored synthetic events; universal abstention from actual geological history.

Stable anchors are (phase+2048*(i+1/2),0), signed integer i, with phase from
first eight hex digits SHA256 UTF8 `story-1|8675309|phase` modulo2048.
Tokens SHA256 `story-1|8675309|history|i`, canonical decimal signed integers.
These anchors/IDs exist before observations. Fixed neighborhood i-1,i,i+1.
This is a deliberately simple band hypothesis, not acceptance of a square grid
or a final regional layout. ID ownership may change with terrain interpretation;
anchor identity does not. Mathematical floor, lower-boundary ownership;
exact equalities use the higher i. No discovery-dependent assignment.

Compute least-squares planar descriptive slopes gx,gz using all2401 elevations
and centered x,z coordinates; regular grid cross covariance is zero. Let
a=clamp(gz/gx,-0.5,0.5) if gx!=0, otherwise a=0 and abstain on orientation.
No threshold is calibrated. Bands are i=floor((x+a*z-phase)/2048).
Contacts x=phase+2048*i-a*z. Whole bands and rectangle intersections are convex;
sample connectivity must still be counted. No decorative noise or separate
horizontal seam. All contacts follow this single tilted-band construction.
The 2401 fixed observations are the finite maximum terrain neighborhood;
there is no observation extrapolation, query, tiling policy or global terrain
claim. The formula outside the field is conceptual only.

One synthetic history: inherited layered substrate, authored tilting in the
direction of the observed broad planar elevation trend, then differential
stripping. gx,gz influence the tilt relationship (not a measured geological dip).
For each visible band, compute mean observed elevation minus whole-field mean.
Positive contrast authors greater stripping/exposed inherited substrate;
negative authors cover preservation; exact zero or absent support leaves the
event unresolved. Seed token first-byte parity chooses the invented substrate
tag A/B only. Substrate and stripping vocabulary are authored alternatives,
not inferred rock, age, erosion rate or tectonics. A surface record names
exposure/cover; its deep record names the same inherited band and token.
No invented depth, elevation interpolation or actual subsurface interface.
Terrain therefore changes event relationships as well as contact orientation.
Regional boundaries are conceptual inherited band contacts even where neighboring
event tags coincide; report that limitation rather than invent extra evidence.

Freeze one evaluation: exact baseline/new arrays, per-ID four-neighbor components,
counts/transitions, slopes/clamp activation, band means/events and shared tokens.
Check byte repeatability, reverse/shuffled traversal, fixed finite support,
signed coordinates/ties, adjacent contact ownership and shared surface/deep
identity. No score is geological validation or gameplay acceptance. Assess maps
visually separately from computed connectivity and authored plausibility.
Viewer embeds SVG sites, original footprint, unresolved gaps, baseline/new
contacts and key results without JavaScript; optional controls may hide overlays.
Portable ZIP contains input, baseline result, output, source, protocol and API
evidence with hashes. Verify actual HTML if available; static rendering is not
browser verification. Preserve the existing untracked viewer repair separately.

Carry forward every gate in PR54-58 reports: failed pressure reduction, paired
coarse drift, matching native support, height/residual and final-block failures;
geometry/uncertainty, numerical reproducer, fresh validation and alternating
paired full-route performance remain open. PR54 four launches exhausted, executed
4a2fa1c; final capture mixin compile-verified only. Historical arrays/indices/ULPs
unavailable. Adoption requires immutable versioned identity, explicit new-world
choice, bidirectional save rejection, exact artifact restore/reopen and full
block/container preservation. Geology-1, production, strict guards, immutable
inputs, optional Ulti-World and unrelated temp untouched. No palettes/dikes/
minerals/integrations. #9/#11 stay open. Passing CI before merge; strict retained
and new evidence re-export after final Windows checkout. Negative result retained.
