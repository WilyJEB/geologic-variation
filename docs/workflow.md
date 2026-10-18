# Development workflow

1. Select one issue and branch from main using feature/<topic> or fix/<topic>.
2. Keep deterministic geological rules in domain/, the TD adapter in Geology,
   and generation application in the mixin. Keep city/pack adapters optional.
3. Run scripts/bootstrap.ps1 and gradlew build with JDK 21.
4. Record relevant evidence from a minimal TD plus addon installation.
   World generation changes require reproducibility, ore/carver and save/reopen
   checks; pure tests alone do not certify them.
5. Open a PR describing observable behavior, checks, compatibility and save
   impact. Merge after required CI and relevant acceptance are recorded.
6. Version release artifacts, document dependency versions and provide checksums.

Do not commit model weights, worlds, native libraries, dependency JARs, caches,
logs with private information or inspection checkouts. Preserve stable block IDs.
Store editable art and author/license provenance separately from runtime exports.
Integrate with packs only through a later explicit adapter/release and test profile.
