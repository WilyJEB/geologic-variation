# Candidate D: stop at native implementation preparation

2026-11-12. **Decision 2.** Do not implement candidate D under the current static
partitions. Its ownership graph is plausible, but a complete resource-accounted
native adapter cannot be specified from this preparation as a small wiring change.
The concrete obstacle is the control/evidence/finalization issuance contract:
pacing, API timestamps, error retrieval, transport teardown and runtime operations
have no complete bounded schedule in the existing cells. Resolving that requires
substantial additional runtime/transport accounting infrastructure or an explicitly
changed requirement. This is not a proof that every possible Windows design is
impossible. No native implementation or execution was performed or authorized.

## Reconciled basis

Local HEAD, fetched origin/codex/retained-navigation and GitHub PR62 head agreed at
`a5161ec851e82959fd1fb6ab780ecd580d5298b8`. Fetched main and PR base agree at
`513c4ca1e950969453faf52723f7ee68c7d6c329`. PR62 is open, draft and unmerged.
Starting-head PR CI43292435740 passed; this is reused build/offline evidence.
Final-head CI and final Windows reproduction are reported separately.

Reviewed AGENTS.md; staged interfaces, eight fake schedules and JSON/ZIP;
containment review/model/tests/package; bootstrap boundary preparation and design
review; both historical Windows preparation reports, injected ports and portable
chain; navigation-3 outcome/process review and carried observation/axis gates.
Earlier partial interfaces and packages remain unchanged. This separate report
does not turn their conditional positive decisions into native proof or erase
their stopping results. No abstract correction is needed to expose this obstacle.

## Ownership and readiness assessment

| Obligation | Concrete adapter requirement and decision |
| --- | --- |
| First helper and partial creation | C configures H/J before creation; each W/S uses creation-time JOB_LIST(H), with H/J excluded from inheritance. On successful CreateProcess return, register BOTH exact process/thread outputs in preallocated C slots before error formatting, attribute deletion, metadata or logging. Keep successful partial creations if later work fails. No create-then-assign fallback. C alone owns H initially, in either helper order. Native ABI/ambient hierarchy/failure semantics remain unvalidated. |
| Local W readiness before H issuance | A credible candidate barrier is W's main/control thread installing immutable J/Cwait/Swait slots, completing its first actual wait/deadline control iteration, and publishing a release-ordered local generation to its sole transfer worker. The worker acquires that generation and rechecks a sticky stop/seal state BEFORE issuing H's DuplicateHandle. Only this control thread can publish readiness; an IPC ACK cannot publish it. Control continues independently while the worker blocks. Memory ordering, interruption and worker failure need source audit; readiness never guarantees future scheduling or survival. This is a proposed local barrier, not implemented or fake-proved. |
| Local acquisition and validation | Receiver worker validates fixed epoch/role/transfer/type/rights/source slot and expected raw identity against an immutable role manifest, executes DuplicateHandle into itself, then stores the successful local result in a reserved inventory slot as its first nonfallible local action. Validation must not allocate/log before registration. Register unexpected successful returns too, then fail. Do not trust arbitrary remote numbers as local handles. Exact source handles stay pinned until return registration or confirmed receiver death. No source reuse, remote-close flag, retry, new epoch or ACK-based reclamation. |
| Partial/lost/replayed transfer | One issuance per fixed ID. Each partial success remains owned with or without ACK; rejected/replayed/lost ACK prohibits target progress. C death before acquisition leaves H last-close containment; acquisition winning the kernel race leaves already-armed W owning H. A returned H copy must be registered even after seal. The graph assumes those outcomes; actual race behavior is not tested. Process death between kernel success and user registration leaves missing evidence, never invented registration. |
| S/targets and cleanup independence | S/P/T receive no H/J handles. Each process closes only its own copies. C/W control has retained J and stable peer/S waits; it directly terminates J before transport join, sampler response, writer or shared lock. Peer/S blocking is handled by the case deadline; peer/S death by retained waits. No transfer completion is required to initiate containment. Both controls blocked/dead, blocked termination and OS suspension retain explicit limitations. |
| Complete survivor inventory | C retains exact creation outputs even before transfer. W retains every successful pull, including late/unaccepted copies; S needs its own exact acquired set. For C-created P not transferred, W's J membership can contain it, but does not supply C's exact handle wait. P-created T introduces a similar publication/death gap. Missing exact known-handle coverage remains incomplete; job-empty alone cannot repair it. A finite preallocated single-producer publication/inventory protocol and terminal worker snapshot are required, not supplied by an ACK list. N4 explicitly permits missed short-lived identity, not fabricated lifetime coverage. |
| Seal and quiescence | Stop issuance/ACK acceptance, resolve every pending acquisition by registered result or exact receiver death, retain source slots meanwhile, and join every local handle user before closing its copies. A blocked transfer/evidence worker cannot be joined by assumption. Exact process teardown may release its table but loses rows and is failed/incomplete finalization. Stop the suite; do not close a handle under a pending wait. |
| Helper shutdown and H disposal | With C alive, retain H until exact W/S shutdown waits plus H membership/accounting proof and local quiescence. H termination after J proof can contain blocked helpers but cannot certify their worker records. After C death, W proves J, stops/waits exact S, quiesces users and closes auxiliary/J copies, then disposes H last. H contains W: last-close may kill W before return. No post-close success row, verified own exit or complete finalization may be manufactured. No survivor means incomplete evidence. |

