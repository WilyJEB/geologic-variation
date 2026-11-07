# Finite terrain-informed regions and pinned execution history (#11)

Diagnostic only. No TD launches, new seeds, production selector or geology-1
changes. Geometry and numerical adoption remain insufficient. #9/#11 stay open.

[Offline protocol](td-window-history-protocol.md), [portable evidence](evidence/td-window-history.zip)
and [hash manifest/results](evidence/td-window-history.json). Run
`scripts/test-td-window-history.py` anywhere with Python and this checkout;
it uses the archive, not upstream sources, models, a server or machine-local runs.

## Intended player-visible property

The goal is **terrain-informed regional coherence**: neighboring geological
regions share a seeded synthetic history, while broad terrain observations bias
that history and the shape of contacts coherently. A finite valley-like corridor
can support an elongated sedimentary-domain hypothesis; uplift can expose inherited
sedimentary rocks on mountains. Neither is a claim to recover real history.
The intended gain is recognizable connected regions and terrain-related contacts
when exploring, with shared surface/deep regional identity rather than independent
per-block choices. This slice demonstrates no gameplay improvement yet.

This is faithful to the original addon concept: terrain interpretation remains
central, but the claim is explicitly local to a declared observation footprint.
It does not demand unrestricted global ridge/basin identity or reconstruct plate
tectonics. Terrain alone does not uniquely determine rock history. A long closed
extremum or shallow saddle may exhibit transverse confinement on the observed
path; that observation cannot certify its exterior identity. PR54's original
false positives and false negatives retain their original labels and remain failed.

A future observation contract must name a canonical native-coordinate regional
grid, exact queried points/rectangles, search halo, transverse distance, path
extent, orientation alternatives and boundary rules. For example PR54's existing
L=1024, d=256 specification describes only that finite sampled footprint, not a
whole mountain chain. A future regional neighborhood must also have a fixed
finite radius; no continent flood fill or exploration-dependent expansion.
Observation support is distinct from TD's larger inference dependency footprint
(padding/overlapping windows); neither implies information about arbitrary terrain
outside the observations. No new support, thresholds or selection rule is adopted here.

Abstain on unavailable/invalid coarse weights, unknown interpolation error for
unsampled extrema, insufficient two-sided observations, competing axes or branches,
boundary-censored continuation, gaps, localization/search limits, intervals crossing
a decision boundary, or inconsistent matching-support values. Search failure is
not a physical termination. A saddle or summit outside support is unknown.
All six reused TD fields still abstain from confirmed geometry. Unknown error
is not zero; checkerboard sensitivity is not a defensible error bound.

A deterministic fallback would need globally anchored seed/domain-separated IDs,
bounded neighbor access, stable tie-breaking and shared surface/deep histories;
continuous contacts must agree across region/chunk boundaries and negative axes.
Its results must not depend on discovery order, cache eviction, retry timing,
thread scheduling or machine-specific availability. An observation failure cannot
switch a continuing save's identity. A fallback should retain coherent seeded
regions while recording unavailable terrain evidence; it cannot silently choose
different geology on different visits. Fix its scope, version and immutable
generator/model context before testing it. A numerical tolerance or fallback does
not repair the historical exact-hash assertion. Production selection is not implemented.

## Reconciliation and evidence authority

Fetched origin/main and local main both started at `8a5ad4d`, the guidance commit
after merged PR55 `a820d63`. GitHub independently confirms #55 merged and #9/#11
open. AGENTS.md applies. Untracked `temp/` is preserved. PR52/53/54/55 portable
results, transcripts, source hashes and bytecode are reused. New work is only
coordinate/cache modeling, additional pinned layout/byte-size bytecode inspection,
offline replay, one reduction check and tests. No analytical outcomes or TD arrays
were newly collected. Every previously inspected seed/control is development data.

The pinned CPU JAR SHA256 remains
`3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`.
Retained `javap -p -c` is the authority, including newly retained TensorWindow,
FloatTensor and model-config bytecode. Explanatory upstream sources are retained
from `8acd2b680ee248334637f8cf13f6c78ac20003da` with hashes. Source comments can be
misleading: InfiniteTensor's comment says eviction follows writes, but executed
bytecode evicts at the end of getSlice, after assembly. The model follows bytecode.
Model config records latent_compression=8, coarse_pooling=1, native_resolution=30.

Pinned public inputs include the seven-channel weighted coarse tensor (six signals
plus blend weight), elevation and optional climate. Explorer's coarse channels
are elevation, p5 and four climate signals; these are not rock/tectonic layers.
The existing coarse adapter checks weights/metadata and decodes elevation. This
slice does not adopt p5 as relief, infer unavailable layers or transfer geology-1
cutoffs. Fine points, native means, coarse range, scaled tiles and relief remain
different observations.

## Auditable state model

