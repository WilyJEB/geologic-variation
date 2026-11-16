# Native harness preparation: bounded stopping point

Offline preparation ONLY. No native validation, attempt allocation, authorization
file, new runtime root, launcher integration or navigation changes. PR62 remains
draft/unmerged. Starting local/remote/PR head was
`3251c04b656d0a0187469e1d1942b7b995c5afd1`; fetched main remains
`513c4ca1e950969453faf52723f7ee68c7d6c329`. Starting CI43276173168 passed.
Untracked viewer repairs and unrelated temp/ remain untouched.

This report supersedes the *future harness design and proposed caps* in
[the previous preparation](windows-process-monitor-preparation.md). That report,
its23 tests, sources and portable evidence remain unchanged historical preparation.
The new sources implement injected control/ownership wiring and mock-inspected
creation/duplication bindings. They do **not** implement native independent-process
bootstrap/transport or the six native case runners. They cannot run a native case.
This is a reviewable partial harness preparation, not an executable native freeze.

## Small ownership design

Three harness processes: controller/verifier, independent watchdog, sampler.
Two benign target processes at most. The controller never samples. Each control
process has its own retained job and wait-only peer/sampler handles. Control polls
only its monotonic deadline, interruption state and these exact retained handles;
it calls retained-job termination directly. No sampler lock/callback/queue or
evidence write precedes termination. The watchdog does not need the optional
parent duplicate to contain the atomically created target.

1. Controller owns a noninheritable, kill-on-last-job-close job, with no breakaway,
   configured limits before target creation. Bootstrap starts the sampler and
   watchdog; neither belongs to the target job. Bootstrap failures charge the case.
2. Watchdog receiver **pulls** job QUERY|TERMINATE (`0xC`), controller SYNCHRONIZE
   (`0x100000`) and sampler SYNCHRONIZE duplicates into its own process. It owns
   each successful duplicate immediately, before any ACK/logging. The controller
   similarly holds watchdog and sampler waits. Source/receiver process handles
   used for duplication require PROCESS_DUP_HANDLE (`0x40`); bootstrap retains
   them from exact creation, never a PID/name lookup. No DUPLICATE_CLOSE_SOURCE,
   DUPLICATE_SAME_ACCESS or inheritable duplicate. Each process closes only its
   own copies, once; a failed close consumes that ownership and invalidates evidence.
3. Only an armed ACK permits target creation. Use STARTUPINFOEX with
   PROC_THREAD_ATTRIBUTE_JOB_LIST (`0x2000D`) and
   EXTENDED_STARTUPINFO_PRESENT|CREATE_SUSPENDED (`0x80004`). Handle inheritance
   is FALSE; job handles never enter targets. Failure has no assignment fallback.
   Preserve attribute storage/job array through CreateProcessW; dispose the
   attribute list afterward. The documented initial size query's expected122 is
   separate from failures; maximum attribute storage64KiB, no resize retry.
4. Acquire returned exact parent/thread handles before logging; query raw identity,
   path and IsProcessInJob. Receiver pulls exact parent QUERY|SYNCHRONIZE|TERMINATE
   (`0x101001`), owns it, then ACKs. Missing/lost ACK means no resume. Ownership
   remains receiver-side after ACK loss: sender never remotely closes the number.
   Creation handles stay controller-owned. THREAD_SUSPEND_RESUME is needed by
   the controller; sampler/verifier process duplicates need QUERY|SYNCHRONIZE.
5. Check creation deadline and watchdog retained-handle liveness again, then resume
   exactly once. No retry. A death after this last check is handled by the surviving
   control role, not asserted impossible. Atomic containment covers controller
   death between creation and parent transfer; pre-create arming removes reliance
   on a create-then-assign interval. Failed metadata/resume/transfer/interrupt enters
   job termination without first waiting for a sink. The frozen Monitor's older
   adopt_suspended/assign method is never used by this proposed harness.

