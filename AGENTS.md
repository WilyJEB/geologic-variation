# Geologic Variation project direction

## User-approved development direction (2026-11-07)

Build a distinctive, maintainable, publishable Terrain Diffusion addon whose
geological regions respond coherently to the landscape. Terrain interpretation
is a central desired feature. Continue this original direction; do not default
to abandoning it or reducing the project to the current simple rock replacement
solely to ship sooner. If evidence makes the direction impractical, explain the
specific obstacle and propose a simpler alternative to the user.

Balance uniqueness with a clean release. Use bounded, decision-oriented research
that leads toward a visual prototype and player-visible value. Do not let
diagnostic work expand indefinitely or require scientifically recovering real
geological history from terrain. Favor explicitly finite-support terrain
properties, coherent seeded synthetic geological histories, uncertainty and
abstention over unjustifiable global ridge/basin identities. Verify which useful
layers the pinned Terrain Diffusion API actually provides before deriving them.
Terrain shape alone does not uniquely determine geology.

## Continuity and evidence

Before continuing #11, read `docs/td-observation-history.md`,
`docs/td-axis-numerical-controls.md`, their frozen protocols and portable evidence.
Reconcile current main/GitHub rather than assuming the recorded checkpoint is
still current. PR55 (`a820d63`) is the checkpoint when this guidance was written,
not a permanently fixed base or proof of later completion.

The proposed next slice is offline-first: analyze the retained PR52 request
prefix using a small auditable model of pinned window dependencies, batching and
eviction; compare against retained counters and PR53/54 histories; decide whether
a minimal distinguishing runtime experiment is justified. Do not treat this
proposal as already executed. Keep a short route to a visual terrain-aware
prototype explicit. Change the next slice when current evidence warrants it.

Preserve geology-1 and continuing worlds until a separately validated, versioned
adoption. Keep frozen failures visibly failed; do not retune old diagnostics or
relabel their failures. Previously inspected analytical controls and TD seeds are
development data for revisions. Distinguish reused evidence, newly performed
checks, compile verification and runtime acceptance.

No new TD execution merely to repeat exhausted controls. Before any justified
new experiment, commit and push its protocol and executable collector with
fixed launch caps including failures, request/startup/window/memory/disk/wall-time
caps and complete arrays, sequences, counters, executed sources/artifacts, inputs
and partial-failure retention. PR54's four-launch budget is exhausted. Its runtime
used 4a2fa1c instrumentation; the final capture mixin is compile-verified only.
Historical full arrays do not exist; historical indices/ULPs remain unknown.

Carry forward the reports' future validation, performance and adoption/save-safety
gates. Keep #9/#11 open until their actual acceptance requirements are met.
Preserve strict guards, immutable inputs, optional Ulti-World and unrelated
`temp/`. Palettes, dikes, minerals and integrations remain outside the current
bounded #11 slice unless subsequently authorized; they are not permanent project
exclusions. Never silently migrate continuing geology-1 saves.

For diagnostic slices following this workflow, deliver portable evidence and
appropriate verification; obtain passing CI before merge, then strictly re-export
retained and new evidence after the final Windows checkout. Scale verification to
the actual change: guidance-only edits do not require TD runs or evidence reruns.

## Communication

Explain progress in plain language, including what a player will gain, what is
actually blocked and why the next check matters. Be candid about pace and
remaining uncertainty; neither promise publishability nor call research a
gameplay improvement without evidence. The user values this unique direction
and also wants a good, clean, publishable addon.
