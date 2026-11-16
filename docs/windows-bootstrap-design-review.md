# Bootstrap design review: decline infrastructure expansion

Decision 2, 2026-11-12: the remaining work is larger than a small transport
adapter. Do not implement or freeze a native bootstrap under the existing
six-case proposal. Keep the injected harness as offline preparation and use
retained terrain panels for the next product design discussion. This is a
bounded design decision, not a finding that Windows cannot support the design.
No native API construction, helper, allocator, runner, socket/preflight, Java,
Minecraft, TD/provider/model execution or save access occurred in this review.

## Reconciled basis and scope

Local HEAD, fetched origin branch and PR62 head initially agree at
`88affa87c6c055922b65f2b2b8b0aa24f1cd78b3`; main/base remains
`513c4ca1e950969453faf52723f7ee68c7d6c329`. PR62 is open, draft and unmerged.
Starting-head push CI43279883831 and PR CI43279894638 passed (reused evidence).
An approved fetch followed the restricted FETCH_HEAD write failure.

Reviewed AGENTS.md, the [harness preparation](windows-validation-harness-preparation.md),
its source, 21 fake tests, schema and portable JSON/ZIP; previous monitor source,
23 tests and preparation package; navigation-3 outcome and process review;
observation-history and axis/numerical controls and their frozen evidence chain.
The earlier preparation is historical and unchanged. This addendum evaluates its
unimplemented bootstrap, not the navigation-3 executed helper. No mock correction
is necessary to substantiate the stopping decision: the defects below are
explicit future interface requirements, not silent repairs or native proof.

## Exact process roles and the missing first handle

Call the controller C, watchdog W, sampler S and target parent/child P/T.
C must retain W and S process/thread handles returned by their exact creation;
no PID lookup is needed for these roles. C can obtain a real self handle by
duplicating its local current-process pseudo handle. W and S cannot use C's
numeric handles directly. For a receiver-side pull executed in W, both the
source-process handle for C and target-process handle for W must be usable in W
with PROCESS_DUP_HANDLE (0x40). W's local current-process pseudo handle can be
the target; the source C handle still has to get into W first.
[DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle)
documents these process rights, receiver-local result values and pseudo-handle
rules. The same reasoning applies independently in S. A SYNCHRONIZE-only C
duplicate from Control.arm is insufficient for pulling later handles.

One feasible *candidate*, not an adopted implementation, is an explicit
inherited handle allowlist for harness creation only: real C process handle
with DUP|SYNC, private IPC endpoints and a fixed bootstrap descriptor. W can
then pull job and S handles from C using source-table tokens. C retains each
source token until the transfer phase ends. C already holds exact W/S creation
handles with duplication rights. W/S wait duplicates use SYNC; sampler target
copies need QUERY|SYNC; N6's C-owned S handle needs TERMINATE as well. Job in C
needs SET_ATTRIBUTES and ASSIGN_PROCESS for limits/creation, QUERY and TERMINATE;
W receives only QUERY|TERMINATE (0xC). Parent in W uses 0x101001; controller
retains creation process/thread handles and the thread's resume right.