Cleanup acceptance remains **successful empty membership AND active0 AND all
known target waits signaled**. Errors are sticky failures even if later drain
succeeds. Missing records, failed/late queries and unresolved inventory are unknown
or failures. No termination return, process exit, ACK or close substitutes for proof.

## Why the static partitions do not establish adapter feasibility

Keep every CALLS/BYTES cell unchanged. C/W each have ordinary 200 control +700
bootstrap/transfer/query +200 evidence, and cleanup 400 control +40
termination/query/close +8 evidence. S has 400+200 ordinary and32+64 cleanup;
P/T each136 ordinary and16 cleanup. Totals remain3072/1024. No unused cell, role,
phase, skipped row or suite quota is available for borrowing.

The proposed one combined peer/S wait plus one clock query can detect **either**
death in two explicit calls. It cannot report both deaths, prove target drain,
or establish cadence. Microsoft documents that a zero-time wait returns
immediately, and wait-any returns the lowest signaled index. Thus 100/200 such
steps do not schedule five/ten seconds. Sleep/timer/scheduler calls must be counted.
A timed combined wait is a possible different schedule, but once one process is
signaled it returns immediately again. Retiring that wait, preserving other-death
coverage, timing proof queries and handling an empty wait set need an explicit
terminal schedule. Wait-all would miss a single death. None is established by
`2 * steps` arithmetic. A finite early failure is safe but cannot pass N1/N2's
spacing/natural drain obligations by burning all steps immediately.

There is a second independent mismatch: complete per-API monotonic start/end and
wall timestamps require clock issuances (or a documented timestamp source).
One clock query per step cannot timestamp both boundaries of the combined wait
and its own elapsed interval. Cached step time may be labeled approximate, but
cannot silently replace required actual API times. Instrumenting clocks also
needs an explicit nonrecursive accounting/evidence policy: do not recursively
timestamp every timestamp call or silently exclude it. QPC frequency setup, wall
queries, error retrieval and failed waits are not free. These are native source
obligations, not requests to change the frozen evidence schema here.

The cleanup40 cell's advertised maximum is32 action calls
(2 job terminations +2 process terminations +4 queries +4 waits +20 closes)
plus8 error-detail calls. If all32 fail and their errors are retrieved, that
advertised envelope needs64 calls, before clocks, handle counts, worker joins,
attribute disposal or endpoint teardown. Even20 failed closes use40 calls
including error retrieval, leaving no action allowance. This is an arithmetic
counterexample to the **advertised maximum**, not a claim that a particular
minimal native role actually owns20 handles or executes all32 actions. A smaller
exact handle/action inventory might avoid it; no such concrete inventory is frozen.
Stopping after an error can preserve failure, but cannot justify dropping remaining
local-close obligations or calling that finalization complete.

