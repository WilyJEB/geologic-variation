# Roadmap

This is an independent Terrain Diffusion addon. Minimal-install acceptance comes
before pack integration. Build success does not close in-game acceptance.

| Milestone | Outcome | Gate |
| --- | --- | --- |
| M0 - Standalone foundation | Independent build, four placeholder stones, CI | Build and domain checks pass |
| M1 - Minimal-install acceptance | Test with only NeoForge, TD and this addon | Client/server, generation, mining, save/reopen and timings recorded |
| M2 - Geology controls and diagnostics | Explainable, tunable, persistent geology | Config changes cannot silently change a continuing world's geology |
| M3 - Assets and masonry | Distinct visual/material building vocabulary | Licensed art, useful shapes/recipes, stable block IDs |
| M4 - City palette API | Stable regional identity for external city systems | Documented API without requiring a city mod |
| M5 - Optional integrations | Ulti-World adapter and evaluated compatibility | Standalone remains supported and independently tested |

The authoritative work list is the repository's GitHub issues and milestones.
The [reproducibility contract](reproducibility-contract.md) defines geology/save
continuity acceptance separately from stronger final-feature diagnostics.
planning/backlog.json records the initial issue definitions and acceptance
criteria. planning/github-index.json maps those definitions to GitHub URLs.

Scope excludes a full tectonic simulation, automatic city culture assignment,
and existing-world block conversion. Final assets and Ulti-World integration
are deferred. Optional integrations must not become mandatory dependencies.

Issue #13 now has a code-first masonry implementation using vanilla texture
placeholders. Final art (#12) and in-game placement/waterlogging review remain
M3 acceptance gates; see docs/stone-families.md.

The researched target is four regional families per host layer alongside vanilla
(#22), coarse-terrain-derived terranes (#11), and future regional mineral systems
(#23). See docs/geology-research.md and planning/geology. These are planned
versioned changes, not features of the current four-rock prototype.

Issue #11's [bounded center/orientation diagnostic](td-tracking.md) remains
evidence only. Localizing extrema does not waive longitudinal continuity or
resolve geological history. New held-out morphology coverage and independent
geological plausibility/coherence remain gates; #9/#11 stay open. No continuing
geology-1 snapshot is migrated, and isolated sampling work is not route savings.
