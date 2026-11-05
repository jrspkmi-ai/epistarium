# Migration: EPISTARIUM 0.7.1 → 0.8.0

The Observatory is opt-in. Core Jorhas Path Finding, Full Research, nine specialist skill contracts, JSON/CSV evidence schemas and the existing CLI commands remain unchanged. The `jorhas._step()` method now also publishes an optional event to a context-local monitoring callback. No callback means the v0.7.1 behavior is retained.

New:
- `python -m epistarium observatory --open`
- `python -m epistarium observatory --idea "TOPIC" --mode pathfind --open`
- `--lang en|id` for report language; browser language can change separately.
- `~/.epistarium-observatory/runs/<id>/` and `.../outputs/<id>/` for local session state.
- Session-specific online-access and final-artifact approval gates.
- `RELEASE_AUTHORIZED` means the operator authorized an artifact package, not scientific verification.

No automatic migration of old run reports is performed. The old `RUN_LOG.json`, `RUN_MANIFEST.json`, source/data ledgers and final research manifest retain their original formats. Do not place new session stores inside GitHub repositories. Do not replace the repository's more recent branding assets or optimized CI workflow with an older ZIP snapshot.
