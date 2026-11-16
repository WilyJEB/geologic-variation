# Offline containment decision: staged helper-job ownership

2026-11-12. Decision **1**: a minimal candidate merits a separately authorized
offline interface-preparation slice. This is a conditional design decision, not
an adopted interface, runnable native freeze, native acceptance or timing proof.
Only this report, a finite abstract handle graph, eight tests and a separate
portable package are added. No native construction/execution or allocation.

## Reconciled basis

Local HEAD, fetched origin branch and GitHub PR62 initially agree at
6d972703223fe20cf81d181b5322550f11a4aac5. Main/base remains
513c4ca1e950969453faf52723f7ee68c7d6c329. PR62 is open/draft/unmerged;
starting PR CI43286678939 and push CI43286665355 passed (reused build/offline
evidence). Fetch initially failed writing restricted FETCH_HEAD; approved fetch
succeeded. Final commit/CI and final Windows reproduction are reported separately.

Read AGENTS.md, boundary preparation/model/tests/JSON/ZIP, bootstrap design
review, both historical monitor/harness preparation reports and portable inputs,
navigation-3 outcome/protocol/process review, observation-history and axis
controls/protocol/evidence chain. Earlier negative decisions remain valid for
their designs. This review adds an alternative; it does not repair old results.

## Documentation basis and limits

Microsoft documents job association at process creation through
[JOB_LIST](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute),
available from Windows10/Server2016. This supports requesting membership as part
of creation rather than relying on a later assignment. Actual atomic failure
behavior, ABI and ambient-job compatibility remain native validation obligations.

[CreateJobObjectW](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw)
documents unnamed/noninheritable creation and last-handle behavior.
[KILL_ON_JOB_CLOSE](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)
acts on the last job handle. Membership is not a local job-handle copy.
[Process termination](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process)
closes that process's handles; objects referenced elsewhere remain valid.
These rules support the graph reasoning below, without an elapsed-time guarantee.

