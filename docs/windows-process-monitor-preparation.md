# Standalone Windows monitor: offline preparation only

User-authorized scope, 2026-11-12: implement a separately named monitor and fake
tests; no activation, launcher integration, native helper execution or allocation.
`scripts/windows_process_monitor.py` has no executable entry point and imports no
frozen helper. DLL loading occurs only on explicit `WindowsAPI()` construction;
that constructor was NOT executed against a native DLL. The tests replace it with
Python functions. No new process, socket, installed-profile check, Java, Minecraft,
TD/provider/model call or save opening is part of this work.

Reconciled starting HEAD/local/fetched origin/PR62: `dda7fc4693096bdf317857082bc06e72a7b48fdf`;
main/base `513c4ca1e950969453faf52723f7ee68c7d6c329`. PR62 is open, draft and
unmerged. Reused starting-head CI [43271958791](https://github.com/WilyJEB/geologic-variation/actions/runs/43271958791)
passed. A restricted fetch could not write FETCH_HEAD; the approved fetch succeeded.
Final preparation-head CI is reported in the handoff, separately from native proof.

## Component and evidence semantics

The adapter uses explicit fixed-width Windows ABI structures and pointer-sized
SIZE_T/handles. It binds documented kernel32 APIs: job creation/limits/membership/
accounting/termination, limited-query+synchronize OpenProcess, GetProcessId,
GetProcessTimes, QueryFullProcessImageNameW, IsProcessInJob, zero-time process
waits, GetExitCodeProcess and K32GetProcessMemoryInfo. Modern Windows is the target;
no broad-rights escalation or fallback is supplied. Parent/thread handles must be
transferred from suspended creation with terminate/resume rights. New descendant
handles receive only limited-query+synchronize rights; they are never killed by PID.

Identity keys are `(PID, raw uint64 creation FILETIME)`. The parent records
controller-authored argv separately from observed executable path; child command
and parent linkage remain unknown. Job membership establishes scope, not ancestry.
Before accepting a child, the component opens a handle, queries exact identity,
verifies membership and path, retains the handle, then reconciles the PID list.
An opened PID that now belongs outside the job is never accepted or terminated.
An exited old identity and a newly observed same-PID identity retain separate handles.
If a PID was recycled before its FIRST open into another process in this SAME job,
the new handle describes only that newly observed identity. Equal PID lists do not
prove snapshot identity continuity. No retroactive identity is assigned to the old
enumeration. Short-lived/unseen descendants and full ancestry remain unobserved.

API start records precede calls; end records preserve result/error, WinError where
available, monotonic start/end and wall timestamp. Query errors and partial samples
remain unknown; missing memory never becomes zero. The sum is sampled working set,
not a simultaneous snapshot, guaranteed peak or exhaustive lifetime observation.
A successful sample means its recorded queries succeeded, not that no unseen child
existed. There are no notifications or ETW tracing claims. Bounded list overflow
(256 entries) fails closed without resizing/retry. An observation error stops
inspection. Ordinary cleanup polls cannot repair the failed observation.

Process exit requires a signaled retained-handle wait; only then is the exit code
read. Exit259 is therefore a valid terminal code. Parent exit is insufficient.
Cleanup requires successful empty membership AND ActiveProcesses=0 AND signaled
waits on every opened/transferred process handle, including unaccepted/raced ones,
before the cooperative deadline. Unknown membership, failed waits/termination,
interruption or late completion keeps cleanup incomplete. Success of termination,
handle close or any future notification is never cleanup evidence. The component
does not retry required-query failures. It retains every partial row. A successful
containment result can coexist with `observation_complete=false`.

The controller must call cleanup and finally close; it must not concurrently close
a sampler's handles. Ownership is consumed before each close attempt, so failures
are recorded without a second CloseHandle on a potentially recycled handle value.
Close proceeds even if evidence persistence fails; failed persistence cannot pass
the trace checker. Acquired handles become owned before completion logging.
The supplied sink must durably append starts/ends, partial samples, ownership and
cleanup/close rows. Sink errors are fatal to observation. The component is not a
general durable storage framework; a future harness must provide flushed JSONL,
preserve truncated tails and treat missing end records as incomplete.

`check_trace` rejects missing API pairs, missing/incomplete samples, unknown totals,
missing cleanup, failed accounting/waits and unmatched/failed closes. It checks
mock evidence consistency only; it is not a native validation or navigation replay.

API basis: [job query](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject),
[process times](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes),
[process waits](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject),
[memory](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo),
[job termination](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject).
Documentation specifies semantics, not measured behavior or verified bindings here.

## Minimal watchdog ownership decision

No hard deadline is claimed. `WatchdogControl` is a pure, fake-tested control step
for a FUTURE independent process, not an activated thread/process. It has its own
duplicate retained job, exact parent and controller handles. It polls only its
deadline/controller wait, never calls a sampler method or waits for its lock, pipe,
queue or evidence sink. At deadline, interruption, controller death or wait failure,
it attempts retained-job termination and exact-parent termination independently,
without logging first. Its own handles are closed once. Termination errors stay
unknown. It cannot certify job-empty cleanup, and does not claim to do so.

A future harness must establish watchdog readiness BEFORE target resume. A simple
"create suspended, then duplicate/assign" handoff has a real gap: controller death
before assignment/handle transfer can strand an uncontained suspended process.
Do not call that design enforceable. The smallest proposed resolution is atomic
creation into the already retained job using Windows10+
`PROC_THREAD_ATTRIBUTE_JOB_LIST` with STARTUPINFOEX/EXTENDED_STARTUPINFO_PRESENT
and CREATE_SUSPENDED; no breakaway. Documented
[creation attributes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
provide this mechanism. The job/watchdog ownership handshake precedes creation;
the future controller still captures exact identity and explicitly verifies job
membership before resume. Keep the component's assignment-failure path tested for
low-level callers, but prohibit the non-atomic handoff in any deadline claim.

This atomic creation/duplication/independent-process wiring is NOT implemented in
this bounded component. It belongs to separately reviewed harness preparation,
before native authorization. If it cannot remain a small auditable harness, stop;
do not add supervisors or a tracing framework. Watchdog death while another job
handle remains open cannot rely on kill-on-close. The surviving controller must
detect watchdog-handle signaling independently of the sampler, terminate the job
and invalidate the case. No job handles may be inherited by targets. Both control
processes dying, blocked kernel termination, suspended OS or disk failure defeat
absolute timing/persistence guarantees. Native validation must measure bounded
observed response; it cannot prove a universal hard real-time deadline. No budget
or launch can rely on enforceable hard deadlines before resolving these gates.

## Proposed benign native validation contract — NOT allocated

This is a ready-to-review case contract, not launch permission or an implemented
harness. A separately authorized harness-preparation change must freeze exact
sources, helper binary/Python bytes, Windows build/architecture/account/session,
command arrays, installed runtime and source hashes, paths, schemas and watchdog
wiring, push them and obtain CI before ANY native case. No changes to navigation-3.
No Java/Minecraft/TD/sockets/saves; only a small inspected benign helper in an
exclusive new root. No unrelated PID churn, process scans or name/PID kill fallback.

Proposed finite maximum: SIX cases, one execution per row INCLUDING setup/spawn/
interruption/cleanup failure. No retries, substitutions or budget transfer. This
document allocates ZERO slots; later explicit authorization must allocate the
entire fixed matrix or a named subset without filling skipped slots dynamically.
Each authorized row gets a durable pre-creation consumed ledger; no deletion/reset.
Stop the whole suite on unverified cleanup, ownership gap or missing evidence.

| Case | Exact behavior and expected evidence |
| --- | --- |
| N1 | One benign target created suspended atomically in job; readiness/identity/path/membership before resume; 20 samples at 100ms target spacing; controlled exit259; signaled exact wait then exit259; empty job/accounting; close once. |
| N2 | Parent creates ONE child in same job; child sleeps5s, parent exits immediately after child-ready signal. Retain child before parent release; observe child outliving parent, then natural drain and exact waits. |
| N3 | Parent and ONE child sleep30s. At2s request job termination. Require both retained-handle waits, membership empty and accounting active0. Termination return alone fails. |
| N4 | Parent emits ONE short-lived child (<10ms), then exits after1s. Accounting TotalProcesses must show both; identity coverage explicitly incomplete if polling misses child. No exhaustive descendant claim; cleanup still requires job-empty evidence. |
| N5 | After parent+ONE child identities are retained, sampler deliberately blocks on a private event without holding any control lock. At2s watchdog must initiate retained-job cleanup without sampler response; separately release sampler after cleanup control, retain actual API times and final accounting/waits. |
| N6 | Parent+ONE child retained; at2s terminate ONLY the harness's retained collector process handle from its designated controller to simulate abrupt collector death. Independent watchdog responds; surviving verifier holds separate job/known-handle duplicates and proves accounting/waits. Never infer success from collector death. |

Per case proposed maxima:15s total including10s cleanup reserve; target running
phase <=5s (N3's30s sleep is deliberately ended early), 2 target processes,
one sampler, one watchdog, one supervising verifier (<=5 harness processes, plus
the already-running invocation shell, which is never controlled). Each fresh
case consumes15s regardless of outcome; aggregate90s target-case entitlement.
Outer suite wall cap120s including setup/reporting; disk64MiB/case,128MiB aggregate,
free reserve1GiB, sampled target-job working set128MiB, all harness processes
sampled sum512MiB. Exact native job memory/active-process limits must also be
configured in the future harness, separately from sampled observations. At most
256 membership slots,512 API calls/case,64 samples/case, no automatic retries.
Caps apply to startup failures too. Query calls may block: the declared wall cap
is a stop/invalidity rule until the independent watchdog is implemented and
validated, never an assumed enforcement guarantee. Exceeding any cap fails the row.

Interrupt anywhere: set durable interrupted disposition when possible; control
process terminates only retained job/exact harness handles, performs required
accounting/waits within the remaining reserve, preserves raw/truncated output and
closes each owner copy once. Ctrl-C delivered during a blocked sampler cannot be
the only cleanup route. A second interrupt does not erase the ledger. Failed
cleanup blocks all subsequent cases and requires a user decision, not a relaunch.

Evidence: pre-creation ledger/authorization, complete source/binary/input manifests,
exact argv, context, monotonic/wall API start/end/error records, every sample and
raw identity, membership reconciliations, accounting totals, signaled waits/exit
codes, ownership/duplicate rights and close results, watchdog readiness/deadline/
trigger/action times, target handshake events, per-process handles/count baseline
and final count, native structure sizes/rights, output inventory and full partial
failure retention. Store independently flushed watchdog/controller JSONL without
sampler locks; lost disk output is incomplete, not reconstructed observation.
Export complete roots portably; corruption tests must reject lost/error/partial
rows and false empty-job claims. No instantaneous memory peak guarantee.

Acceptance requires every authorized applicable row within all limits, no unexplained
owned-handle increase after finalization, exact atomic containment/ownership proof,
every required query successful, required identity/wait evidence and empty-job
accounting. Report N4's short-lived limitation explicitly. N5/N6 must show cleanup
initiation <=1s after trigger and final empty accounting/known waits <=10s after
trigger, as observed acceptance thresholds, not universal guarantees. N1 must have
all20 complete samples; record each API latency and spacing; any spacing >250ms
fails its declared context's100ms sampling target. Other races/access failures,
assignment/resume failure, enumeration overflow and impossible PID timing remain
fake fault-injection tests, never unsafe native system experiments. Native success
would validate only this pinned harness/context; navigation still requires a new
explicit user decision and its unchanged18-row acceptance.

## Verification and stopping point

New tests are deterministic fake-API/state-machine tests with fake clocks. They
cover raw identity, membership, child outliving parent, PID reuse, enumeration/open
races, denied/missing queries, overflow, exit259, assignment/resume failures,
partial samples, failed waits/termination/accounting, late deadlines, interruption,
watchdog independence, sink failure, ownership and trace corruption. Mock ctypes
functions inspect structure sizes/rights and pointer writes without loading DLLs.
The portable preparation audit packages exact new sources/report and test counts;
its strict check re-runs the mock suite and reproduces identical archive bytes.
Existing retained tests/replays remain reused or newly checked as explicitly
reported, never native acceptance. No local Java build is needed for Python-only
preparation; CI's usual builds are compile/offline checks.

Preparation verification on Windows:22 new mock tests,5 retained process/evidence
tests,2 observation-history tests and2 axis/identical-support tests passed.
Strict navigation-3 preparation replay passed; runtime replay remained INCOMPLETE
with zero remaining attempts. All39 frozen input bytes matched their manifest and
both portable archives; all70 files of the actual retained runtime root matched
the complete partial ZIP verbatim. The read-only audit performs that full-root
comparison only with `--check-runtime-root`; CI has no historical runtime root.
`git diff --check` passed. These are newly performed offline checks of reused
evidence. No native validation, allocation or navigation acceptance occurred.

Stop here when this preparation is reviewable. The concrete next design decision
is whether reliable bounded observation can support a later movement/readability
check of the retained terrain-aware display. Monitoring itself adds no gameplay.
Review the player-facing concept using the retained viewer/panel now: finite-support
terrain properties inform coherent seeded synthetic histories, with unknown gaps
and competing interpretations. No further monitor framework or client attempt is
required merely to discuss that visual prototype. PR59 negative contacts remain
negative; no geological plausibility is inferred from shape or navigation.

All [carried review gates](td-navigation-process-review.md), navigation/observation/
axis protocols and portable evidence remain in force: geometry/support/uncertainty,
historical numerical reproducer, joining, separately frozen fresh validation,
paired startup/cold/warm/full-route performance, versioned new-world adoption,
bidirectional save rejection, exact restoration/reopen and snapshot/block/persisted
container safety. Geology-1 and continuing saves never migrate silently. Preserve
all frozen failures, strict production guards, immutable inputs, optional Ulti-World,
viewer repairs and unrelated temp/. PR54 remains exhausted and final capture mixin
compile-only; historical arrays/indices/ULPs remain unknown. #9/#11 stay open.
Navigation-3 retains its sole consumed slot, verbatim root/ledger/approvals/partial
evidence and18 unmet rows. PR62 stays draft and unmerged.
