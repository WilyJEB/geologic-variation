# Candidate D: bounded offline interface preparation

2026-11-12. **Decision 1, conditional:** the abstract ownership and resource
preparation is coherent enough for a separately authorized native
implementation-preparation decision. No runnable native freeze, implementation,
execution, acceptance, durable evidence or hard deadline is established.

Initial local/fetched branch/GitHub PR62 head: 86e6639d292292966e76e1843c581d6757d0a34d.
Main/base: 513c4ca1e950969453faf52723f7ee68c7d6c329. PR62 remains open,
draft/unmerged; starting PR CI43289442636 passed. Final-head CI is reported
separately. Historical containment/boundary/design and both preparation reports,
models/tests/packages, navigation-3 outcome and carried gates were reviewed.
Historical partial interfaces and packages remain unchanged.

## What the small interface means

`staged_helper_interfaces.py` is a finite symbolic protocol, not a replacement
for the historical native-facing ports. Its event order represents required
linearization points. It has no locks, transport, native functions, IPC, helpers,
allocator, case runner or clock. Initial state abbreviates successful atomic
W/S creation in H: C alone owns H/J, helpers own neither. Either first-helper
order and the pre-entry C-death prefix are covered by the unchanged containment
model/package, reproduced transitively by the new audit.

Native creation must register exact returned process/thread handles locally
before metadata/logging and atomically establish H membership. C retains each
successful partial creation even when later attribute deletion or metadata fails.
Failure before creation leaves no member. No create-then-assign fallback.
Bootstrap allowlist contains only real C DUP|SYNC and private endpoint handles;
never H/J. S and targets receive no job handles. No remote-close operation exists.

Fixed epoch1 transfer IDs identify role W and J/Cwait/Swait/H/P/T with immutable
source identity, type and rights (jobs QUERY|TERMINATE, waits SYNC, targets
QUERY|SYNC). These labels are symbolic IDs, not numeric receiver handles.
W executes a pull into its own process. Issuance pins C's exact source token
until result registration or confirmed receiver death. No retry of failed,
lost-ACK or replayed issuance. A new epoch would require a new case entitlement,
not an automatic retry. Endpoint authentication and actual token transport are
native implementation obligations.

`establish_control(True)` is an explicit modeled assumption/barrier: retained
J and exact C/S waits are installed; independent control already runs and owns
its stable inventory without calling transfer/sampler/sink or their locks.
False or partial installation cannot arm. ACK does not establish this barrier.
Only then can `issue(H)` occur. A native implementation must prove this local
ordering and independent execution; a message claiming readiness is insufficient.

On every successful return W registers its local copy first, before ACK or
logging, including returns after sealing. Failed acquisition owns no new copy;
previous partial successes remain owned. Lost ACK never removes an owner.
ACK validates epoch, role, unique transfer and successful acquisition. Target
creation remains forbidden until confirmed H ACK and continuing readiness;
creation/resume additionally needs unchanged exact-target identity/retention
handshake from the historical contract. No target-side H/J copies are allowed.

C death before successful H return last-closes H under the documented semantic
assumption, including a pending pull that has not succeeded. At a racing native
return, either acquisition wins and already-armed W owns H, or source teardown
wins and the pull fails. A successfully returned copy cannot be discarded because
its ACK or row is missing. C death afterward leaves W's copies intact. W death
leaves C responsible. C and W each terminate retained J directly when peer/S
blocks/dies. Both controls dead/blocked, blocked/failed native termination, OS
suspension and disk failure retain the historical explicit limitations.

Survivor inventory includes exact creation handles and every raced/unaccepted
target copy, not just ACKed targets. Job membership catches an untransferred
created target; full known-handle waits are still required. The fake maximum
target set P/T is supplied independently of ACKs. Cleanup requires successful
empty J membership AND active0 AND every known target wait signaled. None may
be inferred from termination success, parent exit, last-close or missing query.
Errors remain sticky case failures even if subsequent proof succeeds.

## Finalization and the self-containing job

Seal stops new issuance and ACK acceptance. Already-issued acquisitions remain
registered/inventoried and pinned until completion or exact receiver death;
seal cannot cancel a kernel operation. Retain independent J control through
target proof. Quiesce all local handle users, including waits/transfer/evidence
users, before consuming each local close once. An unjoined user forbids closing
its handles; preserve inventories and incomplete evidence and stop the suite.
Failed close consumes the close entitlement and remains failure, never retry.

With C alive, C retains H through exact W/S shutdown waits and H membership/
accounting verification; it may terminate H after target proof if a helper blocks.
That does not prove worker quiescence or repair missing records. After C death,
W proves J, stops/waits exact S, quiesces users, closes J and auxiliary local
copies, then disposes of H last. H contains W. Last-close may kill W before
return: no W post-close row, own-exit verification or successful finalization is
invented. The fake marks that fact only as external model commentary. If no
surviving verifier exists, cleanup acceptance/evidence remain incomplete even
if assumed OS containment eventually succeeds.

## Static resource partitions (unchanged caps)

The executable CALLS/BYTES tables are disjoint maxima, never transferable.
Every issuance, including failed bootstrap/acquisition/query/write/close and
GetLastError/clock/file/flush operations, must be charged before issue to its
role, phase and category. No implicit library operation is free. These are
abstract adapter obligations, not audited Python-runtime native-call counts.
An adapter unable to stay inside them must stop preparation, not borrow cells.

