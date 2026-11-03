# TD elongated ridge/basin coverage diagnostic (#11)

**Decision: retain actual-target point diagnostics only. TD elongated-feature coverage remains insufficient; geological classification abstains.**

## Results and preserved failures

[Portable evidence](evidence/td-landforms-2026-11-03.json) retains all numeric screening, candidate, profile, boundary and reverse observations; exact source/artifact/log hashes; and request accounting. No analytical control is counted as a TD feature.

All six NEW CPU fixtures pass collection, within-fixture traversal and snapshot checks. The cross-scale anchor assertion fails separately below. There are 486 screen rows but 243 distinct seed/native screen cells; 310 forward comparisons at per-fixture unique world locations and the same number reversed; 148 distinct seed/native target cells. These support counts are not independent statistical observations. Repeated scales, shared cells, adjacent profiles and overlapping group memberships remain paired/correlated.

| Seed / role | Screen ocean / coast / land | Unique fine locations scale 1 / 6 |
| --- | ---: | ---: |
| 8675309 / development | 32 / 28 / 21 | 52 / 52 |
| 2026110317 / held_out | 34 / 23 / 24 | 51 / 51 |
| -2026110319 / held_out | 38 / 22 / 21 | 52 / 52 |

Ocean/coast/lower/intermediate/upper land are selection strata, not validated geological or fine-surface labels. No required stratum is silently replaced by an expanded search. The first held-out seed shares its coast selection at (16384,16384) with fixed coverage; both memberships remain, and it is collected once. Scale 6 uses the corresponding scaled location.

### Coarse selector success and failure

Each attempted center passes the two-sided 50 m central extremum test. The table preserves every native candidate attempt, including rejected second choices. Negative weakest support means that at least one station is no longer a cross-axis extremum. Values are metres. Sides are ordered minus/plus along perpendicular (-dz,dx) to the declared longitudinal [dx,dz] axis. Full two-sided measurements at all five stations are in the JSON.

| Seed | Kind | Center row,col / along axis | Central minus / plus | Weakest of ten sides | Longitudinal range / residual | Complete support |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 8675309 | ridge | 48,16 / [1, -1] | 969.36 / 1262.94 | -686.48 | 2015.78 / 388.44 | **fail** |
| 8675309 | ridge | 64,0 / [1, -1] | 1032.09 / 963.91 | -268.03 | 1887.12 / 1174.04 | **fail** |
| 8675309 | basin | -32,-32 / [0, 1] | 535.54 / 631.69 | -187.08 | 2804.93 / 627.63 | **fail** |
| 8675309 | basin | -16,-48 / [1, 0] | 431.75 / 904.81 | -338.44 | 3874.11 / 1144.41 | **fail** |
| 2026110317 | ridge | -64,-48 / [1, -1] | 959.28 / 651.43 | -461.89 | 1426.73 / 1422.06 | **fail** |
| 2026110317 | ridge | -48,64 / [0, 1] | 625.52 / 656.91 | -390.68 | 754.67 / 635.69 | **fail** |
| 2026110317 | basin | 48,16 / [1, 1] | 558.91 / 789.11 | -238.78 | 974.24 / 141.69 | **fail** |
| 2026110317 | basin | -32,0 / [1, 0] | 537.84 / 695.11 | -865.98 | 654.07 / 366.95 | **fail** |
| -2026110319 | ridge | -64,48 / [1, -1] | 1258.06 / 1813.20 | -407.82 | 3517.08 / 1418.38 | **fail** |
| -2026110319 | ridge | 64,16 / [0, 1] | 965.87 / 1901.63 | -154.78 | 2633.80 / 806.51 | **fail** |
| -2026110319 | basin | -48,-32 / [1, 1] | 1244.54 / 1463.82 | -24.23 | 2857.34 / 957.28 | **fail** |
| -2026110319 | basin | 32,32 / [1, -1] | 950.59 / 535.18 | -848.04 | 1903.89 / 1663.06 | **fail** |

A strong center does not satisfy finite longitudinal support. The search confirms only its predeclared candidates, so these failures do not demonstrate that TD lacks elongated features elsewhere or along curved/off-axis paths. No held-out retuning or analytical substitute repairs the gate.

### Actual fine profiles at candidate centers

Failed fallback profiles remain failed candidates. Matched-native means and scaled-tile means are evaluated separately with the frozen rules. The table shows the native center's two sides and the weakest signed side across five stations. Full native/tile longitudinal ranges and residuals also remain in the evidence.

