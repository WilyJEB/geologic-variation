# Navigation-3 offline process-monitor review

Decision: stop further live navigation attempts now. Review the small future
contract below before deciding whether to authorize preparation. This report
allocates no budget and authorizes no implementation, native probe, preflight,
socket check, save opening or client execution. Navigation-3 remains exhausted;
all 18 live checklist rows remain unverified. PR62 stays draft and unmerged.

## Evidence and reconciliation

On 2026-11-12, fetched main is `513c4ca1e950969453faf52723f7ee68c7d6c329`.
Local HEAD, remote branch and GitHub PR62 head agree at outcome
`eb89437c18891efdc81ee3fa3409de27ea95fe61` before this documentation change;
PR62 is open/draft/unmerged. Its build/offline CI
[43269920057](https://github.com/WilyJEB/geologic-variation/actions/runs/43269920057)
passed. This is reused CI evidence. Frozen preparation remains
`951fcda92470244475f6164f11520f20b53834a4`; actual execution was at `435de09`.

Primary evidence: [outcome](td-navigation-3-outcome.md),
[complete partial runtime ZIP](evidence/td-navigation-3-runtime.zip),
[computed summary](evidence/td-navigation-3-runtime.json),
[protocol](td-navigation-3-protocol.md), [manifest](td-navigation-3-hashes.json),
[schema](td-navigation-3-schema.json), executed `scripts/navigation-process.py`
and `scripts/launch-navigation-3.py` inside that ZIP. Archive SHA256 remains
`52319ac3ab554e9d183b004792cc1d5b7a0328f7a1666ab8a50651a033f465a5`.
Historical approvals and literal-argv rejection remain verbatim in their original
records. No historical document, frozen executable or evidence is amended here.

The following are retained wall-clock Unix seconds, not newly measured timings.
Process-record timestamps are written AFTER successful identity queries; they
do not record query start/end separately. CreationDate is CIM's serialized value.

| Retained event/member | Observed value |
| --- | --- |
| `ledger.json` allocation | 1794504371.1404812; one slot consumed, zero remaining |
| `spawn-details.json` | suspended creation recorded 1794504373.0396256; PID27824, assigned=true, resumed=true |
| `processes.jsonl` suspended parent | 1794504373.8763137; PID27824, parent23168, creation `/Date(1794504373030)/` |
| monitoring iteration 1 | 1794504374.1624086; job PIDs [27824]; working set39,731,200 bytes |
| monitoring iteration 2 | 1794504375.636034; job PIDs [27824,9140]; total179,404,800 bytes |
| monitoring iteration 3 | 1794504376.2463932; same PIDs; total305,094,656 bytes |
| observed descendant identity | PID9140, parent27824, creation `/Date(1794504373882)/`; retained command identifies conhost |
| next iteration | identity query timed out; no completed process/monitor row |
| `cleanup.json` | 1794504378.416157; active_before [27824,9140], forced=true, parent exit1, remaining job PIDs [], identity query [], both known identities absent |
| final ledger | finalized=true; no finalization errors; resource wall9.335783549s, output17,840,560 bytes; immutable inputs unchanged |

Exactly which query: the fourth monitoring iteration's `job.identities(pids)`,
following `job.pids()`, called `subprocess.run` with timeout=1 and argv:

```text
powershell.exe -NoProfile -Command
$ids=@(27824,9140); Get-CimInstance Win32_Process | Where-Object { $ids -contains $_.ProcessId } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine,WorkingSetSize | ConvertTo-Json -Compress
```

The script is ONE argv element after `-Command`. This is the fifth nonempty
identity invocation overall: one suspended-parent query and three successful
monitor queries preceded it. Cleanup subsequently queried the known PIDs
successfully. It is not the suspended identity, job-PID enumeration, preflight,
or post-termination query that timed out. Source control flow and the retained
exception establish that distinction; there is no new process experiment.

Before the timeout, Java was resumed, both exact identities/commands were
retained, and three resource samples existed (wall3.026/4.499/5.115s).
All samples had has_position=false. No first position, human input, screenshot,
route, world/save creation or normal server shutdown evidence exists.
Cleanup provides actual partial containment/termination evidence for these two
identities, not complete navigation acceptance or an exhaustive descendant trace.

Unknown: exact failed-query start time, partial stdout/stderr, CIM/provider state,
duration of each subprocess phase, instantaneous memory peak and any unseen
short-lived descendants. The ledger retains repr(TimeoutExpired), not its output
fields or a phase trace. Startup, CIM enumeration, serialization, scheduling and
load are hypotheses, not measured causes. No Windows, Java or geology
incompatibility follows. Structural exclusion supports zero TD execution; zeros
in monitor are not measured provider/model counters.

## Cost and reliability of the frozen design

Every nonempty sample starts a new PowerShell interpreter, enumerates all
Win32_Process records, filters locally and serializes identity, command and memory.
That couples a nominal one-second resource watchdog to interpreter/CIM latency
and unrelated system process population. Three successful process-row spacings
include1.474s and0.610s; these are completion spacings, not query durations.
The source sleeps only the remainder of one second from iteration start.
Neither instantaneous peaks nor guaranteed one-second detection are established.
No CPU-cost distribution or failure probability can be estimated from this run.

The parent HANDLE is already retained for exit-code polling, but its creation
identity still uses CIM; children have no retained handles. Membership enumeration
then PID-based lookup races with exit/reuse. Missing rows fail closed, which is
safe for acceptance but can end a useful diagnostic on transient observation
failure. CreationDate comparisons help distinguish reuse only after successful
lookup. Full command lines are expensive metadata, not a safe kill target.
The same subprocess dependency is used after termination; another timeout there
would leave cleanup evidence incomplete even if the job had drained.

The one-second subprocess timeout is not a hard end-to-end deadline for process
creation plus termination/wait and the whole monitoring iteration. The helper's
cleanup15s loop also does not bound all subsequent CIM/finalization work. In this
run final wall stayed well below1200s; no general timing guarantee follows.
No timeout increase or retry is proposed for navigation-3.

## Proposed future contract — review only

Scope is one small replacement monitoring component in a separately named future
diagnostic. Keep the retained renderer, records, route, immutable inputs, guards
and all old artifacts unchanged. Do not implement or refreeze navigation-3.
Preparation, benign native validation and any game launch require separate
explicit authorization; this proposal sets no new attempt count or budget.

1. Retain the exact parent process HANDLE returned by suspended creation. Read
   PID, raw64-bit creation FILETIME via GetProcessTimes and executable path before
   resume. Retain launched argv as controller-authored metadata, not a claim of
   independently observed runtime command text. Assign a non-breakaway,
   kill-on-close job before resume; failure terminates/waits on that exact
   suspended handle. Never fall back to PID-wide or name-wide termination.
2. Use direct documented job queries for membership, and OpenProcess with only
   required query/synchronize/memory rights for new members. Before accepting a
   child, query creation FILETIME and IsProcessInJob on the opened handle; retain
   that handle through finalization. Reconcile membership again to expose races.
   PID plus raw creation identity is the record key; a reused PID is a different
   process. Never act on an unverified replacement. Parent-PID/path metadata
   cannot establish current membership. Missing parent linkage stays unknown;
   job membership establishes scope without claiming a complete ancestry graph.
3. Poll exit with WaitForSingleObject on retained process handles (distinguish
   signaled/timeout/WAIT_FAILED); read exit code only with explicit wait evidence,
   avoiding STILL_ACTIVE/exit259 ambiguity. GetProcessMemoryInfo supplies sampled
   working set; check required access rights and structure sizes explicitly.
   Commands for children may be unavailable: retain path/creation/membership as
   identity and label command unknown. Revising command-evidence requirements
   requires explicit review in that future contract, never retroactive acceptance.
4. Log each query's monotonic start/end, wall timestamp, API/result/error and
   completeness. Access denied, vanished-before-open, inconsistent membership,
   buffer overflow, wait failure or missing memory is UNKNOWN/incomplete, never
   absent or zero. Stop inspection on required-query failure and enter bounded
   job-scoped cleanup; no automatic retries/relaunches. Ordinary reconciliation
   polls are recorded samples, not a retry that erases a failed observation.
5. Terminate only the retained job on failure; retain it while waiting on every
   known process handle and querying job membership AND active-process accounting.
   Require successful empty membership, ActiveProcesses=0 and signaled known
   handles with timestamps/errors preserved. Parent exit alone, successful
   TerminateJobObject, closing handles, or an exit notification is insufficient.
   An unobserved short-lived member prevents an exhaustive identity claim;
   job-empty evidence is separate from per-identity evidence. Query failure or
   wait deadline leaves cleanup unverified and blocks further execution. Do not
   reopen PIDs to replace retained-handle exit evidence. Close owned handles once
   after recording results; record close failures separately.
6. Keep the hot path free of shell/CIM subprocesses. Optional job completion-port
   events could accelerate discovery, but are outside the minimal implementation:
   ordinary notifications are not guaranteed and contain recyclable PIDs. Polling
   plus retained handles still cannot reconstruct every short-lived process.
   Do not build an ETW/process-tracing framework to complete this navigation gate.

These are design requirements, not a reliability claim. Direct APIs remove the
per-sample shell/provider dependency; they still have access, race and scheduling
failures. A thread deadline cannot cancel an arbitrary blocked native call.
Before native validation, review a bounded independent watchdog/ownership plan
that can terminate the same job without depending on the sampler returning;
otherwise do not claim a hard wall limit. Freeze its resource caps, ownership,
interrupt/collector-death behavior and partial-failure persistence first.

API basis: [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes),
[process handles](https://learn.microsoft.com/en-us/windows/win32/procthread/process-handles-and-identifiers),
[job queries](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject)
and [completion-port caveats](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port).
See also [process waits](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)
and [memory queries](https://learn.microsoft.com/en-us/windows/win32/psapi/process-memory-usage-information).
These document API semantics; they do not validate a proposed binding on this PC.

## Verification and decisions still required

New offline tests in `scripts/test-navigation-process-offline.py` extract only the
frozen identities method's AST and inject a mock subprocess. They verify exact
argv/timeout, no retry, empty-PID bypass, JSON shapes, malformed output and query
errors; retained archive/hash/sequence checks verify the report's evidence chain.
No native helper import, OS process query or subprocess execution occurs in them.
All five new tests passed locally; `git diff --check` passed. The CI workflow now
runs this offline suite alongside its existing build/offline checks. No local
Java build or evidence re-export is needed for this report-only proposal and
mocked regression addition. Final-head CI status is reported in the handoff.
Initial CI [43271299889](https://github.com/WilyJEB/geologic-variation/actions/runs/43271299889)
failed only the new test's assumption that two untracked viewer repairs exist in
a clean checkout. The corrected test verifies their manifest hashes and exact
preparation/runtime archive equality, plus local equality when present. Tracked
frozen inputs still require local equality. No viewer repair was added or changed.
A separate mock test now exercises the clean-checkout absence of both repairs.
They do not test the proposed replacement. Existing FakeJob tests in
`test-navigation-3.py` exercise orchestration/cleanup outcomes but bypass the real
native helper and did not establish its latency or bindings. Do not rerun its
absent-runtime-root preparation assertion against the consumed real root.

Before approving a future implementation, require fake-API/state-machine tests
for handle ownership and close-once behavior; assignment/resume failure; exit259;
child outliving parent; exit between enumeration/open; PID reuse before open;
membership mismatch; missing/denied creation/path/memory queries; list overflow;
partial samples; failed waits/termination/job queries; job-empty with unsignaled
known handle; parent gone with child present; short-lived unseen child; deadline
and collector interruption; durable incomplete evidence. Use deterministic fake
clocks and handles, assert no unrelated PID is acted on, and corrupt portable
evidence to ensure missing samples/errors cannot replay as acceptance.

Separate native-runtime gate, if authorized: one bounded benign-process harness,
with no Java/Minecraft/TD/sockets/saves, to exercise actual ctypes layouts/rights,
suspended assignment, child inheritance/outliving parent, retained-handle waits,
forced cleanup and job accounting, interrupt/collector-death containment and
handle leaks. Freeze a finite failure-charged case matrix and time/memory/disk/
process caps before execution; compare query latency to the sampling target under
that declared context. Do not deliberately churn unrelated system PIDs. Fault
injection remains necessary for races that cannot be induced safely/reliably.
Native success would be bounded evidence, not universal Windows reliability.

Only after that gate and a new user decision could one no-TD navigation attempt
be considered. Its unchanged18-row acceptance would answer whether movement,
regional size/contacts/shared histories, full panel tokens and both configurations
are readable and coherent in-world. It would not improve geology or resolve
PR59's negative contacts. Given repeated exhausted display attempts, another
client slot is not justified yet. Declining it leaves PR62 incomplete/draft;
use retained panel/viewer evidence for bounded design review and move the next
authorized prototype decision toward finite-support terrain properties, seeded
synthetic histories and explicit unknowns. Do not require indefinite monitoring
research before reviewing that player-facing concept. Revisit navigation only
when its missing movement evidence is needed for a concrete design decision.

All carried [navigation gates](td-navigation.md), [observation history](td-observation-history.md)
and [axis/numerical gates](td-axis-numerical-controls.md) remain: geometry/support/
uncertainty, historical numerical reproducer, multi-field joining, separately
frozen fresh validation and paired startup/cold/warm/full-route performance,
versioned new-world adoption, bidirectional save rejection and exact restoration/
reopen/snapshot/block/persisted-container safety. Preserve PR59 negative contacts,
all frozen failures, geology-1, continuing saves, strict production guards,
immutable inputs, optional Ulti-World, viewer repairs and unrelated temp/. PR54's
four launches remain exhausted; final capture mixin is compile-only; historical
arrays/indices/ULPs remain unknown. #9/#11 stay open. No offline test or CI result
establishes runtime acceptance or player-visible gameplay improvement.
