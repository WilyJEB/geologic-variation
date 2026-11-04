# geometry-arc-1 / numerical-support-1 bounded protocol

Base: merged PR52 6c5f105. All examined seeds are development, including
2026110407 and -2026110411. No new held-out seed is authorized by this protocol.
No production changes. Frozen PR51/52 exporters and criteria stay unchanged.

Offline geometry first: geometry-arc-1 uses bilinear interpolation of retained
64px point grids, never labels interpolated points as observed extrema. Compare
interpolation against exact analytical functions at queried positions; retain
maximum errors. Bilinear interpolation is a convex combination of four samples;
it cannot exceed their extrema but can displace an apparent crest. No overshoot
interpolation. Shoulders and predicted steps always 256 native pixels, 16 equally
spaced directed axes. Five stations, two per branch. Initial center offsets in
64px lattice disk radius128; later offsets only transverse -64,0,+64 relative to
prediction. Max per-step turn22.5 degrees, combined90; displacement from original
straight station <=256. Greedy best weakest-side search only; no backtracking,
branch extension or gap bridging. Retain alternatives and incomplete paths.
Alternatives within10m and >128px transverse or >45deg apart abstain. Edge winners
abstain. Both sides >=50m is a diagnostic contrast threshold, not geology-1.
Interpolation uncertainty: maximum analytical error is descriptive, not a bound
on unknown TD derivatives. Retained TD geometry always abstains from confirmed
extrema/coverage pending finer observed support. Report original criteria and
arc-distance endpoint residual separately; changing elevation is not missing
extrema. Test rotation/translation, curves, height trends, slopes, isolated
peaks/depressions, saddles, crossings, parallel alternatives and gaps. Preserve
old cardinal false negative. No tuning on revised terrain results.

Numerical experiment, after pushing this protocol: maximum THREE serial JVM
launches total (including failed launches), CPU, 6GiB Java heap, maximum16GiB
process working set sampled before/after commands (not instantaneous peak), disk
reserve4GiB before each launch/command, 40min total, startup360s, command300s.
Maximum32 direct pipeline requests total, maximum1500 newly computed windows
per JVM including startup at command checkpoints; one call can overshoot, then
stop. No large3073 patch repeats. Exact native row -14, cols -6/+6, seed
-2026110411. Compare unpadded256 square, halo1 cropped to same support, two
128-row batches concatenated, repeated identical request, reversed cell order,
diagnostic-cache clear. Provider tensor cache has no assumed clear API; fresh
process is the cold-state intervention. Two fresh scale1 fixtures, alternating
order. Third fixture seed2026110407 checks recorded corner [16640,3072] using
256 tile versus halo1 and exact point; this cannot reproduce the original large
patch context and remains an explicitly limited corner investigation.
Retain all float bits binary big-endian, input/model/config/source/artifact
hashes, exact coordinates/request boundaries, logs, counters, indices, absolute
and ULP differences, means/relief/floor-clamped signed-short quantized heights.
No tolerance replaces strict equality. No cause assigned without controlled
support. Stop on limits and retain partial results; no replacement launch.

Fresh held-out validation is deferred to a separately committed/pushed selector,
evaluation and resource protocol only after calibration and numerical gates.
At least two genuinely fresh seeds, scales1/6, signed terrain contrasts and
multiple coarse/province contacts, fixed coverage separate from selected features,
paired native observations would be required. No p5 or transferred geology cutoffs.
Morphology never establishes geological plausibility. #9/#11 remain open; #5
stronger failure, strict guards, optional Ulti-World, immutable shared inputs and
unrelated temp/ stay intact. No palettes/dikes/minerals/integrations.
Future adoption requires immutable identity, explicit new-world-only selection,
bidirectional continuing-save rejection, exact restoration/reopen and complete
snapshot/block/persisted-container preservation. Never migrate geology-1.
Integrated candidates require alternating paired CPU startup/cold/warm/full-route
benchmarks on NEW fixtures; isolated-query savings are not route savings.

Offline implementation correction after numerical collection (no new TD run):
lateral +/-64px center alternatives now retreat along the tangent by
256-sqrt(256^2-64^2), so actual center-to-center distance is exactly256, including
the backwards branch. The earlier implementation kept predicted distance256 but
actual lateral steps were263.88. Revised calibration remains development data;
its saddle/isolated-extremum failures remain visible. Numerical collection used
56cfca7 source bytes, retained verbatim inside the portable archive. The numerical
probe/collector were not changed; this geometry correction did not execute TD.