The Python model carries coordinates, cache order, batch membership and counts;
it has no floats, neural inference or generic scheduling framework. Channel
indices are suppressed because each slice covers the complete channel dimension,
whose only intersecting window index is zero. Bounds are half-open, row=z/col=x.
For spatial window size S and stride T, intersections run from
ceil((start-S+1)/T) through floor((end-1)/T), row-major, column fastest.

| Tensor | Output channels / size / stride | Dependency window for index (i,j) |
| --- | --- | --- |
| coarse | 7 / 64 / 48 | none |
| init latent | 6 / 64 / 32 | coarse 4x4, stride1, offset-1 |
| step latent | 6 / 64 / 32 | init 64x64 stride32; coarse 4x4 stride1 offset-1 |
| residual | 2 / 256 / 192 | step 32x32 stride24 |

Missing windows are deduplicated in insertion order with containsKey (no LRU
promotion). Ensure all dependencies for that list first, in declared dependency
order. Init/step then group the list in fours; dependency slices are read in
dependency-major, then member order. Residual/coarse compute singly. Every
getSlice ensures, assembles row-major (promoting get hits), then evicts only its
own tensor. Cache writes retain an existing key and promote it instead of
overwriting. Byte size is channels*S*S*4. Each tensor's limit is104857600 bytes;
keep one entry even if oversized. Capacities are914 coarse,1066 each latent,
200 residual, but ensure can temporarily exceed them until a slice returns.

computeElev aligns native bounds outward to the8-pixel grid after48-pixel
padding, reads residual first, then step latent at padded bounds/8. Climate adds
an8-coarse-pixel halo to floor/ceil(native bounds/256). These extra reads affect
access order even if they compute no new windows.

Scale1 diagnostic tile reads call getPipelineData directly, climate=false. They
do not use the heightmap cache. Scale6 calls fetchHeightmap: floor world starts/6,
ceil ends/6, add two native pixels on every side, pipeline.get with climate=true.
The provider cache is separate from tensor stores: serial hits promote its
logical access clock; after insertion, size>68 removes eight oldest. Public clear
affects CACHE/PENDING only. No pending concurrency is modeled: the retained
collector serializes calls and waits for each to complete. Unknown unlogged
concurrent work would invalidate the candidate history rather than be invented.

Measured startup is four windows and one coarse call. The retained prepare source
calls getPipelineCoarse(0,0,1,1), predicting coarse indices (-1,-1),(-1,0),(0,-1),
(0,0). The model starts with that source-derived candidate. Historical internal
startup order/cache membership was not logged; matching counts do not prove it
unique. No search over startup states was performed.

## Comparison with retained history

All100 PR52 command deltas and104 absolute checkpoints match (102 comparisons
per scale). All69 retained PR53/54 metric checkpoints also match, including both
PR53 cell orders, its separate corner history, PR54 AB/BA and repeated reads.
These are newly performed offline checks against reused runtime counters.
No model mismatch was encountered; the code stops and visibly fails its counter
gate at the first mismatch in any history. A corruption test exercises that stop.

| PR52 first native miss | scale1 predicted before -> after | scale6 predicted before -> after |
| --- | --- | --- |
| row-14 col-6 | ordinal326:3625 ->3648 | ordinal322:3588 ->3609 |
| row-14 col+6 | ordinal366:3712 ->3735 | ordinal362:3673 ->3694 |

The3625/3588 values are also measured command-start counters. Before the col+6
command, measured totals are3706/3667 as PR55 states; intervening coarse requests
inside that command add six windows before the target read. Thus3712/3673 are
model-derived immediately-before-target counts, not a correction to measured data.
Full command ends are3735/3694 and match retained metrics. The archive preserves
every modeled batch/eviction, target pre-read cache order and count comparison.

Source-derived predictions at A (col-6): step computes the same four keys
(-16,-8)..(-13,-8) in both scales. Init computes10 missing keys in scale1
(batches4/4/2), versus8 in scale6 (4/4). Scale1 additionally recomputes
(-16,-8),(-16,-7). At B, step similarly computes (-16,7)..(-13,7);
init10 versus8, with scale1 additionally recomputing (-16,6),(-16,7).
Residual computes nine windows per target in both scales. Complete key sequences,
including which common keys move between batches, are portable in result.json.

