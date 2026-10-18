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
planning/backlog.json records the initial issue definitions and acceptance
criteria. planning/github-index.json maps those definitions to GitHub URLs.

Scope excludes a full tectonic simulation, automatic city culture assignment,
and existing-world block conversion. Final assets and Ulti-World integration
are deferred. Optional integrations must not become mandatory dependencies.