This candidate changes harness creation, not target creation. A
[HANDLE_LIST](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
requires inheritable real handles and CreateProcess bInheritHandles=TRUE.
CreationBindings.atomic currently hardcodes FALSE, one attribute and target
JOB_LIST. It cannot create this bootstrap unchanged. Target P must continue to
use FALSE with JOB_LIST and CREATE_SUSPENDED, never inherit a job handle, and
have no create-then-assign fallback. Separate creation paths, allowlist lifetime,
clearing inheritance, IPC framing and rejection of unknown tokens are required.
No names, recyclable PIDs or remotely returned numbers may become local owners.

## Ownership and failure obligations not supplied by the current interfaces

The following is a requirements table for the rejected expansion. It is not a
tested native state machine or a new authorization contract.

| State/event | Required owner and action | Failure disposition |
| --- | --- | --- |
| Before W/S creation | C owns configured target job and bootstrap endpoints; own each successful process/thread return before logging | Charge row even with no target; close local resources; retain every partially created harness process for stop/wait |
| W/S created, not armed | C retains W/S handles; receiver owns each inherited bootstrap handle on entry | No P creation; C death must be observed through retained C wait or receiver startup logic; suspended/not-yet-running helpers need separate cleanup coverage |
| Arm pull succeeds | W owns job, C wait and S wait immediately, before ACK; distinct source-C DUP handle remains valid through transfers | Partial pull or lost armed ACK: no P creation; no remote close or retry; receiver unwinds local ownership, C stops/waits exact helpers |
| Both control loops ready | C polls exact W/S waits; W polls exact C/S waits using stable job/wait copies | Only after readiness may C atomically create P suspended in job; no callback to transport on either polling path |
| P creation returns | C owns P/thread before metadata, attribute deletion or IPC; W already holds job | C death before parent pull: W terminates job; metadata/creation error: job termination, no resume |
| Parent pull/ACK | W owns P as soon as receiver-side duplication succeeds; source P token remains C-owned | Lost ACK: P never resumes, W keeps its copy until finalization; sender cannot reclaim a remote numeric value |
| Transfer blocked or peer/S death | Independent control loop polls deadline/interruption/exact waits and issues retained-job termination | No transfer join, sampler response, logging or disk operation may precede termination; failed/blocked native termination is incomplete |
| Interruption or concurrent trigger | Sticky case failure and one terminal control action per role; all successful acquisitions remain owned | Second interruption never resets entitlement or abandons ownership; action errors stay failures even if later drain succeeds |
| Finalization | Stop issuance, quiesce transfer and sampler users, verify empty membership AND active=0 AND every known wait signaled, close each local copy once | Unjoined worker: do not close handles it may use; stop suite, preserve partial evidence; failed close consumes local ownership and invalidates case |

W dying leaves C responsible; C dying leaves W responsible. Both dying is outside
an absolute response guarantee. Bootstrap cannot assume W is polling before its
job pull finishes. No target may exist in that interval, but partially launched
W/S still need cleanup. A stopped/suspended helper cannot execute its own C-death
check. Solving *that* controller-death gap needs a separately reviewed containment
arrangement for harness roles or an explicit weaker bootstrap-cleanup claim.
The target job cannot contain W/S without changing the independence design.
Kill-on-last-job-close does not solve it while any other job copy remains open.

Close-once is local, not a distributed ACK protocol. Owner.close consumes a
handle before attempting close, but has no sealed lifecycle or concurrent-use
guard. Control.parent can race Control.step and acquire after firing; rejecting
the ACK does not remove that acquired ownership. Its table must remain alive
until the worker stops. Closing during a pending wait has
[undefined behavior](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject).
Process teardown can release its own handles, but does not supply durable rows
or prove target cleanup. A blocked worker may require exact-process teardown;
which survivor verifies its handle set is additional design, not Owner.close.

## Concrete interface audit

| Current port | Real-role connection needed | Mismatch |
| --- | --- | --- |
| Wiring.start / transport.arm_watchdog | C transfer worker sends typed source tokens; W worker pulls and ACKs; W control polls independently | Fake Transport calls W synchronously in C's test thread; no IPC, ready-loop barrier, bounds or peer authentication |
| Wiring.api.atomic(job, argv, acquire) | C adapter maps immutable executable, correctly quoted mutable Windows command line and cwd to CreationBindings.atomic | Binding requires six arguments including executable/command_line/cwd; no adapter or command construction policy exists |
| CreationBindings.pull(source, token, receiver, rights, acquire) | Execute in receiver, target its own process, register locally without blocking | Accepts arbitrary receiver and callback; tests permit a remote result to enter caller's table; receiver locality is a comment, not enforced |
| Control.arm and Control.parent | W receives role-bound job/C/S/P tokens; C's symmetric Control uses W/S waits | No identity/type/role/epoch validation; ACK strings have no transfer ID; no replay rejection or finalization seal; sampler/verifier child copies absent |
| Wiring.start | C worker performs metadata/transfer/resume while C control thread continues | No thread/scheduler implementation; synchronous blocking start cannot itself provide independent C polling |
| Monitor and WindowsAPI | S samples, C verifies through separate retained handles; independently configured job limits before P exists | create_job sets kill-on-close only, not active-process2/commit128MiB; adopt_suspended assigns after create and is forbidden here; cleanup emits synchronously |
| DurableRows / check_evidence / schema | Off-control bounded buffers, role streams, authenticated known handles and per-case evaluator | No bounded queue/byte quota, schema validation or close/ACK/coverage evaluator; checker accepts a simplified trace and does not establish complete close ownership |

The fake blocked-sampler/sink test proves Control.step does not reference those
objects; it does not schedule independently blocked processes. Mock pointers
establish intended flags and rights, not real receiver context or ABI acceptance.

## Revised six-case cap audit

All figures below audit the existing proposal, allocate zero rows and preserve
bootstrap/setup/spawn/transfer/interrupt failures as consumed cases in any later
authorized design. No retry, replacement row or cleanup overrun is permitted.

| Cap | Audit result and missing condition |
| --- | --- |
| 3 harness +2 targets | Logical roles fit5, but shell/console hosts, interpreter/runtime threads and any cleanup supervisor are not budgeted by an executable freeze. No extra persistent helper fits. The two-control-thread plus one worker layout cannot also require an independent blocking writer thread without review |
| 15s/case, cleanup reserve10s from no later than5s; suite120s | 6*15=90 leaves30s suite setup/finalization; must start case clock before bootstrap and include failed starts. No process can enforce the suite clock after all control roles die; blocked native calls remain unbounded observations |
| N1/N2 | Twenty samples at100ms need about1.9s plus startup/exit; child4s in N2 leaves under1s for startup/handshake before5s. Neither fits by assumption; late readiness fails, never shifts the clock |
| N3/N5/N6 | Readiness and child retention must finish before fixed2s trigger; initiation within1s and drain within10s after trigger also obey15s. N6 intentionally loses sampler evidence; survivor must already have independent child/known-handle inventory, absent from Wiring |
| N4 | Requested <10ms child lifetime does not promise measured lifetime; TotalProcesses=2 is distinct from identity coverage. Missing identity stays unknown |
| Target commit128MiB and active2 | Native limit structures and flags must be set and verified before creation; current create_job does not set them. Job set requires SET_ATTRIBUTES. Target working-set sum128MiB is separate sampled evidence |
| Harness working-set sum512MiB | S cannot be sole measurer of its own death/block case; observer, exact handles, sampling cadence and unavailable readings need specification. No current native harness memory limit; no peak guarantee |
| Disk64MiB/case,128MiB suite,1GiB free | Include partial bootstrap, source copies, all streams and truncated output. Aggregate stops first; writers need prepartitioned issued-byte limits and finite in-memory records. Blocked persistence cannot be on control path; current DurableRows has none of this accounting |
| 4096 calls,3072 ordinary +1024 reserved | Not yet a static partition: independent roles need disjoint tokens, including bootstrap calls, transport I/O, failed calls, clock/wait scheduling, memory, teardown and closes. No shared lock on control path |
| 64 samples,256 members,64KiB attributes | Maximum2 target processes does not authorize opening256 handles. Attribute two-call sizing counts both issuances; no resizing after required failure. Every successful partial acquisition requires reserved finalization capacity |

Numerical check: two control roles *300 steps *2 waits =1200 wait calls across
15s, not2400. If both continue throughout the10s reserve,200 steps/role consume
800 reserved waits, leaving224 of1024 for termination, verification, worker
shutdown, transport disposal and closes. A verifier polling two target waits
plus membership/accounting every50ms for10s adds800 more: that naive composition
cannot fit the reserve. A future design must stop redundant control polling or
choose a smaller bounded proof schedule, without dropping peer-death coverage.
One successful proof uses2 job queries plus one wait per known target/harness
process; the number of retained copies and failed acquisitions must be frozen.
An unsignaled successful poll may be followed by a bounded scheduled poll; a
required API error cannot be retried away.

For two retained live targets Monitor.sample uses2 membership queries plus
2*(wait+member+wait+memory)=10 API calls/sample before initial discovery.
64 samples can therefore cost640 calls, plus discovery/identity/path, harness
memory, exit checks and evidence I/O. That does not alone exhaust3072, but it
does not prove a full partition. Calling Python wrappers instead of counting
their native issuances undercounts identity's multiple APIs and flush/fsync.
Budget failure must use reserved tokens before exhaustion, never borrow another
role's or case's quota. A fixed schedule must specify whether scheduler/clock
and runtime-internal calls are in scope; an all-runtime Win32-call count is not
what these injected adapters measure. This ambiguity blocks a runnable freeze.

## Bounded alternative and next gate

Stop native monitoring work here. Keep historical mock interfaces explicitly
partial and retain the six-case proposal as unallocated, unimplemented and not
ready for native authorization. Review the terrain-aware visual concept now via
[story panel](evidence/td-story.html) and [region viewer](evidence/td-region-visual.html).
Discuss finite-support terrain properties, coherent seeded synthetic histories,
competing interpretations and visible unknowns using that retained evidence.
This can guide what a player should see without another client attempt; the
monitor review itself adds no gameplay and is not a prerequisite to that review.

If native monitoring is later necessary for a concrete decision, the next gate
is a separately authorized **offline implementation-preparation** scope that
explicitly accepts the additional harness bootstrap lifecycle work. It must
resolve helper containment before readiness, inheritance/IPC/local receiver
enforcement, adapter signatures, worker quiescence and survivor inventories,
plus a static per-role ordinary/cleanup API and byte partition. Freeze fake
failure schedules and reject lost/replayed ACKs and post-finalize acquisition.
Do not implement an allocator or six-case runner merely to make this review
appear complete. Exact native helper/runner/command/context/resource freeze and
passing CI must precede a separate explicit failure-charged native allocation.
No hard deadline or runnable native freeze is asserted here.

## Verification and preservation

This slice adds only this review. Previous preparation JSON/ZIP and all harness
sources/tests/schema remain byte-identical. Reproduce their deterministic
packages after final Windows checkout with the existing audit (no --write is
needed when bytes already match), including --check-runtime-root. Run existing
fake harness/monitor, retained-process, observation-history and axis tests;
strict preparation replay and retained runtime replay preserve INCOMPLETE.
Final commit/CI and final-checkout audit results are reported in the handoff.
CI compilation and mocks remain separate from native/runtime acceptance.

Navigation-3's entire70-file root, frozen39 inputs, consumed slot, approvals,
ledger and partial evidence stay verbatim; no new roots, flags or ledgers.
PR59 negative contacts, frozen failures, geology-1, continuing-save safety,
production guards, immutable inputs, optional Ulti-World, viewer repairs and
unrelated temp/ remain preserved. #9/#11 stay open. Geometry/uncertainty,
historical numerical reproducer, joining, fresh validation, paired startup/cold/
warm/full-route performance and versioned adoption/bidirectional rejection/
exact restoration-reopen-snapshot-block-persisted-container gates carry forward.
PR54's four launches remain exhausted; final capture mixin remains compile-only;
historical missing arrays/indices/ULPs remain unknown. PR62 stays draft/unmerged.
