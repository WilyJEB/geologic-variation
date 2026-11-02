# Reproducibility and mod compatibility

## Supported geology-1 contract

For identical supported seed, scale, saved geology settings, generator version,
TD artifact, model inputs and backend context, the addon promises deterministic
regional identity, palette selection and its natural-host assignment. Traversal
order does not select a different regional rock. Saved settings remain active on
reopen; incompatible inputs reject rather than silently changing new geology.
Accepted evidence is limited to the recorded environment and sampled coordinates,
not every hardware/driver combination or arbitrary modpack.

The addon preserves vanilla/NeoForge feature generation and does not promise
identical final ore, vegetation or other feature positions across every chunk
population order. Later features may replace a host with ore or another eligible
material. The natural traces demonstrate this behavior without the addon as well
as with it; the supported promise concerns geology's assignment, not a global
rewrite of vanilla's feature/RNG/order behavior.

This policy follows the user's delegated choice on 2026-11-01 to favor vanilla
behavior and final-pack compatibility. It resolves #5's contract decision and
accepts that issue's original province/save-continuity scope using existing
runtime evidence. It does not turn the stronger failed final-block test into a
pass, change generation rules, or certify untested combinations.

## Compatibility rationale and implementation boundary

NeoForge's [1.21.1 biome-modifier documentation](https://docs.neoforged.net/docs/1.21.1/worldgen/biomemodifier/)
describes adding/removing placed features through biome IDs/tags and decoration
steps. Keeping those shared extension points and existing ore-host tags intact
is the compatibility choice here. This is an engineering decision supported by
the measured baseline, not a claim that all mods share one reproducibility policy.

Do not globally reseed/reorder another mod's features, serialize all worldgen,
broaden exact-block predicates, convert ores back to host rock, or rescan player
construction merely to equalize final hashes. Integrations must be explicit and
bounded, with minimal-install and pack-specific acceptance. Ulti-World remains
optional. A reproduced compatibility regression is still a bug to investigate;
this contract is not permission to dismiss missing ores or altered cavities.

## Evidence and retained diagnostics

- [Production matrix](runtime-matrix-2026-10-28.md): actual region records at
  scales 1/6, negative-coordinate contacts, snapshot/restart preservation,
  matching sampled new neighbors and sampled non-TD dimension gating.
- [Host/stage acceptance](host-acceptance-2026-11-01.md): complete SURFACE/CARVERS
  states match across traversal; normalized addon/TD-only states match. All four
  current hosts pass the recorded mining/ore/carver fixtures.
- [Natural write trace](natural-coal-trace-2026-11-01.md): neighboring gravel or
  emerald writes can skip coal-host random draws, shift later veins and produce
  saved host/coal differences in both arms, without regional palette conflicts.
- [Startup guards](context-startup-2026-11-01.md): continuing config isolation and
  five rejection/restoration cases. Broader #9 runtime coverage remains open.

`runtime-acceptance.py reproducibility` retains its strict positioned-regional-
block assertion and known scale-6 failure. Keep its output and portable evidence
visible as a stronger diagnostic. Do not replace it with a normalized hash or
claim whole-world bitwise determinism. Stage/palette acceptance and final-state
diagnostics answer different questions.

Future sampler/palette/deposit changes under #11/#22/#23 still require explicit
#9 versioning and continuing-world behavior. This policy changes neither
geology-1 nor the measured 14.383-second cold-route overhead; #11 remains the
performance target after its prerequisites.
