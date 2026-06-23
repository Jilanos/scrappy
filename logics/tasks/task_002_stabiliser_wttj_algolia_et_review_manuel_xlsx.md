## task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx - Stabiliser WTTJ Algolia et review manuel XLSX
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 98
> Confidence: 93
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex

# Definition of Done (DoD)
- [x] WTTJ Algolia connector supports pagination up to a configurable limit.
- [x] Run command defaults to the profile-derived query set without `FPGA engineer`.
- [x] Run command supports target volume around 100 offers and can continue when insufficient eligible results are found.
- [x] Retry/backoff exists for transient provider failures.
- [x] Contract/location/internship filters are represented in normalized offers and scoring/rejection reasons.
- [x] XLSX writer produces `all_scored` and `rejected` sheets.
- [x] XLSX contains `decision`, `review_note`, and stable offer identifiers for import.
- [x] CLI command imports `selected`, `rejected`, `maybe` decisions from XLSX into SQLite.
- [x] SQLite schema persists manual review decisions.
- [x] Unit tests cover pagination parameters, rejection routing, XLSX sheet structure and decision import.
- [x] Smoke command demonstrates WTTJ collection, XLSX output and import path.
- [x] Logics validation passes.

# Backlog
- `item_002_stabiliser_wttj_algolia_et_review_manuel_xlsx`

# Acceptance criteria
- AC1: `scrappy run` can collect about 100 WTTJ offers through Algolia pagination and produce an XLSX.
- AC2: Transient Algolia errors use bounded retry/backoff and leave useful console messages.
- AC3: Default queries are `electronics engineer`, `signal processing engineer`, `R&D engineer`, `medical imaging engineer`; `FPGA engineer` is not included.
- AC4: Internship/apprenticeship offers are excluded or routed to `rejected` with an explicit reason.
- AC5: Non-eligible but informative offers remain in `all_scored` with `eligible=false`.
- AC6: XLSX contains `all_scored` and `rejected` sheets with stable offer IDs, decision fields and scoring reasons.
- AC7: A CLI import command persists `selected`, `rejected`, and `maybe` review decisions from XLSX into SQLite.
- AC8: No web UI is introduced.

# Validation
- Run `python3 -m pytest`.
- Run `python3 -m scrappy run --db /tmp/scrappy-review.sqlite --profile examples/profile.yaml --top 5 --xlsx /tmp/scrappy-review.xlsx`.
- Run the new review import command against a fixture XLSX.
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run `logics-manager flow finish task task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx.md` after implementation.
- Finish workflow executed on 2026-06-23.
- Linked backlog/request close verification passed.

# Report
- Implemented WTTJ Algolia pagination with configurable `--target-offers`, `--max-pages`, `--hits-per-page` and bounded retry/backoff.
- Added default WTTJ query set: `electronics engineer`, `signal processing engineer`, `R&D engineer`, `medical imaging engineer`; `FPGA engineer` remains in profile skills/roles but is not used as a default query.
- Added CDI/full-time contract gate to scoring, alongside Paris/full-remote/substantial-hybrid, seniority and internship/apprenticeship rejection.
- Reworked XLSX export to include `all_scored` and `rejected` sheets, stable source identifiers and manual review fields.
- Added `scrappy import-reviews` to persist `selected`, `maybe`, `rejected` decisions into SQLite.
- Added tests for XLSX sheet structure, rejection routing, pagination, manual review persistence and import CLI.
- Smoke validated WTTJ collection/export and review import on `/tmp/scrappy-review.sqlite`.
- Finished on 2026-06-23.
- Linked backlog item(s): `item_002_stabiliser_wttj_algolia_et_review_manuel_xlsx`
- Related request(s): `req_001_stabilize_wttj_review`

# AI Context
- Summary: Implement WTTJ Algolia pagination and XLSX manual review import in the CLI workflow.
- Keywords: wttj, algolia, pagination, retry, xlsx, sqlite, review-import, selected, rejected, maybe
- Use when: Coding or validating the WTTJ stabilization and manual review slice.
- Skip when: Work is about new providers, UI, or CV/letter generation.

# Links
- Request: `req_001_stabilize_wttj_review`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# AC Traceability
- AC1 -> WTTJ pagination and XLSX export. Proof: `scrappy/connectors/wttj.py` implements `target_count`, `max_pages`, `hits_per_page`; smoke run wrote `/tmp/scrappy-review.xlsx`.
- AC2 -> Retry/backoff for Algolia. Proof: `WttjPublicConnector._post_json` retries transient HTTP/URL/timeout failures before raising a runtime error.
- AC3 -> Default query set. Proof: `examples/profile.yaml` and `scrappy/cli.py` default to `electronics engineer`, `signal processing engineer`, `R&D engineer`, `medical imaging engineer`.
- AC4 -> Internship/apprenticeship rejection. Proof: `scrappy/scoring.py` hard-excludes these terms and `tests/test_scoring.py` covers the rejection.
- AC5 -> Non-eligible retention. Proof: `scrappy/reporting.py` writes every ranked offer to `all_scored`, with non-eligible offers also routed to `rejected`.
- AC6 -> Review workbook fields. Proof: `scrappy/reporting.py` writes `all_scored` and `rejected` with `source`, `source_id`, `decision`, `review_note`, `eligible`, `score`, `reasons`, `url`; `tests/test_reporting.py` passes.
- AC7 -> Manual review import. Proof: `scrappy import-reviews` persists `selected`, `maybe`, `rejected` into SQLite; `tests/test_cli.py` and smoke import pass.