| Role/phase | Issuances and issued bytes still requiring an exhaustive native source schedule |
| --- | --- |
| C ordinary | Runtime startup/loading and shutdown policy; real self/DUP handles; private endpoint creation/inheritance; H/J create/set/query; both helper attribute sizing/init/update/delete/create; thread start/barrier; target creation/identity/path/membership; transfer framing/read/write/error/clock; resume; context, disk reserve, source reads/hashes/copies/manifests; baseline handle/memory measurements; evidence opens/writes/flushes/closes. Suite setup uses row1 cells only. |
| W ordinary | Inherited-slot registration/authentication; receiver-local duplicates/validation; first control iteration and local barrier; worker creation/synchronization; all control/error/time calls; own known-target acquisition and measurements; evidence/transport operations. A generic Python import/thread/JSON/file wrapper cannot certify its implicit Windows calls as zero. |
| S ordinary | Exact process handles/identity discovery, membership reconciliations, per-target wait/member/memory queries, all three harness memory observations or specified survivor replacements,64 sample bound, clocks/errors/transport/persistence. The existing Monitor.sample path can use10 calls for two targets BEFORE harness sampling/discovery:64*10=640 exceeds S's400 sample cell. A genuinely different sampler is required; not an adapter count of six by assertion. N1 only needs20 samples; that does not validate the advertised64-sample maximum. |
| P/T ordinary | Explicit entry/runtime calls, parent-child JOB membership/no-handle inheritance, create/handshake/ready/release/exit259, N4 short-life request, sleep/wait/clocks/error/transport/output. Helpers' requested sleep is not measured lifetime. No shell/console helper outside the five-process limit may be silently introduced. |
| C/W cleanup | Direct J action; all known-target waits and J queries; partial acquisition resolution/source pins; worker joins and exact S/W teardown; H queries; final handle counts; all failures/error retrieval/clocks; each local close; endpoint cancellation/disposal; evidence writes/flush/file close and final inventory. C suite finalization uses row6 cleanup cells even if earlier rows failed, without borrowing skipped entitlements. A blocked worker may consume the sole evidence worker; no extra writer thread is allowed. |
| S/P/T cleanup | Remaining local handle-user quiescence, endpoint/attribute/native storage disposal, error/clock/exit/close and partial evidence within their own cells. A role killed before persistence leaves incomplete rows, never reconstructed successes. |

This table identifies missing accounting, **not** an exhaustive issuance count.
Claiming such a count now would conceal the very stop condition. Counting only
explicit ctypes wrappers excludes runtime/library operations the requirement
includes. Resolving it needs a pinned minimal native runtime/entry path, transitive
call audit and bounded transport/persistence/finalizer design. Counting internal
OS implementation work as new application API calls is not proposed; the missing
boundary is application/runtime/library issuance. No profiler/tracing framework,
native program or general transport framework is built for this decision.

## Storage, layout and six cases

Arithmetic remains8MiB/case and48MiB for six rows plus8MiB suite provenance=56MiB,
within64MiB/case and128MiB aggregate. Failed write request lengths count in full;
no short-write/retry refund. Open/flush/close/error calls count independently.
Bounded rows/arrays, full partial tails, source/binary/runtime provenance and
manifest overhead must fit assigned role bytes; an8MiB source tree does not bound
the installed runtime's provenance or native binary dependencies automatically.
No larger package, row truncation-as-success or extra output root is authorized.

The logical layout fits three harness/two targets, C/W control+one worker and S
one thread. The claimed20 handles/role is not an enumerated native inventory:
creation process/thread, worker, barrier, endpoints, evidence files, H/J, self,
source DUP, peer/S/target copies and runtime handles all require distinct lifetime
and high-water accounting. GetProcessHandleCount needs query rights; wait-only
copies alone cannot measure it. Runtime-created threads/processes/handles cannot
be excluded by naming only application roles. Buffers <=8MiB/role,256 member slots
and serial64KiB attributes do not establish512MiB harness working-set fit.
Target active2/commit128MiB and separate sampled128MiB remain unchanged.