| Seed | Kind | Native center minus / plus | Weakest native | Weakest tile scale 1 / 6 | Native / tile-1 / tile-6 complete support |
| --- | --- | ---: | ---: | ---: | --- |
| 8675309 | ridge | 1081.74 / 1161.61 | -904.33 | -857.28 / -769.60 | **fail** / **fail** / **fail** |
| 8675309 | basin | 419.36 / 636.76 | -285.02 | -275.96 / -293.56 | **fail** / **fail** / **fail** |
| 2026110317 | ridge | 913.72 / 650.32 | -533.05 | -480.00 / -326.80 | **fail** / **fail** / **fail** |
| 2026110317 | basin | 548.14 / 826.20 | -358.30 | -337.40 / -428.36 | **fail** / **fail** / **fail** |
| -2026110319 | ridge | 1071.41 / 1596.86 | -503.97 | -489.16 / -489.44 | **fail** / **fail** / **fail** |
| -2026110319 | basin | 1152.40 / 1521.65 | 51.65 | 33.88 / -94.48 | **fail** / **fail** / **fail** |

Frozen coverage gate: **FAIL**. It requires a ridge AND basin on BOTH fresh seeds, passing coarse, matched-native fine and scaled-tile support at both scales. A point extremum or a failed fallback never counts as successful elongated coverage.

### Terrain agreement, grouped by sampling purpose

Native scale-1 central coarse mean versus actual-target full fine-cell mean: mean absolute error (m), followed by central-sign agreements / rows. Scale 6 is excluded from native sample counts. These are descriptive rows, not independent accuracy trials. Fixed coverage and selected contrasts overlap at the shared point above; profile rows are strongly spatially correlated.

| Native cohort | Province anchor | Actual target | Fixed grid 4 |
| --- | ---: | ---: | ---: |
| development / coverage | 1126.48; 3/5 | 114.84; 5/5 | 1434.75; 4/5 |
| development / contrasts | 677.62; 4/5 | 52.18; 5/5 | 638.54; 5/5 |
| development / profiles | 1243.37; 20/30 | 100.98; 30/30 | 786.16; 25/30 |
| held_out / coverage | 1469.66; 6/10 | 121.04; 9/10 | 1127.65; 8/10 |
| held_out / contrasts | 1121.19; 7/10 | 50.21; 9/10 | 773.27; 8/10 |
| held_out / profiles | 1258.46; 51/60 | 87.12; 60/60 | 630.98; 55/60 |

The JSON separately retains each representative's own matched-support error, fine displacement from the target, pixel below-zero fraction and neighborhood-vs-cell tendency disagreement. A central coarse average and native fine average remain different model products; three-by-three neighborhood signs do not establish fine shoreline exposure or geological plausibility.

### Boundaries, traversal and bounded requests

Every coarse/grid edge pair and both independently located province contacts are retained per fixture. All province contacts actually change the Java-reported province. Maximum jumps below are changes in support statistics, not one-block physical cliffs. Counts include paired scales and must not be interpreted as independent boundary observations.

| Edge group | Paired edge rows | Max anchor / target / grid central-mean jump (m) | Max target tile-mean jump (m) |
| --- | ---: | ---: | ---: |
| grid_boundary | 24 | 0.00 / 604.87 / 3216.76 | 625.88 |
| province_boundary | 12 | 5433.76 / 0.00 / 0.00 | 0.00 |

| Seed / scale | Unique fine queries | Deduplicated coarse / native-cell requests | Direct data calls | Heightmap calls | New windows forward / reverse |
| --- | ---: | ---: | ---: | ---: | ---: |
| 8675309 / 1 | 52 | 89 / 89 | 193 | 0 | 2711 / 393 |
| 8675309 / 6 | 52 | 89 / 89 | 89 | 104 | 2699 / 380 |
| 2026110317 / 1 | 51 | 90 / 90 | 192 | 0 | 2836 / 418 |
| 2026110317 / 6 | 51 | 90 / 90 | 90 | 102 | 2836 / 418 |
| -2026110319 / 1 | 52 | 92 / 92 | 196 | 0 | 2926 / 435 |
| -2026110319 / 6 | 52 | 92 / 92 | 92 | 104 | 2927 / 441 |

The table covers forward comparisons and their reversed recomputation only. Public native-cell misses are deduplicated by the diagnostic LRU; two separate uncached tile reads occur per unique world query. At scale 6 the tile reads enter the heightmap API; internal provider work is not counted as a public direct-data call. Halo-cell counts, representative cells, actual getter requests and newly computed windows are different units, all retained separately.

