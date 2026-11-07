# pressure-visual-1 — frozen offline comparison

Base: reconciled origin/main d995cf8415927e9a3a5fc90eb769a48c09364f27,
merged #56; GitHub #9/#11 open on 2026-11-07. No TD execution permitted.

Select exactly ONE reduced pressure sequence and its scale6 paired reference
before evaluating either. Retained PR56 reconstruction request ordinals:

* scale1: [85,90,231,232,233,234,235,236,237,238,239,240,241,242,243,244,326,366]
* scale6: [85,90,231,232,233,234,235,236,237,238,239,240,322,362]

Both begin with the unchanged source-derived startup candidate (coarse [0,0,1,1]).
These are the two large patches, every public call in events238/240, then the
first A/B native misses. Keep every selected request's original bounds, role,
climate flag and order. Different public ordinals identify corresponding events,
not equal request numbers across scales. Exact selected objects are exported.

Rationale from retained traces, not a new candidate evaluation: patch90 creates
the four distinguishing init keys in both histories. Patch85 supplies earlier
cache/ancestor context missing from #56's failed two-call check. Event240 contains
the first predicted distinguishing eviction (scale1 request238); event238 supplies
the preceding command's different tile reads. Include whole commands so coarse
and provider reads are not silently dropped. This deliberately tests the local
pressure episode rather than assuming all accumulated pressure is necessary.
It may fail because older missing pressure or dependency creation groups matter.
No claim of minimality: 18/14 requests, including two large patches.

First audit retained full-history counters with the frozen #56 model, stopping
on any disagreement. Add observational tracing without changing model rules;
require exact original full-history batches, evictions and terminal cache order.
Trace creation DAGs, dependency read order/version, cache order before/after each
request, per-slice eviction timing and exact target groups. Separate source-derived
predictions from runtime counters; actual historical startup/internal state unknown.

Compare each reduced arm to its own full history: distinguish key creation
ancestry (stage/key/ordered batch members/recursive dependency reads), target
batch membership and ancestry, relevant pre-target cache membership/access order,
and distinguishing key eviction timing/context. Report every criterion even if
one fails; do not try any replacement sequence, minimize, search or retune.
Any failed criterion stops this numerical investigation and prohibits preparing
a runtime experiment in this slice. No historical float bits can be inferred.

Visual: exactly one retained native terrain field, first field in the existing
PR53 geometry evidence, selected by archive order rather than appearance. Show
its retained sample sites and finite coordinate extent, descriptive neighboring
sample elevation differences, missing/edge support and abstention. No confidence
scores or confirmed extrema. One conceptual connected contact overlay may be
drawn on this field, explicitly labeled an authored synthetic-history illustration,
never a computed geological result. No production selector or new terrain queries.

Deliver deterministic archive/manifests, portable offline replay and corruption
tests, report and static visual. Existing #54/#55/#56 exports and failures remain
unchanged. Historical arrays/indices/ULPs unavailable; #54 ran4a2fa1c; final capture
mixin compile-verified only. All carried-forward validation/performance/adoption/
save-safety gates apply; geology-1, guards, immutable inputs, optional Ulti-World
and unrelated temp/ untouched. Both adoption gates remain insufficient.
