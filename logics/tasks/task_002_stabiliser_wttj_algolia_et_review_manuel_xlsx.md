## task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx - Stabiliser WTTJ Algolia et review manuel XLSX
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 98
> Confidence: 92
> Progress: 0
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# Definition of Done (DoD)
- [ ] WTTJ Algolia connector supports pagination up to a configurable limit.
- [ ] Run command defaults to the profile-derived query set without `FPGA engineer`.
- [ ] Run command supports target volume around 100 offers and can continue when insufficient eligible results are found.
- [ ] Retry/backoff exists for transient provider failures.
- [ ] Contract/location/internship filters are represented in normalized offers and scoring/rejection reasons.
- [ ] XLSX writer produces `all_scored` and `rejected` sheets.
- [ ] XLSX contains `decision`, `review_note`, and stable offer identifiers for import.
- [ ] CLI command imports `selected`, `rejected`, `maybe` decisions from XLSX into SQLite.
- [ ] SQLite schema persists manual review decisions.
- [ ] Unit tests cover pagination parameters, rejection routing, XLSX sheet structure and decision import.
- [ ] Smoke command demonstrates WTTJ collection, XLSX output and import path.
- [ ] Logics validation passes.

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

# Report
- Task created for the next implementation slice. Implementation not started in this task yet.

# AI Context
- Summary: Implement WTTJ Algolia pagination and XLSX manual review import in the CLI workflow.
- Keywords: wttj, algolia, pagination, retry, xlsx, sqlite, review-import, selected, rejected, maybe
- Use when: Coding or validating the WTTJ stabilization and manual review slice.
- Skip when: Work is about new providers, UI, or CV/letter generation.

# Links
- Request: `req_001_stabilize_wttj_review`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
