# Offline bootstrap preparation: stop at pre-readiness containment

2026-11-12. The newly authorized offline lifecycle slice reaches the explicit
stop condition: the proposed three-role design still needs substantial harness
containment work or an explicitly weaker bootstrap-cleanup requirement. No native
implementation, allocator, helper, case runner or execution is supplied. This is
a separately packaged negative preparation result, not a runnable native freeze.

## Reconciled basis

Local HEAD, fetched origin branch and GitHub PR62 head agree at
48b0f7a34e88f19a25c9bc51dd707a2d78de6cb3; main/base remains
513c4ca1e950969453faf52723f7ee68c7d6c329. PR62 is open, draft and unmerged.
Starting-head CI is checked independently in the handoff. Reviewed AGENTS.md,
bootstrap design review, both preparation reports, sources/tests/schema and
portable packages, navigation-3 outcome/process review, observation history and
axis/numerical controls with their carried protocols/evidence. Historical reports
and preparation packages are unchanged; this addendum does not supersede failures.

## Smallest distinguishing fake schedule

The finite role model in `scripts/bootstrap_cleanup_boundary.py` explores the
first successful helper creation with exact creation handles already owned by C.
It permits helper scheduling and C death in either order. Both choices of first
helper (W or S) admit this prefix:

1. C creates the first helper and owns its exact process/thread handles.
2. C dies before the helper executes its first instruction.
3. A live helper remains; no process capable of executing cleanup is available.

The model treats a scheduled helper as a *candidate* cleanup agent, generously;
it does not assume successful self-termination or retained-job proof. It finds
the gap even with that favorable assumption. It models no Windows behavior and
does not prove that Windows cannot support a different design. Unsuspended
creation also does not require child scheduling before the creator dies.
Reversing W/S creation order cannot repair the first-child interval. Starting
both in parallel still has a first successful creation. Readiness, inherited
DUP|SYNC handles, typed transfers, ACKs, exact-process ownership and future
independent polling cannot execute before a helper runs. No target exists in
this prefix, so atomic target JOB_LIST containment is irrelevant to this gap.

C is responsible for partial helpers while alive; after C dies before the first
helper runs, the proposed design has no executable cleanup owner. Assigning that
duty to the unscheduled helper would silently weaken the requirement. Death of
C alone suffices here; this is not the accepted double-control-death limitation.
Nor is this an assertion that every temporarily unscheduled helper is permanently
stuck: later scheduling is possible, but cleanup is uncovered until then and a
suspended helper may never execute its entry check.

An additional persistent supervisor violates the existing three-harness-process
cap. An OS-owned harness containment arrangement might avoid that extra process,
but must address atomic first-helper membership, who holds its job copies,
controller-death behavior, W/S independence, teardown and handle lifetimes. It is
substantial containment infrastructure relative to the current target-only job
ports. This slice stops before designing or implementing it, as requested.

## Finite implementation boundary and remaining obligations

Only the abstract boundary model, five fake tests, this report and deterministic
portable audit are added. No partial replacement ownership API is adopted: doing
so while bootstrap cleanup remains uncovered would misleadingly suggest the
requested coherent model exists. The historical interfaces remain explicitly
partial. The following requested gaps remain open, not silently waived:

* Source C real DUP|SYNC handle and exact W/S creation handles, inherited allowlist
  lifetime, local source/receiver identity and rights; no PID lookup.
* Receiver-local ownership before typed epoch/role/transfer ACK, replay rejection,
  lost-ACK retention and source-token lifetime; local close only.
* Independent C/W polling while transfer, sampler or persistence blocks; survivor
  inventory for every accepted and raced target/helper handle.
* Finalization seal before issuance stops, in-flight acquisition registration,
  worker quiescence before close-once and failure disposition for an unjoined user.
* Fake-tested Wiring/Control/CreationBindings adapters, immutable command/cwd and
  target FALSE/JOB_LIST/suspended creation distinct from harness inheritance.
* Static disjoint per-role ordinary/cleanup issuance quotas totaling <=3072/1024,
  finite record buffers and issued-byte quotas covering bootstrap and finalization
  failures inside 64MiB/case and 128MiB/suite. No partition is certified here.

The model allocates only small Python state objects offline. That is not a native
API/evidence budget demonstration. Native limits, independent scheduling,
inheritance/IPC, ABI/rights, helper shutdown, blocked calls, leak checks, durability
and six case acceptance all remain unvalidated. No hard deadlines are claimed.

The exact next authorization gate is a **separate offline containment decision**:
explicitly authorize reviewing an OS-owned containment arrangement for the three
harness roles within the existing caps, or explicitly accept weaker pre-readiness
cleanup semantics. This result does not authorize either change. Only after that
decision and closure of the listed fake-interface/resource obligations could a
separately authorized native implementation be considered. Exact executable,
command/context/resource freeze and passing CI must precede any separately
failure-charged native allocation. No flags, authorization files, runtime roots
or ledgers are created here.

## Reproduction and preservation

`python scripts/audit-bootstrap-boundary-preparation.py --write` writes only the
separate preparation JSON/ZIP under docs/evidence. Without --write it reruns the
five fake tests, reproduces that package, and strictly reproduces both historical
preparation packages and their 44 fake tests/39 frozen inputs. Add
`--check-runtime-root` on the final Windows checkout to compare all 70 retained
runtime files with the complete partial ZIP. The audit never constructs WindowsAPI,
imports the frozen native helper or executes a process/socket/preflight check.
CI runs the portable path; final-head CI and local checks are reported separately.

Navigation-3's root, frozen sources/artifacts, consumed slot, approvals, ledger and
partial evidence remain verbatim: INCOMPLETE, zero attempts remaining. PR59
negative contacts, frozen failures, geology-1, continuing-save safety, production
guards, immutable inputs, optional Ulti-World, viewer repairs and unrelated temp/
are preserved. #9/#11 stay open. Geometry/support/uncertainty, historical numerical
reproducer, joining, fresh validation, paired startup/cold/warm/full-route
performance and versioned adoption/bidirectional rejection/exact restoration,
reopen/snapshot/block/persisted-container gates carry forward. PR54 remains
exhausted; its final capture mixin is compile-only and missing historical arrays,
indices and ULPs stay unknown. PR62 stays draft and unmerged.

Monitoring adds no player-visible improvement. Terrain-aware prototype discussion
remains available now through the retained [story panel](evidence/td-story.html)
and [region viewer](evidence/td-region-visual.html): finite-support terrain cues,
seeded synthetic histories, competing interpretations and explicit unknowns.
Further monitoring is not a prerequisite for that product review.
