# Constant-support geometry calibration and exact-support numerics (#11)

**Diagnostic only. Calibration fails feature discrimination; historical numerical
causation remains unresolved. No fresh held-out execution. Geology-1 is unchanged.**

[Protocol](td-geometry-numerics-protocol.md), [analytical/development replay](evidence/td-geometry-arc.json),
[sensitivity cases](evidence/td-geometry-sensitivity.json), [numerical comparisons](evidence/td-numerics.json),
[portable exact bits, transcripts and executed sources](evidence/td-numerics.zip).

## Reconciliation and frozen evidence

Current main/origin and GitHub reconciled at merged PR52 `6c5f105`.
GitHub confirms merged #47 d6d59ca, #48 db8bcea, #49 05bd8b9, #50 ce91c6a,
#51 e3fdbcf and #52 6c5f105. No applicable AGENTS.md exists in this checkout
or its project ancestors. Protocol/resource rules were committed/pushed at
fff65b4; exact collector/probe sources at56cfca7 before execution. All previously
examined seeds, explicitly including2026110407 and -2026110411, are development.

PR51 and PR52 selectors/exporters are untouched. Strict retained #47–#51 exports
reproduce committed JSON. PR51 still rejects `Paired coarse drift`; PR52 still
rejects `Actual matching native support changed`. Their separate negative exports
preserve those rejections and failed coverage. No tolerance is added. #5's stronger
failed final-block assertion remains failed. #9/#11 stay open.

## Offline geometry calibration

Separately named geometry-arc-1 uses256-native-pixel shoulders and actual256-pixel
center-to-center steps at every orientation. Sixteen directed axes; initial
radius128 lattice localization; later three transverse alternatives; bounded
turning/displacement; one greedy path, no backtracking/branch extension or gap
bridging. All alternatives and reasons are exported. Actual cumulative path
distance drives endpoint-linear residuals. Original index-linear criteria remain
unchanged in their own exporters. The protocol records an offline implementation
correction: lateral displacement originally lengthened a step to263.88; tangent
retreat now holds actual length256. That correction reran only analytical and
retained development fields, never TD or held-out data.

Interpolation is bilinear on retained64px grids, a convex combination of observed
values. It never establishes an observed unsampled crest, never overshoots the
four input values, and is not a replacement fine field. Analytical exact-function
errors are measured at retained successful candidate centers/shoulders, not a
uniform error bound over all rejected queries. Maximum errors are3.991m straight,
5.350m curved,4.081m along-axis trend,2.421m saddle,7.982m isolated extremum and
258.251m across the deliberately discontinuous gap. Unknown TD derivative/error
bounds remain unknown; no analytic bound is transferred to TD.

180 controls: five rotations0/22.5/45/67.5/90 degrees, translations0/37px,
ridge/basin signs, nine shapes. Each shape has20 cases.

| Analytical shape | Diagnostic support /20 | Interpretation |
| --- | ---: | --- |
| Straight ridge/basin |20| Constant orientation bandwidth succeeds |
| Curved ridge/basin |20| Bounded curve recovery |
| Along-axis height trend |20| Extrema persist despite failed height-range rule |
| Slope |0| Rejected |
| Crossings |0| Rejected/incomplete |
| Parallel alternatives |0| Edge/ambiguity abstention |
| Genuine contrast gaps |0| Incomplete, no bridging |
| Isolated peaks/depressions |20| **False positive: discrimination fails** |
| Saddles |20| **False positive: discrimination fails** |

The previous perfect cardinal-ridge false negative is replayed unchanged and
retained in full. Improving that alias does not repair the newly exposed false
positives. No revised-selector coverage claim follows.

Six reused native candidate fields (paired scales are not recounted) yield
3/3/3/4/5/5 stations in seed/kind order8675309 ridge/basin,2026110407 ridge/basin,
-2026110411 ridge/basin. The last two have complete interpolated contrast paths;
all six remain unconfirmed and coverage-failed. Four incomplete searches do not
prove physical interruption. Two checkerboard perturbations +/-0.1m retain the
same selected points/station counts and diagnostic decisions in all six fields.
This is limited sensitivity evidence, not an error bound or a tolerance. It
cannot restore exact hashes or prove geometric robustness to arbitrary errors.

