## task_003_diagnostiquer_la_limite_de_collecte_wttj - Diagnostiquer la limite de collecte WTTJ
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 98
> Confidence: 94
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# Definition of Done (DoD)
- [x] WTTJ discovery exposes raw hits, duplicate hits and target-reached state.
- [x] WTTJ page searches preserve Algolia `nbHits` and `nbPages` metadata.
- [x] CLI reports target miss diagnostics with target, discovered count, `max_pages` and `hits_per_page`.
- [x] CLI reports per-query provider capacity.
- [x] Existing `discover()` callers still receive a list of offers.
- [x] Focused tests cover discovery diagnostics.
- [x] Validation passes.

# Backlog
- `item_003_diagnostiquer_la_limite_de_collecte_wttj`

# Acceptance criteria
- AC1: The CLI explains when the requested target is not reached and includes target, unique discovered count, `max_pages` and `hits_per_page`.
- AC2: The CLI reports raw provider hits and duplicate hits removed during WTTJ discovery.
- AC3: The CLI reports per-query capacity using Algolia metadata (`nbHits`, `nbPages`) so low-volume queries are visible.

# Validation
- Run `python3 -m pytest`.
- Run `python3 -m scrappy run --db /tmp/scrappy-limit.sqlite --profile examples/profile.yaml --target-offers 1000 --max-pages 5 --xlsx /tmp/scrappy-limit.xlsx`.
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run `logics-manager health`.
- Run `logics-manager flow finish task logics/tasks/task_003_diagnostiquer_la_limite_de_collecte_wttj.md` after implementation.
- Finish workflow executed on 2026-06-23.
- Linked backlog/request close verification passed.

# Report
- Root cause: the default WTTJ query set currently has only 146 raw Algolia hits with `--max-pages 5 --hits-per-page 20`, and 140 unique offers after deduplication. `--target-offers 1000` cannot be reached without broader queries, more providers, or different search criteria.
- Implemented `DiscoveryResult` and `SearchPage` diagnostics in `scrappy/connectors/wttj.py`.
- Updated `scrappy/cli.py` to print raw provider hits, duplicate hits removed, a target-not-reached warning and per-query capacity.
- Smoke proof on 2026-06-23: `python3 -m scrappy run --db /tmp/scrappy-limit.sqlite --profile examples/profile.yaml --target-offers 1000 --max-pages 5 --xlsx /tmp/scrappy-limit.xlsx` reported 140 unique offers, 146 raw hits, 6 duplicates, and per-query capacities of 66, 6, 72 and 2 hits.
- Test proof on 2026-06-23: `python3 -m pytest` passed with 18 tests.
- Finished on 2026-06-23.
- Linked backlog item(s): `item_003_diagnostiquer_la_limite_de_collecte_wttj`
- Related request(s): `req_002_diagnose_wttj_collection_limit`

# AC Traceability
- AC1 -> Target miss diagnostics. Proof: `scrappy/cli.py` prints target requested, unique discovered count, `max_pages` and `hits_per_page` when `DiscoveryResult.target_reached` is false.
- AC2 -> Raw and duplicate hit diagnostics. Proof: `scrappy/connectors/wttj.py` records `raw_hits` and `duplicate_hits`; `scrappy/cli.py` prints them.
- AC3 -> Per-query capacity. Proof: `scrappy/connectors/wttj.py` preserves `nb_hits` and `nb_pages`; `scrappy/cli.py` prints query capacity lines.

# AI Context
- Summary: Implement CLI diagnostics for WTTJ target-offer collection limits.
- Keywords: wttj, algolia, diagnostics, target-offers, nbHits, nbPages, deduplication
- Use when: Explaining why a WTTJ run cannot reach requested target volume.
- Skip when: Adding new providers or changing ranking/scoring.

# Links
- Request: `req_002_diagnose_wttj_collection_limit`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
