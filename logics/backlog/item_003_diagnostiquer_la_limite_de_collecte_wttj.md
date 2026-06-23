## item_003_diagnostiquer_la_limite_de_collecte_wttj - Diagnostiquer la limite de collecte WTTJ
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 98
> Confidence: 94
> Progress: 100%
> Complexity: Low
> Theme: Provider diagnostics
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# Problem
The WTTJ run accepts `--target-offers 1000`, but the default query set may have far fewer provider results. The operator currently sees only `Discovered: 140`, without knowing whether this is caused by pagination, query capacity, Algolia limits, or deduplication.

# Scope
- In:
  - expose raw provider hits, duplicate hits and per-query Algolia capacity in CLI output
  - preserve the current connector API for existing callers
  - cover the diagnostics with focused tests
- Out:
  - adding new WTTJ queries
  - adding a second provider
  - changing scoring/ranking rules

# Acceptance criteria
- AC1: The CLI explains when the requested target is not reached and includes target, unique discovered count, `max_pages` and `hits_per_page`.
- AC2: The CLI reports raw provider hits and duplicate hits removed during WTTJ discovery.
- AC3: The CLI reports per-query capacity using Algolia metadata (`nbHits`, `nbPages`) so low-volume queries are visible.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: CLI target miss output is in scope.
- request-AC2 -> This backlog slice. Proof: raw and duplicate hit reporting is in scope.
- request-AC3 -> This backlog slice. Proof: per-query Algolia capacity reporting is in scope.

# Decision framing
- Product framing: Not needed
- Product signals: (none detected)
- Product follow-up: No product brief follow-up is expected based on current signals.
- Architecture framing: Not needed
- Architecture signals: (none detected)
- Architecture follow-up: No architecture decision follow-up is expected based on current signals.

# Links
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
- Request: `logics/request/req_002_diagnose_wttj_collection_limit.md`
- Primary task(s): `task_003_diagnostiquer_la_limite_de_collecte_wttj`

# AI Context
- Summary: Diagnostiquer la limite de collecte WTTJ
- Keywords: backlog-groom, request, diagnostiquer la limite de collecte wttj, bounded slice
- Use when: Use when implementing or reviewing the delivery slice for Diagnostiquer la limite de collecte WTTJ.
- Skip when: Skip when the change is unrelated to this delivery slice or its linked request.

# Priority
- Impact:
- Prevents misreading `--target-offers` as a guaranteed count and makes query breadth decisions evidence-based.
- Urgency:
- Immediate follow-up to a confusing operator run.

# Notes
- Hybrid rationale: Derived from request `req_002_diagnose_wttj_collection_limit` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_002_diagnose_wttj_collection_limit.md`.
- Generated locally by logics-manager.
- Task `task_003_diagnostiquer_la_limite_de_collecte_wttj` implements this slice.
- Task `task_003_diagnostiquer_la_limite_de_collecte_wttj` was finished via `logics-manager flow finish task` on 2026-06-23.

# Tasks
- `task_003_diagnostiquer_la_limite_de_collecte_wttj`