Remaining phases are accounted separately below. C/D/H/W means public coarse calls / direct-data calls / heightmap calls / newly computed windows. Startup is a counter snapshot, not a timing benchmark. Fine forward/reverse request misses are independently replayed against the two cleared LRUs.

| Seed / scale | Startup C/D/H/W | Screen + confirmation C/W | Suite + oracle C/W | All post-startup C/D/H/W |
| --- | ---: | ---: | ---: | ---: |
| 8675309 / 1 | 1/0/0/4 | 97/12 | 154/0 | 429/386/0/3116 |
| 8675309 / 6 | 1/0/0/4 | 97/12 | 154/0 | 429/178/208/3091 |
| 2026110317 / 1 | 1/0/0/4 | 97/12 | 154/0 | 431/384/0/3266 |
| 2026110317 / 6 | 1/0/0/4 | 97/12 | 154/0 | 431/180/204/3266 |
| -2026110319 / 1 | 1/0/0/4 | 97/12 | 154/0 | 435/392/0/3373 |
| -2026110319 / 6 | 1/0/0/4 | 97/12 | 154/0 | 435/184/208/3380 |

All complete forward/reverse evidence objects match after both diagnostic LRUs clear. Reversal still computes new windows: visited tensor support is not guaranteed to stay cached. Native-cell LRU peaks are 89–92 entries (cap 128); this does not claim a separate 129-cell native eviction test. Every real coarse suite deduplicates four concurrent callers to one request, retains 128 entries after 129 misses, and recomputes the evicted entry. Screening/confirmation, fine/reverse collection and suite/oracle together compute 3091–3380 windows per fixture after startup, below the 12,000 cap. Startup counters are retained separately. All disk/time guards pass.

Across scales, 356/357 paired policy rows have identical complete native-cell hashes. Repeated representative cells within those rows remain shared observations, not extra native coverage. Coarse screening/profile overlap checks agree exactly. This is evidence traversal/coherence validation, not fresh-process final-feature determinism.

**Additional frozen criterion: FAIL — `Paired coarse drift`.** At seed
-2026110319, native target (-7808,-11392), the scale-1 province anchor is
(-6874,-11474), coarse cell (row -45,col -27). At scale 6 the corresponding
target (-46848,-68352) selects a different province, with anchor
(-52466,-68591), coarse cell (-45,-35). The target and fixed-grid native support
remain identical: 119/119 paired rows each. Anchor support matches at 118/119.
The independent province oracle reproduces both selections. `Provinces.at`
floors anchor coordinates in world units before comparing distances, so exact
cross-scale province correspondence is not guaranteed near a contact. This
does not justify changing geology-1 or treating displaced anchors as paired
native support. The failed original assertion remains unchanged and failing.

The frozen `summarize-td-landforms.py` rejects the complete raw matrix with that
exact error. The separately named, postcollection `export-negative-td-landforms.py`
first executes and requires that original rejection, then repeats every raw,
source and artifact check and records the failed paired assertion and its full
numeric mismatch. It does not change the selector, morphology criteria or
collected data, and it cannot turn the failed assertion or coverage gate into a
pass. Its own exact source digest and the frozen exporter digest are retained.
CI explicitly requires the original rejection as well as negative-result replay.

Counts describe combined serial diagnostic work sharing TD caches. They are not independent per-policy timings, cold/warm benchmarks or chunk-route savings. No integrated candidate is adopted.

### Concrete remaining morphology gate

Before extending point diagnostics, freeze a new bounded protocol that resolves candidate-center/orientation uncertainty sufficiently to supply actual TD ridges AND basins with two-sided fine extrema and finite longitudinal support on new held-out seeds at scales 1/6. Independently localize fine crests/troughs and document curved-feature and saddle ambiguity; retain matched native and scaled-tile results separately. Require the complete ridge/basin-by-seed gate rather than only favorable stations or central curvature. These seeds are now examined data and cannot become fresh validation for revised rules. Geological history/plausibility remains a separate unpassed gate.

## Scope and reconciliation

Production remains geology-1. This slice adds offline selection, collection and
analysis only; neither production nor the opt-in Java probe changes. The complete
production JAR entry comparison against retained PR #50 is required before launch.
No worldgen output, geological thresholds, save format or generator selection changes.

