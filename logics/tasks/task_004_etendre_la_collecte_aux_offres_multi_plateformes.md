## task_004_etendre_la_collecte_aux_offres_multi_plateformes - Etendre la collecte aux offres multi-plateformes
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 96
> Confidence: 88
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex

# Definition of Done (DoD)
- [x] Indeed automatic access path is analyzed; LinkedIn fallback is documented if Indeed is not practical.
- [x] The selected second provider automatic mode is implemented.
- [x] Multi-provider CLI orchestration is implemented.
- [x] Provider statistics are reported consistently.
- [x] Inter-source duplicate fusion is implemented for high-confidence duplicates.
- [x] XLSX output exposes source, merged-source and downrank signals.
- [x] Sponsored/repost/recruitment-agency signals are downranked and visible.
- [x] Provider constraints are documented.
- [x] Acceptance criteria are covered.
- [x] Validation passes.

# Backlog
- `item_004_etendre_la_collecte_aux_offres_multi_plateformes`

# Acceptance criteria
- AC1: La CLI permet de lancer une collecte multi-source explicite, par exemple WTTJ plus Indeed si l'analyse d'acces le confirme, avec options documentees pour selectionner les providers actifs.
- AC2: Le second provider implemente une strategie d'acces automatique stable et documentee, sans import manuel et sans dependance obligatoire a un scraping authentifie fragile.
- AC3: Chaque provider expose des statistiques de run homogenes: hits bruts, offres normalisees, offres uniques, doublons intra/inter-source, erreurs et raison d'arret lorsque le target n'est pas atteint.
- AC4: La base locale conserve la provenance source et permet de relier des annonces equivalentes vues sur plusieurs plateformes sans perdre les identifiants source originaux.
- AC5: Le scoring et le XLSX restent communs a toutes les sources; le XLSX permet de filtrer par source et de voir si une offre a ete observee sur plusieurs plateformes.
- AC6: Les doublons probables entre plateformes sont fusionnes automatiquement lorsque le niveau de confiance est suffisant, avec conservation des identifiants source et d'une raison de similarite lisible.
- AC7: Le comportement en cas d'echec partiel d'un provider est robuste: les autres providers continuent, le run est trace, et l'utilisateur voit quelles sources ont echoue avec warning.
- AC8: Les limites legales/techniques de LinkedIn, Indeed et du provider choisi sont documentees dans le README ou une spec Logics avant implementation complete.

# Validation
- Run `python3 -m pytest`.
- Run a smoke collection with WTTJ plus the selected second provider or import fixture.
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run `logics-manager health`.
- Run `logics-manager flow finish task logics/tasks/task_004_etendre_la_collecte_aux_offres_multi_plateformes.md` after implementation.
- Finish workflow executed on 2026-06-24.
- Linked backlog/request close verification passed.

# Report
- Current decisions: prioritize Indeed, automatic-only ingestion, quality-over-volume, targeted profile queries, automatic high-confidence duplicate fusion, downrank and signal sponsored/repost/recruitment-agency offers, keep Paris/full-remote/substantial-hybrid geography, continue with warnings on partial provider failure.
- Indeed access analysis: official Indeed partner documentation is oriented toward job posting / ATS / apply integrations rather than an unauthenticated candidate-side job search API; the public RSS endpoint returned `403 Forbidden` for profile queries; therefore the implemented automatic path is a configurable HTTP JSON adapter for a partner or third-party Indeed API via `SCRAPPY_INDEED_API_URL` and optional `SCRAPPY_INDEED_API_KEY`.
- Implemented provider-neutral `DiscoveryResult` and `SearchPage` in `scrappy/connectors/base.py`.
- Implemented `IndeedApiConnector` in `scrappy/connectors/indeed.py`.
- Updated `scrappy run` to accept repeated `--provider`, run each provider independently, continue with warnings on provider failure, and print provider stats.
- Added SQLite `offer_aliases` and normalized dedupe keys so high-confidence cross-source duplicates are fused while preserving source identifiers.
- Updated XLSX output with `merged_sources` and `duplicate_reason`.
- Added scoring downrank signals for sponsored/promoted, repost and recruitment-agency offers.
- Documented provider constraints and configuration in `README.md`.
- Smoke proof without real Indeed API credentials: `python3 -m scrappy run --db /tmp/scrappy-multi.sqlite --profile examples/profile.yaml --provider wttj-public --provider indeed-api --target-offers 5 --max-pages 1 --xlsx /tmp/scrappy-multi.xlsx` continued after Indeed warning and wrote XLSX.
- Smoke proof with local automatic Indeed fixture endpoint: command discovered and scored 1 Indeed offer and wrote `/tmp/scrappy-indeed-fixture.xlsx`.
- Test proof: `python3 -m pytest` passed with 22 tests.
- Finished on 2026-06-24.
- Linked backlog item(s): `item_004_etendre_la_collecte_aux_offres_multi_plateformes`
- Related request(s): `req_003_multi_platform_job_collection`

# AC Traceability
- AC1 -> Multi-source CLI. Proof: `scrappy/cli.py` accepts repeated `--provider` values including `wttj-public` and `indeed-api`.
- AC2 -> Automatic Indeed mode. Proof: `scrappy/connectors/indeed.py` implements HTTP JSON automatic collection configured by environment variables, with no manual import path.
- AC3 -> Provider stats. Proof: `DiscoveryResult`/`SearchPage` are shared and printed by CLI for each provider.
- AC4 -> Source provenance and linking. Proof: `scrappy/storage.py` adds `offer_aliases` and preserves source/source_id aliases for merged offers.
- AC5 -> Common scoring/XLSX. Proof: all providers normalize to `Offer`; `scrappy/reporting.py` writes source and merge columns.
- AC6 -> Duplicate fusion. Proof: `upsert_offer` merges high-confidence normalized title/company/location duplicates and records duplicate reason.
- AC7 -> Partial failure behavior. Proof: CLI catches provider `RuntimeError`, marks provider run failed, prints warning and continues.
- AC8 -> Constraints documented. Proof: `README.md` documents Indeed official/RSS findings, third-party API configuration and no aggressive scraping posture.

# AI Context
- Summary: Implement the multi-platform ingestion slice once the second provider and ingestion mode are selected.
- Keywords: multi-provider, indeed, linkedin, wttj, deduplication, provider-stats, xlsx
- Use when: Implementing the next ingestion provider and shared multi-source orchestration.
- Skip when: Still refining provider choice or working only on WTTJ.

# Links
- Request: `req_003_multi_platform_job_collection`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
