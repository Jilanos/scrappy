## task_006_integrer_l_api_offres_d_emploi_france_travail - Integrer l API Offres d emploi France Travail
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 95
> Confidence: 88
> Progress: 80
> Complexity: Medium
> Theme: Provider expansion
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex

# Definition of Done (DoD)
- [x] France Travail OAuth client-credentials flow is implemented without storing secrets.
- [x] `france-travail` provider is available from the CLI.
- [x] France Travail offer responses are mapped to `Offer`.
- [x] Pagination/range behavior is implemented and represented in provider stats.
- [x] Location/query parameters are aligned with Paris/full remote/substantial-hybrid strategy.
- [x] Fixture tests cover token request, offer mapping and pagination/statistics.
- [ ] Real smoke France Travail run is executed when credentials are available.
- [ ] Real WTTJ + France Travail smoke run is executed when credentials are available.
- [x] README documents setup, env vars, scopes/API and troubleshooting.
- [ ] Acceptance criteria are covered.
- [x] Validation passes.

# Backlog
- `item_006_integrer_l_api_offres_d_emploi_france_travail`

# Acceptance criteria
- AC1: La CLI supporte un provider `france-travail` activable avec `--provider france-travail`, compatible avec les providers existants.
- AC2: Le connecteur France Travail obtient et utilise un token OAuth depuis des variables d'environnement locales, sans stocker de secret dans le depot.
- AC3: Les offres France Travail sont mappees vers `Offer` avec au minimum identifiant stable, titre, entreprise, localisation, contrat, description/snippet, URL et champs remote/salaire si disponibles.
- AC4: La collecte utilise les requetes profil ciblees et le perimetre Paris/full remote/substantial hybrid; les offres hors cible restent visibles avec raisons de rejet/downrank dans le XLSX.
- AC5: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint, pagination/range utilisee, et warnings API.
- AC6: La deduplication inter-source fonctionne entre France Travail, WTTJ et futurs providers en conservant les identifiants source.
- AC7: Un smoke reel France Travail seul produit un XLSX exploitable.
- AC8: Un smoke reel WTTJ + France Travail produit un XLSX exploitable et continue avec warning si un provider echoue.
- AC9: La documentation explique comment creer/configurer l'application France Travail, quelles variables d'environnement utiliser, les scopes/API requis, limites connues et commandes de validation.

# Validation
- Run `python3 -m pytest`.
- Run `python3 -m scrappy run --provider france-travail --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-france-travail.xlsx`.
- Run `python3 -m scrappy run --provider wttj-public --provider france-travail --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-wttj-france-travail.xlsx`.
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run `logics-manager health`.
- Run `logics-manager flow finish task logics/tasks/task_006_integrer_l_api_offres_d_emploi_france_travail.md` after implementation.

# Report
- Implemented `FranceTravailConnector` in `scrappy/connectors/france_travail.py`.
- Added `--provider france-travail` to the CLI.
- Implemented OAuth client credentials using `SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID`, `SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET`, configurable scope/token/search URLs, department/location and contract filters.
- Implemented France Travail `range` pagination and Content-Range total parsing.
- Mapped France Travail offer fields to `Offer`: id, intitule, entreprise, lieuTravail, contrat, experience, salaire, teletravail, description and canonical detail URL/origin URL.
- Added fixture tests for missing credentials, offer mapping, pagination/statistics and token caching.
- Updated README with configuration and smoke commands.
- Test proof: `python3 -m pytest` passed with 30 tests.
- Available smoke proof without credentials: `python3 -m scrappy run --provider france-travail --target-offers 2 --max-pages 1 --xlsx /tmp/scrappy-france-travail-missing-creds.xlsx` continues with a warning and writes XLSX.
- Blocker: no `SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID` or `SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET` is present in the local environment, so real France Travail-only and WTTJ+France Travail smoke runs cannot be completed yet.

# Partial AC Traceability
- AC1 -> CLI provider. Proof: `scrappy/cli.py` accepts `--provider france-travail`.
- AC2 -> OAuth. Proof: `FranceTravailConnector` obtains OAuth token from env-provided client credentials and does not persist secrets.
- AC3 -> Offer mapping. Proof: `tests/test_france_travail_connector.py` covers mapping from France Travail JSON to `Offer`.
- AC4 -> Targeted collection. Proof: connector sends profile query, department/location and contract filters.
- AC5 -> Stats. Proof: connector returns `SearchPage` with hits, total and pages from Content-Range.
- AC6 -> Inter-source deduplication. Proof: connector emits normal `Offer` source/source_id records consumed by existing storage alias/dedupe path.
- AC9 -> Documentation. Proof: README documents env vars, endpoints and validation commands.

# AI Context
- Summary: Implement the official France Travail job offers API provider for Scrappy.
- Keywords: france-travail, pole-emploi, jobs-api, oauth, provider, paris, free-api
- Use when: Implementing or validating France Travail as a Scrappy job source.
- Skip when: Work concerns paid Indeed APIs or WTTJ-only behavior.

# Links
- Request: `req_005_integrate_france_travail_jobs_api`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