| Role | Ordinary calls | Cleanup calls | Ordinary bytes | Cleanup bytes |
| --- | ---: | ---: | ---: | ---: |
| C | 1100 | 448 | 2MiB | 1MiB |
| W | 1100 | 448 | 2MiB | 1MiB |
| S | 600 | 96 | 1MiB | 512KiB |
| P | 136 | 16 | 128KiB | 128KiB |
| T | 136 | 16 | 128KiB | 128KiB |
| Total | 3072 | 1024 | 5.25MiB | 2.75MiB |

C/W ordinary: 200 control calls (100 steps before5s: one combined peer/S zero-time wait plus one monotonic-clock query), 700 bootstrap/transfer/query,
200 evidence I/O. Cleanup: 400 control calls (200 steps for10s with the same two-call shape), 40 termination/query/
close, 8 batched evidence I/O. Forty covers at most2 job terminations,2 exact
process terminations,4 job queries (J/H membership+accounting),4 known-process
waits,20 local closes and8 error-detail calls. No failed query retry. Discovery
or wait/proof needs beyond these finite cells are incomplete, not truncated proof.
Ordinary 700 covers a maximum20 local owned handles total (including bootstrap,
creation, transfers and endpoints; never more than20 closes), three attribute lifecycles
(two helper creations and P), job setup/limits, identity/membership/path queries,
resume/handshake and error/clock calls; the rest is unused safety capacity.
These maxima constrain the future adapter, not permission to create extra targets.
S's400 sample/query/wait covers64 samples *6 calls plus16;200 covers bootstrap,
clock/error/evidence; cleanup32 quiesce/closes and64 evidence. P/T136/16 cover
their bounded create/handshake/wait/exit/close/error/clock work. No extra writer
thread: each C/W has control+one transfer/evidence worker; S one sampling thread.

At quota exhaustion initiate cleanup from reserved cells; use only remaining
own cleanup cells. Never complete an over-budget case. Batched bounded memory
records keep control independent of storage; 2 rows/API at <=512 bytes each
plus64 samples <=4KiB and full256-slot membership records fit byte partitions.
Rows exceeding bounds fail without truncation-as-success. Failed write bytes
remain charged. No per-call flush requirement; native durable acceptance still
requires complete start/end/error rows, raw partial tails and successful flush/
fsync. Missing or memory-only rows remain incomplete. No crash-proof claim.

8MiB/case <64MiB; six fixed row partitions total48MiB plus separate suite-only
C provenance/source-copy partition8MiB =56MiB <128MiB. Source copies larger than
8MiB stop freeze. Suite-only C setup/finalization uses row1's ordinary and row6's
cleanup cells respectively, with no extra issuance allowance; unused/skipped
rows never donate quota. No output entitlement depends on another row's success.
The512MiB sampled harness bound includes bounded buffers <=8MiB/role,256 member
slots,64KiB total live attribute storage; runtime/interpreter overhead remains
to be measured. Attributes are serially reused only after users quiesce.
Target active2/commit128MiB and separate sampled128MiB remain. Disk reserve1GiB,
15s/case from before bootstrap, reserve10s by5s,120s suite and six failure-charged
rows remain unchanged. All limits apply, earliest wins. Arithmetic is feasible;
50ms polling, startup before2s, timing/memory/disk fit are not demonstrated.

## Evidence classification and next gate

Documented Windows semantics: receiver-local duplicate values/noninheritance and
source/receiver DUP rights ([DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle));
pending-wait close is undefined ([WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject));
creation-time JOB_LIST and real-handle inheritance allowlists
([creation attributes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)).
Last-close/membership/termination documentation remains linked in the unchanged
containment review. Actual atomic failures/ambient hierarchy/ABI/rights are native
obligations. Successful eventual OS cleanup and independent control are modeled
assumptions. Fake tests check only event-order ownership, ACK gates, survivor
inventories, seals/quiescence and static arithmetic. They cannot prove independent
native execution, OS termination, timing fit, durable evidence or cleanup acceptance.

Reproduce `python scripts/audit-staged-helper-preparation.py`; `--write` only
creates this separate JSON/ZIP; `--check-runtime-root` reads all70 retained files.
The audit reproduces all earlier packages and57 earlier fake tests/39 frozen inputs.
New8 tests are offline only. Final Windows reproduction and CI follow commit.

**Stop here. Exact next authorization gate:** separately authorize one bounded
native implementation-preparation decision for candidate D, reviewing whether
real-role readiness/receiver-local registration, authenticated transport adapters,
quiescence/survivor verification and exhaustive native-call/resource accounting
can be implemented within these partitions and existing caps. This result grants
no native bindings, transport/helper/runner/allocator implementation or execution.
Any later implementation needs explicit scope; exact executable/context/resource
freeze with passing CI and failure-charged native allocation remain later gates.

Navigation-3 root/frozen sources/artifacts/consumed slot/approvals/ledger/partial
evidence stay verbatim, INCOMPLETE/zero remaining. Preserve historical failures,
PR59 negative contacts, geology-1, continuing-save safety, production guards,
immutable inputs, optional Ulti-World, viewer repairs and unrelated temp/. #9/#11
and geometry/support/uncertainty, historical numerical reproducer, joining,
fresh validation, paired startup/cold/warm/full-route performance, versioned
adoption/bidirectional rejection/exact restoration/reopen/snapshot/block/
persisted-container gates remain open. PR54 exhausted; final capture compile-only;
historical missing arrays/indices/ULPs unknown. No local native/process-control,
preflight/socket, Java/Minecraft/TD/provider/model or save execution occurred.
PR62 stays draft/unmerged. Monitoring adds no player-visible improvement.
Terrain-aware prototype review is available now through retained
[panel](evidence/td-story.html) and [viewer](evidence/td-region-visual.html);
further monitoring is not a prerequisite.