Fetched origin/main equals PR #50 merge
`ce91c6abdc9793bf14014fd6bf4c6ac689acd934`. GitHub confirms PR #47–#50 merged and
#9/#11 open. Read repository workflow, reproducibility and world-upgrade contracts,
the coarse/terrain/sampling reports, code and retained evidence. No ancestor
AGENTS.md exists. This branch follows `feature/` from the repository workflow.

Strict retained re-exports for PR #47 near/cold evidence (using its exact PR #46
artifact), PR #48 and PR #50 reproduce their committed JSON values exactly.
PR #49's LF checkout correction remains applied. These are new validation of
retained files, not reruns of those full JVM matrices. The new development
fixtures intentionally re-query 44 known location/scale pairs in the combined
profile workload. Their complete province, coarse/native and target/anchor tile
evidence exactly matches PR #50; these repeated inputs are not independent fresh
coverage or final-block determinism evidence. PR #50's six distinct
ridge/basin candidates still fail cross-axis extrema; its analytic elongated
controls remain separate synthetic evidence. Previously examined seeds, including
20261103, are never relabeled fresh held-out terrain.

## Frozen protocol and interpretation

[Protocol](td-landform-protocol-2026-11-03.md), selector, collector and evaluator
were committed and pushed at `5aebc684bfdce6bcfc73ccec0dc4344ee619dd8f` before
fresh-seed inspection. Development seed is 8675309; fresh held-out seeds are
2026110317 and -2026110319. Scales 1/6 repeat native support as paired sensitivity.

The selector requires explicit two-sided 50 m prominence/depth at five stations
over 1024 native pixels (1448.15 on diagonals), with bounded along-axis excursion
and residual. Four lattice orientations are tested. Tilted cross slopes cannot
become extrema through detrending. Curved/off-axis landforms can be missed;
saddles outside the bounds and interrupted extrema abstain. A cell mean locates no exact fine crest:
center uncertainty is +/-128 native pixels in each axis. The 50 m morphology
margin is not geological calibration and transfers no geology-1 cutoff. p5 is
excluded. Every failed confirmation and fallback profile remains visible.
The margin is not a calibrated model-error estimate; failure does not demonstrate
that a physical landform is absent elsewhere or at a finer support.

More precisely, the corridor test rejects saddles whose longitudinal excursion,
residual or cross shoulders fail the frozen bounds. It does not uniquely
distinguish a shallow longitudinal saddle/undulation that stays within all bounds
from a ridge corridor. Four tested orientations also do not establish a unique
continuous orientation. Such semantic ambiguity remains uncertainty, not evidence
for a named geological structure; fine crest localization is still absent.
“Basin” here means an elongated trough relative to two cross shoulders, not a
closed hydrological catchment or a demonstrated sedimentary basin. Axial and
diagonal corridors have different declared physical lengths/widths. Cell averages
and the gaps between their centers do not prove continuous fine-pixel morphology.

Each seed/scale has five fixed diagonal-transect coverage points, deliberately
selected ocean/coast/lower/intermediate/upper land contrasts, four signed grid
edge pairs and two actual province contacts. These are bounded descriptive
samples, not independent population draws. Feature profiles sample five along-axis
centers and both cross shoulders at every station (15 cells per feature).
Missing terrain strata or feature kinds cannot trigger an enlarged search.

Full native fine-cell means match the coordinate rectangle of each central
coarse average, while remaining different model products. Their disagreement
is not solely sampling error. Native relief uses all 65,536 fine pixels. Coarse
neighborhood range spans nine coarse averages. Fine-tile relief uses 25 quantized
samples from a separate 256-world-block rectangle. At scale 6 that rectangle
spans about 42.7 native pixels and uses TD's heightmap/noise path; the full native
cell still spans 256 pixels. Tile samples include the center-near sample at
index 127 at scale 1, not an independently localized fine crest. Do not equate
these ranges or fit a conversion factor. Province anchors and the existing
four-cell representative grid remain comparisons, never replacements for targets.

The collection caps are 81 screening plus <=20 confirmation requests and <=52
unique fine comparison locations, followed by reverse traversal. Six serial
JVMs have 6 GiB heap, 360 s startup/300 s command/45 min fixture/4 hour total
limits; window budget is <=12,000 after startup, with 1 GiB prelaunch and
512 MiB live disk reserves. Both 128-entry diagnostic LRUs clear before reversal;
TD/provider caches stay warm. This tests evidence traversal independence, not
fresh-process final-feature determinism or route performance.

## Evidence and verification boundary