| Historical case | Remaining obligation within the unchanged caps |
| --- | --- |
| N1 |20 complete samples at100ms spacing, no gap>250ms; exact signaled exit259, J empty/active0 and known waits. Two-call zero-time control arithmetic supplies no spacing. |
| N2 | Retain child before parent release, observe child outliving parent, natural4s child drain. Startup/handshake must leave room before5s ordinary boundary; no timing fit demonstrated. |
| N3 | Retain parent/child before2s trigger; terminate J with exact waits and membership/accounting, under both reserve and15s cap. No deferred trigger to hide bootstrap latency. |
| N4 | TotalProcesses2; requested<10ms child life and1s parent exit do not prove measured lifetime or full identity coverage. Missing identity stays unknown. |
| N5 | Sampler blocks without control locks; independent action at2s, observed initiation<=1s and proof<=10s from trigger, also15s cap. Releasing/joining sampler, survivor sampling and blocked writer evidence must be counted. |
| N6 | C terminates only exact retained S; W independently acts on S death; C's own J/known-target copies prove drain. S's final output cannot be required to arrive after its death or fabricated. Survivor inventory/measurement and failed records remain explicit. |

All six remain unallocated and native-unvalidated.15s starts before bootstrap,
10s reserve starts by5s, suite120s, disk reserve1GiB; earliest cap wins. Arithmetic
feasibility proves neither startup-before2s, polling response, memory fit nor
durability. No hard deadline is claimed. There is no justified small file list for
native implementation under this decision; supplying one would bypass this stop.

## Documentation and evidence classification

Primary Microsoft pages checked2026-11-12:

* [Creation attributes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute): JOB_LIST and real inheritable HANDLE_LIST mechanism; not validation of these adapters.
* [DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle): source/target DUP rights, receiver-local result and noninheritance options; no remote-close usage permitted here.
* [WaitForMultipleObjects](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitformultipleobjects): wait-any/timeout semantics and undefined pending-wait close.
* [QPC](https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancecounter): interval counter, not scheduling or automatic wall timestamps.
* [Job limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information) and [process termination](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process): last-job-handle kill flag and local process table teardown; no deadline or evidence promise.
* [TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject) and [handle counts](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesshandlecount): termination/query interfaces, no substitute for the required cleanup conjunction.

The proposed barrier and inventory schedules above are design reasoning.
Eventual successful containment and independent control remain modeled assumptions.
The65 retained fake tests establish symbolic/order/mock properties only. The new
package checks provenance and arithmetic witnesses; it adds no native/fake-runtime
acceptance. No DLL-backed WindowsAPI construction, transport/bindings/helper/
allocator/case-runner implementation, process-control/preflight/socket, local
Java/Minecraft/TD/provider/model execution or save access occurred.

## Verification, preservation and exact next gate

Separate files: this report; `scripts/audit-staged-helper-native-decision.py`;
`docs/evidence/windows-staged-helper-native-decision.json` and `.zip`; one CI audit
step. Audit deterministically packages this decision and hashes its basis, checks
the inherited packages, and reproduces the static counterexamples. Use `--write`
only for this separate package. After final Windows checkout run the audit with
`--check-runtime-root`: all39 frozen inputs and all70 actual retained runtime files
must remain identical. Final-checkout checks and CI are recorded in the handoff.

**Stop. Exact next authorization gate:** explicitly authorize a separately bounded
offline resource-contract redesign decision, accepting that a pinned runtime,
control pacing/timestamp policy, transport/finalization call graph and exact handle
inventory require substantial additional preparation; or explicitly authorize
changed requirements/partitions. Neither option is authorized here. No native
implementation authority follows. Any later implementation scope, exact executable/
context/resource freeze with passing CI and failure-charged native allocation are
separate subsequent gates. Do not repeat exhausted controls for this decision.

Navigation-3 complete root, frozen sources/artifacts, consumed slot, approvals,
ledger and partial evidence remain verbatim: INCOMPLETE, zero remaining. Preserve
all historical failures, PR59 negative contacts, geology-1, continuing-save safety,
production guards, immutable inputs, optional Ulti-World, viewer repairs and
unrelated temp/. PR62 remains draft/unmerged; #9/#11 remain open. Geometry/support/
uncertainty, historical numerical reproducer, joining, fresh validation, paired
startup/cold/warm/full-route performance, versioned adoption/bidirectional rejection/
exact restoration/reopen/snapshot/block/persisted-container gates carry forward.
PR54 remains exhausted; final capture compile-only; historical arrays/indices/ULPs
unknown. Monitoring adds no gameplay. Terrain-aware visual prototype review remains
available now through the retained [panel](evidence/td-story.html) and
[viewer](evidence/td-region-visual.html); further monitoring is not a prerequisite.