The bindings use documented [job-list creation attributes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
and [DuplicateHandle ownership/rights](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle).
These sources establish API intent, not working native bindings on this machine.
CreationBindings only accepts injected kernel functions; it loads no DLL. Tests
supply Python functions and inspect pointers, flags, structures and rights.

## Failures, independent control and evidence

Controller death: watchdog's exact controller wait fires, including before parent
transfer. Sampler death: both surviving control roles independently observe its
wait. Watchdog death: controller's exact watchdog wait fires. Failed peer wait is
unknown and triggers termination. N6 kills only the retained sampler process,
leaving controller/verifier alive. A deliberately blocked sampler is never a
control dependency. Parent-transfer work must run outside the watchdog control
loop on a separate worker; arm is completed before that loop starts. The two
stable control handles and sampler wait are never replaced/closed while polling.
At finalization join/stop the worker before closing its ownership table; failure
to join is incomplete and stops the suite. Never concurrently close sampler
handles while it may be in a native call. OS teardown of a dead process closes
its own table; surviving roles still must verify the job and their known handles.

Interruption anywhere sets incomplete disposition when persistence works, invokes
retained-job cleanup, and consumes the row. A second interruption does not reset
anything. Termination failure, blocked kernel call, double control-process death,
OS suspension or disk failure can defeat response/persistence limits. No
universally enforceable hard deadline is claimed. API limits are issuance limits;
the clock cannot cancel an issued native call. Polling/elapsed thresholds are
observed acceptance rules, not guarantees. No PowerShell/CIM fallback exists.

Termination success is never cleanup proof. The surviving verifier requires
successful empty membership AND ActiveProcesses=0 AND signaled waits on every
retained process handle, including raced/unaccepted handles, before its deadline.
Control-action errors remain case failures even if subsequent containment is
verified. Observation completeness and cleanup completeness are separate. Query
failure/late completion is unknown, never empty/zero. There is no failed-query
retry. A blocked API/evidence writer leaves its start without an end, hence an
incomplete trace. No close, parent exit or notification substitutes for proof.

[Schema](windows-validation-harness-schema.json) describes proposed JSONL rows.
Use separate controller/watchdog/sampler streams, sequence keys scoped by role,
wall/monotonic times, start/end/error/WinError, exact identity and handle owner,
transfer ID/rights/ACK, readiness, trigger/action times, full membership/accounting,
samples with nullable memory, waits, closes and final incomplete disposition.
DurableRows writes/flushes/fsyncs via injected objects, with sticky failure and
no truncation/repair. Native writers must not be on control paths: action results
may remain only in memory if persistence blocks; missing output invalidates the
case. A finite in-memory control record can be drained later without control
waiting for its consumer. Do not claim crash-proof logging of an API return.
Retain raw truncated tails, output inventory, source/binary/input hashes, exact
argv/context/Windows architecture/build/account/session, structure sizes, native
limits and baseline/final handle counts. Lost/error/missing rows cannot pass the
conservative check_evidence consistency checker. That checker is not a complete
native acceptance evaluator; the future runner must supply authenticated known
handle sets and case-specific coverage rather than trusting the trace to list them.

## Six-case proposed contract: zero slots allocated

Each case, including bootstrap/setup/spawn/transfer/interrupt/cleanup failure,
would charge ONE of SIX fixed rows. No retries/substitutions/transfers. Later
explicit authorization must name rows after a complete native executable freeze
and passing CI. A durable pre-creation consumed ledger would then be required;
none is created here. Stop all later rows on unverified cleanup/ownership/missing
evidence. No ambient process enumeration, PID churn or unrelated target control.

| Row | Later native behavior and required result |
| --- | --- |
| N1 | One target, atomic suspended creation; full handshake before resume.20 complete samples at100ms target spacing, controlled exit259, signaled exact wait then exit259, empty membership/accounting and known waits. Any sample spacing>250ms fails. |
| N2 | Parent creates ONE same-job child sleeping4s; child retained before parent-release handshake. Parent then exits; observe child outliving it and natural drain.4s replaces the old5s sleep to leave startup margin. |
| N3 | Parent+ONE child request30s sleeps; at2s since case start terminate retained job; both exact waits and empty accounting/membership required. Sleep request is not running entitlement. |
| N4 | Parent creates ONE child requesting<10ms life; parent exits after1s. TotalProcesses must show2. Poll-missed identity remains unknown; observed child lifetime is not guaranteed by its sleep request. Final job proof still required. |
| N5 | After parent+child retained, sampler blocks on private event. At2s control deadline initiates retained-job termination without sampler/sink response. Separate control releases sampler afterward. Preserve API times; final waits/accounting required. |
| N6 | Parent+child retained; at2s controller terminates ONLY its retained sampler handle. Watchdog independently sees sampler death and terminates job. Surviving controller/verifier uses own job/known-process duplicates for proof. |

Fixed proposed caps, replacing contradictory older numbers:

* 15s/case from **before bootstrap**, including a10s cleanup reserve beginning no
later than5s; startup/target phase <=5s, N3/N5/N6 action scheduled at2s from case
start. Failure to establish readiness/retention before2s fails those rows; no
rescheduling. Six failure-charged entitlements total90s; suite120s including all
setup/finalization. N5/N6 observed initiation <=1s after trigger and verified drain
<=10s after trigger, also within15s case cap. Earlier applicable bound wins.
* At most5 new live processes total:3 harness+2 targets; no extra supervising
verifier/helper/shell process. Already-running invocation shell is excluded and
never controlled. Controller and watchdog each allow one control thread plus one
transfer/evidence worker; sampler uses one sampling thread. A bootstrap needing
extra persistent processes is outside this contract and must return to review.
* Target job native ACTIVE_PROCESS limit2 and job committed-memory limit128MiB;
sampled target working-set sum128MiB is a **separate** cap, not equivalent to commit.
All3 harness processes sampled working-set sum512MiB. Native harness-process
limits/handle measurements remain implementation gates, not enforced by these mocks.
*64MiB output/case,128MiB suite total including partial failures/source copies,
1GiB free reserve. Stop at the first applicable cap; six rows are not entitled to
384MiB. Writer counts issued bytes; disk reserve/accounting belongs off control
paths. No logging retry when storage is unavailable.
* 4096 native API issuances/case across roles, including bootstrap, transfer,
sampling, waits, termination and closes; maximum3072 before cleanup leaves1024
for cleanup/finalization. This explicitly replaces512, which did not budget
multiple independent control polls. Control interval50ms target; <=300 control
steps per role per15s, at most two zero-time waits/step. At most64 samples/case,
256 membership entries,64KiB attribute storage. No retries after required errors.
Quota must be prepartitioned per role before bootstrap (no shared counter lock on
control path); the missing native runner must prove the full static partition
fits4096. Budget exhaustion triggers cleanup using reserved calls; inability to
finish inside reserve is incomplete, never permission for extra calls/rows.

## Precise obstacle and stopping decision

The remaining bootstrap is consequential, not a missing CLI wrapper. Native
receiver-side pull requires exact source-process DUP_HANDLE rights and a bounded
transport that bootstraps those rights **without publishing recyclable PIDs or
passing receiver-valid numbers as locally owned handles**. Its parent-transfer
worker may block while the watchdog must continue polling. Bootstrap must retain
every partially created control process, handle lost readiness/ACKs and death
before either receiver starts, and enforce native limits/API partitions without
turning evidence writes into a control dependency. The current injected transport
tests these state transitions but does not implement that Windows bootstrap.

Adding an IPC bootstrap, inspected benign helper, six role-specific runners and
crash-safe case allocator here would expand this bounded ownership patch into
additional infrastructure. Under the user's stop-before-expansion instruction,
stop at this explicit boundary. **No exact native command/helper binary freeze
can honestly be issued from these sources.** This report does not certify that
the requested fully wired native harness is complete. Native execution is blocked
on a separately reviewed, bounded bootstrap design/implementation and exact
helper/runner/command/context/resource freeze, then explicit native authorization.
No approval flags or executable authorization template are provided.

Exact commands that ARE supported now (offline only):

```text
C:\Users\digif\AppData\Local\Programs\Python\Python313\python.exe scripts/test-windows-validation-harness.py
C:\Users\digif\AppData\Local\Programs\Python\Python313\python.exe scripts/audit-windows-harness-preparation.py
C:\Users\digif\AppData\Local\Programs\Python\Python313\python.exe scripts/audit-windows-harness-preparation.py --check-runtime-root
```

`--write` on the last audit generates portable **preparation** JSON/ZIP under
docs/evidence only. There is no native entry point, authorization argument or
runtime-root creation. The audit rechecks the previous portable preparation and
all39 frozen navigation inputs; the optional local comparison verifies all70
retained runtime files verbatim against their complete partial archive. CI uses
the portable-only path; the local full-root check runs after final checkout.

New tests use only fake clocks/APIs/transport/process creation. Mock ctypes pointer
writes are not ABI/native proof. Atomic CreateProcessW, job limits, DuplicateHandle
rights, independent scheduling/transport, interruption delivery, receiver worker
join, fsync durability, native handle leaks, helper behavior and all six cases
remain native-unvalidated. CI builds/mocks and portable reproduction cannot pass
navigation's18 rows. Navigation-3 stays consumed/INCOMPLETE with zero remaining.

Local verification:21 new mock tests plus23 previous monitor tests,5 retained
process/evidence tests,2 observation-history tests and2 axis tests pass. Strict
navigation-3 preparation replay passes; runtime replay reports INCOMPLETE and zero
attempts remaining. An initial offline runtime replay omitted its `--runtime`
selector and failed with a preparation-mode KeyError; corrected invocation passes
and preserves all unmet rows. No source/evidence was changed to bypass that error.
The new portable audit reproduces the old preparation ZIP exactly and verifies
all39 frozen inputs and all70 actual runtime-root files. Final checkout re-export
and new-head CI are reported in the handoff, separately from native proof.

Review the terrain-aware concept now using retained [story panel](evidence/td-story.html)
and [region viewer](evidence/td-region-visual.html): finite-support landscape
properties informing seeded synthetic histories, competing interpretations and
explicit unknowns. No client attempt or monitor extension is needed for that
review, and monitoring itself adds no gameplay. PR59 negative contacts, all frozen
failures, geology-1/continuing saves, production guards, immutable inputs,
optional Ulti-World, viewer repairs and unrelated temp remain unchanged. All
[process review gates](td-navigation-process-review.md), observation/axis frozen
protocols and portable evidence remain carried; geometry/uncertainty, historical
numerical reproducer, joining, fresh validation, paired startup/cold/warm/full-route
performance, versioned adoption, bidirectional rejection and exact restoration/
reopen/snapshot/block/persisted-container safety remain open. #9/#11 stay open.