The retained -2026110411 original basin already had five observed two-sided
extrema while failing original height-range/residual conditions. Such a rejection
cannot be described as missing extrema. Analytical linear height trends confirm
this distinction. Arc detrending describes elevation along the path; saddles also
pass that geometric description, so removing a height condition alone would be
insufficient. No original failure is retroactively passed.

## Exact matching native support experiment

Three NEW metadata fixtures, scale1, CPU Java21; seeds are development.
First two use -2026110411, row-14 cols-6/+6, alternating cell order. Each requests
256x256 twice, halo1 cropped back to the same256x256 support, two128-row batches,
then a diagnostic-cache clear and reversed256x256 reads. Third uses2026110407,
cell row12 col65, recorded corner(16640,3072):256x256, cropped halo1,1x1 and repeat.
No large3073 patch was repeated. Exact big-endian float bits, matching support,
request rectangles, differing row-major indices, absolute/ULP differences,
means/relief and signed-short floor/clamp differences are retained.

| Row-14 cell | Intervention versus first256-square | Differing floats /65536 | Max absolute m | Max ULP | Quantized differences |
| --- | --- | ---: | ---: | ---: | ---: |
| col-6 | halo1 cropped |3972|0.07080078125|461|61|
| col+6 | halo1 cropped |4004|0.09228515625|378|85|
| col-6 | two row batches |2046|0.08935546875|366|49|
| col+6 | two row batches |2021|0.075439453125|309|41|

The same modes reproduce exactly across both processes. Every repeated unpadded
request matches exactly, before/after diagnostic-cache clear and opposite traversal.
Shape/halo and batching are separate interventions. The clear-plus-reversal step
combines two factors; it is not an isolated cache-versus-order causal result.
Fresh process also reverses initial order, so its agreement is a combined control,
not a factorial estimate of independent order and process effects. Diagnostic
native-cell caches are bypassed by direct queries. Provider tensor caches remain
warm within a process; no provider-cache clear is claimed. The upstream same-seed
setSeed route returns early and is not assumed to clear them. Cold here means a
new process, not a measured tensor-cache occupancy assertion.

Halo mean differences are+0.000377748m/-0.000238243m; relief differences are
-0.009277344m/+0.064941406m. Batched means differ-0.000491466m/+0.000155345m;
cell relief is unchanged. Tiny means conceal substantial individual differences
and quantized-height changes. Exact equality remains failed for shape changes.

Both new unpadded hashes exactly match PR52's **scale6** cell hashes:
col-6 `8d4959a72c842dd9d026288dd1d429df05edf97f285cf7570fbe1c48a5c702ad`,
col+6 `8bdc29080eeb5dcc3beab568097797e1e61e97f669cad34ef0d9d03828b2a738`.
They do not reproduce PR52's scale1 hashes. The historical scale-paired mean
differences remain7.748603820800781e-7/7.003545761108398e-7m. Those old full float
arrays were not retained, so historical differing indices/ULPs cannot be recovered
from hashes. New arrays are retained for every request. Neither rounding, caching
nor an upstream bug has been established as the historical cause.

Minimal supported reproducer, on the pinned CPU fixture/seed, is:
`acceptance numeric -6 -14 0` followed by `acceptance numeric -6 -14 1`.
Compare the cropped binary arrays: same native support, different request halo.
This reproduces **request-context sensitivity**, not the old identical-request
cross-scale failure. The full collector supplies setup and preserves exact inputs.

Corner investigation separately:256-square and1x1 give-1604.928466796875m at the
recorded corner, quantized-1605, matching the retained tile. The retained large
patch corner was-1605.0055m, quantized-1606. The new halo changes3958 cell samples
(max0.0770263671875m;44 quantized differences) but does not recreate the original
large-patch context. The original corner discrepancy remains unresolved and
visible; it is not attributed to flooring alone.

## Resources, provenance and verification