Both patch requests occur at ordinals85/90. The model predicts patch90 creates
the four distinguishing init keys. Scale1 evicts the two A keys at request238,
and the two B keys during request326 (A's read); scale6 retains all four through
both target reads. The model records121 versus116 getSlice eviction events in
the full retained prefixes. A's scale1 recomputation can itself alter later B
state: the cells are not independent fresh-process samples. PR53/54 early direct
reads lack this long pressure history; their initial two reads add61 windows
each after startup, then their repeats add none, matching the retained counters.

These are predictions of an auditable candidate state, not historically observed
internal events. Aggregate agreement is stronger than merely asserting a cache
effect, but does not uniquely recover state, batch arithmetic or array bits.
It does not prove a provider bug, nondeterministic ONNX behavior, rounding cause
or historical hash reproduction. PR53's halo/batching sensitivity remains a
separate demonstrated effect. PR54's26 arrays still match its direct baseline
and PR52 scale6; neither historical scale1 hash has been reproduced. Historical
full arrays do not exist: differing indices/ULPs stay null/unknown.

## Runtime decision and short route to a prototype

**No minimal distinguishing runtime experiment is justified by this slice.**
The model supports execution history as a concrete mechanism worth testing,
but a two-request candidate fails the required reduction check: patch90 followed
by A predicts init6 (4/2), not full-history10 or8. It computes835 total windows.
Its failed `preserves_either_full_prefix_target_grouping=false` is retained.
No pressure-prefix search or retuning followed. A full replay would require
hundreds of calls and both large patches, rather than isolate the distinguishing
eviction/retention. Identical target batch sizes alone would also be inadequate:
cached ancestor windows may have been created in different groups earlier.

What is missing is one small, explicitly bounded retained pressure sequence
whose offline trace preserves the distinguishing keys' creation ancestry,
eviction/retention and target batch membership against a paired reference under
the same startup. That must include all dependency reads that can change this
state, not just target coordinates or aggregate totals. This report supplies
the exact candidate traces to assess it without another TD run. Do not substitute
AB/BA, process, scale, halo/batching or empty-provider-clear controls already
exhausted. No runtime collector or launch budget is prepared/authorized here.
Before any later justified execution, commit and push the exact protocol and
executable collector with failures consuming launches; cap requests, startup/total
windows, memory, disk and wall time; retain complete arrays/sequences/counters,
executed source/artifact/input bytes and partial failures. PR54's four launches
remain exhausted. Runtime provenance is4a2fa1c; its final capture mixin is still
compile-verified only.

Keep the next work decision-oriented: assess one bounded pressure reduction from
these traces, and stop if it cannot preserve the distinction. If a distinguishing
reproducer resolves numerics, freeze a finite observation/uncertainty contract
and analytical evaluation for terrain-informed coherence. Fresh validation is a
later separately authorized slice, with genuinely new seeds, scales1/6, negative
coordinates, contrasting terrain and multiple coarse/province contacts; fixed
coverage and selected features stay separate and shared cells/scales paired.

The first visual prototype should be a diagnostic regional map/overlay on retained
terrain: show observed terrain evidence, competing seeded histories, contacts and
abstained areas side by side. That can expose whether connected regions visibly
respond to landscape without changing saves or pretending morphology establishes
geology. Reused fields are development illustrations, not validation. Bound that
prototype to one finite map and a player-facing question: are its regions and
contacts recognizable, coherent and meaningfully related to this landscape?
This diagnostic visualization can proceed on retained fields while adoption
remains gated; it does not need a new TD survey or a production selector.
Do not expand into palettes, dikes, minerals or integrations in this slice.

Production adoption still requires both geometry/numerical gates, separately
pushed selector/evaluation/resource rules, immutable generator identity, explicit
new-world-only choice, genuine bidirectional continuing-save rejection, exact
original-artifact restoration/reopen and complete snapshot/block/persisted-container
preservation. Never migrate geology-1. Integrated candidates need alternating
paired CPU startup/cold/warm/full-route benchmarks on NEW fixtures; isolated
query savings do not imply route savings. Retained save/529-container evidence
is reused, not newly executed. Strict guards, immutable inputs, optional Ulti-World
and every existing validation/performance/save-safety gate remain intact.

## Verification

The portable tests check signed half-open intersections against brute-force
overlaps, post-assembly eviction, scale6 padding/provider hits, exact archive
replay and corrupted-counter stop behavior. Passing tests mean the evidence is
reproducible; they do not turn a failed reduction or historical hash into a pass.
PR51 `Paired coarse drift`, PR52 `Actual matching native support changed`, frozen
height/residual criteria and #5's stronger final-block assertion remain failed.
Full verification, CI, merge and final Windows checkout re-export are recorded
on the PR; no TD model is executed for any of those checks.

Pre-PR verification passed Java21 build/domain/settings/coarse/probe, resource
and catalog checks, and44 Python tests (43 passed, one unchanged frozen positive-
path skip). Strict original-source/artifact #47–#53 exports, PR54 analytical and
exact-array exports, PR55 history and the new evidence all reproduced unchanged
in `runs/acceptance/td-window-strict-premerge-01`. The first restricted build
attempt could not access the existing Gradle lock; the normal-cache retry passed.
That was a build retry, not a TD launch. The final-checkout audit uses
`scripts/reexport-td-window-history.py` and must reproduce all of these again.