[Job objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
document default descendant association and no removal of existing membership.
[TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject)
terminates job members; helpers cannot postpone it with an entry-point check.
No helper scheduling or readiness is assumed in the first-child failure prefix.
Documentation does not prove polling, successful calls, empty-job evidence,
quiescence, durable records or this machine's compatibility.

## Finite alternatives

C is controller/verifier, W independent watchdog, S sampler, P/T targets.
J is the existing target job; H is a separate helper job. Each proposed job is
unnamed, non-breakaway and configured before member creation. C creates all
processes directly. No helper spawns another process. Exact process/thread
creation handles belong to C immediately; process-handle ownership does not
itself terminate a process. Auxiliary wait/duplication/IPC handles are local
copies as in the historical review, not additional job owners.

| Alternative | Membership and job-handle owners through teardown | First successful helper, then immediate C death | Independence and cost / disposition |
| --- | --- | --- | --- |
| A: create then assign H | Before creation C:H,J; first helper initially outside H; later W/S:H members, C:H, C/W:J after arming; C drains helpers then closes H | No atomic membership; first helper survives unscheduled outside H | Same three roles but fails before assignment; readiness and reversed order cannot help. Reject. |
| B: atomic H with early shared copy | Before creation C:H,J; first helper atomically in H and inherits H (or receives it before independent control); later W/S in H; C and receiving helper own H; C/W own J | C closes only C copies; unscheduled helper's H copy prevents last-close termination | No supervisor, but cleanup depends on unscheduled helper. A duplicate is just as fatal as inheritance. S's copy can survive even W death. Reject. |
| C: atomic H, C sole owner forever | Before creation C:H,J; W/S atomically in H, neither owns H; after arming C/W:J; C remains sole H owner through helper drain and final close | Last H close terminates first helper without entry execution | Closes first gap, but C death kills W even after readiness. J can drain by eventual last close after W termination, provided targets/S hold no J copies. That cascade is not independent W cleanup of targets on C death. Reject for the requested independence. |
| D: atomic H, staged W copy | C sole H until W independent control established; W/S atomically in H; then C/W:H,J, S owns neither job; targets only J and own neither job; C outside H/J. Detailed lifecycle below | Before W copy exists, C's last close terminates first helper; no target exists. After W copy exists W is already independently armed | Same three roles and existing thread allowances. Adds one job and one gated W copy; no external supervisor, nested job cycle or new thread. Conditional candidate. |
| E: external supervisor | Fourth process owns H containing C/W/S, keeps H before first helper; C/W:J; supervisor drains H then closes | Supervisor or OS last-close can cover first helper if its own bootstrap is already solved | Needs fourth harness process or a pre-existing trusted service and its lifecycle/security contract. Revised cap/substantial infrastructure; reject. |

Using J itself for W/S would put target termination on the watchdog's own
containment and mix its existing active2/commit128MiB target limits with harness
roles. Including C too would remove the surviving verifier. Mutual nested jobs
do not supply a small independent design. No such change is adopted.

## Candidate D: exact phases and local owners

1. Before first creation: C owns sole H handle (configure kill-on-last-close,
   no breakaway) and sole J handle with unchanged target limits. C is in neither
   proposed job. H is excluded from every inheritance allowlist. An ambient job
   on C may constrain this arrangement: fail closed, no breakaway fallback.
2. First creation may be W or S: JOB_LIST contains H; exact process/thread
   handles go to C. The allowed real C DUP|SYNC and private endpoint handles
   may enter the helper, never H or J. Creation/attribute failures stop bootstrap.
   If C dies immediately, OS closure of C's sole H handle terminates the helper,
   even suspended or before any instruction. Closing process/thread handles alone
   would not do this. Failure before successful creation leaves no new member.
3. Both helpers created: H members W/S; C still sole H owner. C owns their exact
   creation handles. S may own C wait and query/wait process copies but no job
   handles. W acquires retained J QUERY|TERMINATE, C/S waits, and required exact
   inventory. Partial J transfer/lost ACK does not create a target. C death still
   closes last H, terminating W/S; W's J copy closes only when W terminates.
4. Establish W's independent control loop **before any H duplication is issued**.
   It must already poll C/S/deadline/interruption, terminate retained J without
   transfer/sampler/sink dependencies, and retain inventory through finalization.
   Worker blocking must not stop this loop. Readiness here is a future enforced
   local invariant, not an ACK alone. Before H copy: C death still kills helpers.
   After H copy: C death cannot last-close H; already-armed W handles cleanup.
   The exact boundary must include successful acquisition before ACK/logging.
5. W receives one noninheritable H copy with QUERY|TERMINATE (no assignment or
   limit mutation). C keeps its H copy. Lost H ACK means no P and failure cleanup;
   it does not reclaim W's local copy. No S/target/other-process H copy is allowed.
   Only confirmed H acquisition plus unchanged control readiness permits P.
   C creates P suspended atomically in J, inheritance FALSE. P's child T inherits
   J membership, no job handles. H and J are separate, not nested in each other.
6. Running: C/W independently retain J and exact peer/S waits; C retains H and
   W/S creation handles. C blocks: W can terminate J directly with C still holding
   J/H. S blocks/dies: W can terminate J directly; C has the symmetric route.
   W dies: C's H/J copies remain; C must explicitly terminate J, then drain S/H.
   W blocks: C has the same retained-J route, followed by exact helper stop/waits
   or retained-H termination after target proof; H includes W/S, never C. During
   bootstrap C is responsible for every partial helper while alive; no P exists.
   No last-close claim applies while C owns a copy. Both controls dead: eventual
   last H/J closure supplies containment under the graph assumptions; observation,
   timing and persistence are incomplete, never an absolute response guarantee.
7. Finalization while C alive: seal acquisition/issuance, keep independent control
   armed through target drain, prove J empty AND active0 AND all known target
   waits signaled, quiesce users before local closes. S stops or C stops its exact
   handle. W relinquishes H/J only after target cleanup/quiescence, then exits;
   C retains H until exact helper waits, H membership/accounting and own users are
   resolved, closes its local copies once. Unjoined workers/failed queries remain
   incomplete and stop the suite. No live handle is closed under a wait/user.
   H termination can stop a blocked helper but does not turn its unjoined users
   or missing records into successful finalization.
8. Finalization after C death with W owning H: W first terminates/verifies J using
   its own job/known-target handles; it stops/waits exact S, quiesces workers and
   closes J locally. It must not terminate H first (that kills itself). Closing
   its last H copy can terminate W itself; alternatively W's termination closes
   that copy. No claim of a post-self-close row or verified own exit is possible.
   Missing final self-evidence is incomplete, not fabricated. C death before W
   owns H leaves no surviving verifier; OS containment is still covered, not
   measured cleanup proof. This does not weaken any case acceptance requirement.

W holds a handle to a job containing W after readiness. This is a deliberate
ownership reference back to its own containment, **not** a cyclic nested-job
hierarchy. It defeats last-close on C death by design in that phase; independence
then relies on W's already-established control, never on a future unscheduled
entry check. A requirement for OS-only cleanup even after both independent loops
block would exceed this candidate and the existing design. No such new guarantee
is claimed. No disable/re-enable limit, removal from H or remote close is used.

## Fake evidence, resource boundary and native obligations

The finite model computes handle-closure/kill fixed points for two first-helper
orders and four staged phases. Its eight tests distinguish assignment gaps,
early/shared-copy leaks, sole-C shutdown, pre-ACK ownership, W-death responsibility
and target/S-copy counterexamples. It models successful eventual termination,
not Windows calls, independent scheduling, blocked APIs or time. The W action
is an explicitly assumed action, not a tested controller implementation.

Candidate D requires one additional job and gated copy with acquisition/failure
records. It needs no fourth process or extra thread beyond the existing C/W
control+worker and S sampling thread allowances. The staged transition fits the
existing bootstrap concept but is not implemented by current interfaces. It
does not close their typed receiver-local transfer, lost/replayed ACK, seal,
worker-quiescence, immutable command/cwd adapter or survivor-inventory obligations.

All caps remain unchanged: three harness/two targets, 15s/case including cleanup
reserve10s from no later than5s, suite120s, target active2/commit128MiB and separate
sampled working-set128MiB, harness sampled512MiB, disk64MiB/case/128MiB aggregate,
free1GiB, 4096 issued calls partitioned3072/1024, 64 samples/256 member slots/
64KiB attributes. No quota partition or timing fit is certified. H setup, attribute
handling, duplicate/queries/waits/closes and failure paths must fit the same
budgets in the next offline review; inability to fit returns to decision2 rather
than raising caps. H must not inherit J's target limits over W/S accidentally.

Native obligations remain: successful JOB_LIST semantics in the pinned context,
ambient hierarchy/rights/ABI/allowlist acceptance, local copy inventory, independent
scheduling under blocked transfer/sampler/persistence, exact known process coverage,
helper shutdown, leak/limit measurement, bounded observed thresholds and complete
six-case evidence. Documentation and fake tests satisfy none of those executions.

## Exact next authorization gate and preservation

Stop here. Next gate: explicitly authorize **one offline interface-preparation
slice for candidate D's staged helper-job ownership**, within unchanged caps,
covering pre-copy independent-control readiness, receiver-local acquisition before
ACK, lost/replayed ACK and death schedules, survivor inventories, sealed
finalization/quiescence and static per-role ordinary/cleanup call and byte
partitions. No native bindings, transport implementation, helpers, allocators or
case runners follow from this decision. A failed bounded preparation must stop.
Native implementation, exact executable/context/resource freeze with passing CI,
and explicit failure-charged native allocation remain separate later gates.

Reproduce with `python scripts/audit-bootstrap-containment-review.py` (add
`--write` only to package this new review; add `--check-runtime-root` for final
Windows preservation). Strictly reproduces boundary and both historical packages,
49 historical fake tests/39 frozen inputs; verifies all70 actual runtime-root files
when requested. CI uses only the portable path. New package records exact source
hashes, base/main, documentation URLs and fake outcomes. No runtime root/ledger,
approval flag or authorization file is created.

Navigation-3 root, frozen sources/artifacts, consumed slot, approvals, ledger and
partial evidence remain verbatim: INCOMPLETE, zero attempts. Preserve historical
failures, PR59 negative contacts, geology-1, continuing-save safety, production
guards, immutable inputs, optional Ulti-World, viewer repairs and unrelated temp/.
#9/#11 remain open. Carried geometry/support/uncertainty, historical numerical
reproducer, joining, fresh validation, paired startup/cold/warm/full-route
performance and versioned adoption/bidirectional rejection/exact restoration,
reopen/snapshot/block/persisted-container gates remain. PR54 remains exhausted,
final capture mixin compile-only; missing historical arrays/indices/ULPs unknown.
PR62 stays draft/unmerged. No local native/process-control/preflight/socket,
Java/Minecraft/TD/provider/model execution or save access occurred.

Monitoring adds no player-visible improvement. Review the terrain-aware prototype
now through the retained [story panel](evidence/td-story.html) and
[region viewer](evidence/td-region-visual.html). Finite-support landscape cues,
seeded synthetic histories, competing interpretations and visible unknowns can
be discussed without further monitoring work or another launch.