New runtime collection is confined to NEW metadata-only disposable fixtures.
Only before first launch, seed/scale and matching snapshot metadata are established
together; no terrain is copied or continuing-save snapshot changed. Immutable
TD/models are linked, addon/probe copied. Only stopped disposable ONNX caches
are cleaned. Shared inputs, original template and unrelated temp/ are preserved.

Pinned MC 1.21.1, NeoForge 21.1.251, Java 21.0.6 Windows 11/amd64, official TD
2.3.0 CPU SHA-256 `3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8`,
model/config aggregate `64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9`.
Production SHA-256 remains `c5775ecafaefaaebb192d81152ab128d291d98e824fd4794e4b8d61f20850fa2`;
probe is retained PR #50 `abf66093bc7cdca8254c7fc6c8178358628d7dcdc381f544203278276c553a9c`.

The strict negative-result audit validates executed source bytes, artifacts, raw-log hashes and
the entire numerical command transcript, recomputes selection/evaluation, simulates
LRU misses/deduplication and preserves all failed gates. Portable replay runs in CI
without inference. Raw fixtures/logs remain ignored under
`runs/acceptance/td-landforms-2026-11-03-01`; no models, worlds or private logs
are uploaded.

The retained six-channel oracle checks the decode contract; p5 is never a
selector, profile, prior or geological-classification input. Green CI validates
evidence handling and replay, not a pass of the failed morphology coverage gate.

No new full-chunk/reopen matrix is claimed here. Retained PR #50's six fixtures /
twelve JVM launches preserve exact snapshots, complete sampled blocks and all
529 persisted terrain coverage/status/block-state records per fixture. This slice
revalidates that evidence and identical production/probe artifacts, rather than
repeating unchanged save-safety tests. New fixtures check snapshot-byte preservation.

Local verification passes JDK 21 build/domain/settings/coarse/probe checks,
resource checks (64 blocks, 158 recipes, 711 JSON), the existing catalog and
diagnostic tests, and ten new semantic/portable audits. These include independent
forward/reverse LRU replay, recalculation from all 25 tile heights, exact
screen/profile overlap and 44 retained point comparisons. The original frozen
exporter's rejection is an explicitly required test outcome, not a claimed pass.
All six JVMs exit zero; stopped-case optimization caches are removed and about
1.86 GiB free remains. No acceptance process or game/RCON listener remains.
No production or probe Java source changes.

## Remaining gates and compatibility

Keep explicit `synthetic-prior-1` deterministic SHA-256 seed/row/column ordering
and arbitrary weights in [0.4,0.6] for competing geological interpretations.
No geological posterior, confidence or rock selection is established. Morphological
validation cannot distinguish recovered geological histories. Independent seeded
history/plausibility/coherence criteria remain necessary even if TD coverage passes.

No palette, dike, mineral system or integration is introduced. Strict guards,
optional Ulti-World and #5's stronger failed final-block assertion remain intact.
#9/#11 remain open. PR #47's isolated-query savings are not route savings; PR #46's
inconclusive cold-route result stays visible. No integrated candidate or new
comparative performance benchmark exists in this slice.

Any changed output still requires a distinct immutable generator identity and
explicit new-world-only selection. Genuine continuing saves must reject both
version directions before Ready; exact original-artifact restoration/reopen must
preserve snapshot bytes, complete sampled blocks and every persisted terrain
coverage/status/block container. Never migrate or rewrite continuing geology-1
snapshots. An integrated candidate additionally needs alternating paired CPU runs
against then-current main on NEW fixtures separating startup, genuine cold tensors,
warm sampling and full chunk routes with actual requests/new-window counts.

## Reproduction

```powershell
./scripts/bootstrap.ps1
./gradlew.bat build runtimeProbeJar
py scripts/test-td-landforms.py
py scripts/verify-td-landforms.py --java <java21> --td <official-cpu-jar> --baseline <retained-PR50-addon> --protocol-commit 5aebc684bfdce6bcfc73ccec0dc4344ee619dd8f --output <NEW-output>
# Frozen exporter must reject this retained matrix with "Paired coarse drift".
py scripts/summarize-td-landforms.py <NEW-output> --output <rejected-output>
py scripts/export-negative-td-landforms.py <NEW-output> --output <portable-json>
```

Do not use these already inspected held-out seeds as fresh validation of a revised
selector. A revised geometry/search protocol needs a new preinspection freeze and
new seeds. Strict re-export after final Windows checkout is part of acceptance;
LF attributes preserve exact executed source bytes without changing recorded hashes.