Actual runtime matrix: runs/acceptance/td-numerics-2026-11-04-02. Three JVM launches,
24 numeric commands /28 direct pipeline requests, no diagnostic result cache or
hidden command-row multiplication. Unique256-cell supports: three seed/cells;
point support overlaps the corner cell. Modes and repeated executions are paired
observations. Startup new windows4/4/4; final totals126/126/67; post-startup122/122/63
=307, total319. Coarse startup calls1 each; no heightmap calls. No broad survey.
Sampled Java working set peaked5,296,193,536 bytes (not instantaneous peak).
6GiB heap,16GiB sampled working-set cap,4GiB disk reserve,1500 windows/JVM,
32 requests and40min total limits held; elapsed158.125s including fixture work.
Checkpoint guards can overshoot inside one request; no overshoot occurred here.
The first setup directory -01 hit sandbox hardlink denial before any launch;
its partial results are preserved, excluded from launch/request totals.

Shared model/template manifests remain identical; CPU JAR SHA256
3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8.
Exact addon/probe hashes, model files, backend/context and config hashes are in
portable JSON/archive. Snapshot bytes remain unchanged in each new fixture.
Executed sources from56cfca7 are embedded and checked against that exact Git
object; revised offline geometry is separately source-hashed in its own evidence.
The deterministic archive retains every binary and console transcript.

New: offline controls, six reused-field recalibrations and sensitivity cases,
three bounded CPU fixtures, exact bits and provenance. Reused: all #47–#52 fields,
strict failures, save/reopen/block and529 persisted-container acceptance; those
save/reopen gates were not newly executed. Production source/resources and
geology-1 are unchanged. Optional Ulti-World and unrelated temp/ remain intact.
No palettes, dikes, minerals or integrations. Morphology does not establish
geological plausibility: competing seeded synthetic interpretations retain
uncertainty and geological selection abstention.

## Remaining gate

Finish diagnostic-only. Before fresh held-out inspection, separate elongated
features from isolated extrema/saddles using preregistered analytical positives
and negatives; establish observed TD extrema or a defensible interpolation-error
policy; independently isolate provider-state/traversal versus fresh-process
behavior on the historical matching-support discrepancy with retained full bits.
A small shape reproducer is not a historical-cause reproducer. Freeze any revised
selector/evaluation/resource rules before at least two NEW seeds, scales1/6,
negative coordinates, contrasting terrain and multiple coarse/province boundaries.
Keep fixed coverage, selected features and paired native observations separate.
Fine points, native-cell means, coarse neighborhood range, scaled tiles and fine
relief remain different evidence. Differing anchor support is distinct from unequal
hashes on matching support. No p5 or geology-1 cutoff transfer.

Future output-changing adoption still requires immutable generator identity,
explicit new-world-only selection, genuine bidirectional continuing-save rejection,
exact original-artifact restoration/reopen and complete snapshot/block/persisted-
container preservation. Never migrate continuing geology-1 snapshots. Integrated
candidates additionally require alternating paired CPU startup/cold/warm/full-route
benchmarks on NEW fixtures. Never extrapolate isolated-query savings to route savings.

Reproduction: run scripts/calibrate-td-geometry.py and
scripts/audit-td-geometry-sensitivity.py; export-td-numerics.py strictly checks the
raw directory and builds the portable archive; test-td-geometry-numerics.py replays
both and tests bit corruption. Use the collector only with a NEW budget and output
directory; the completed three-launch budget is exhausted. Final Windows checkout
must re-export #47–#52 and this slice with strict source/artifact/log checks.

Local verification: Java21 build/domain/settings/coarse/probe tasks pass; resources
and catalog checks pass. The26 landform/tracking/control/negative/calibration tests
have25 passes and one intentional frozen positive-path skip. Portable tests check
raw transcript membership, exact request bounds, source/archive hashes, float bits
and deliberate corruption. Process/listener inspection after shutdown finds no
remaining Java/Python diagnostic processes or game/RCON/explorer listeners.
Collector follow-up only automates copying executed-source bytes and recording
the Git ref; the completed experiment used the original56cfca7 collector, with
its exact source copies checked against Git before portable export. No extra TD
execution was performed for this packaging improvement.
