## task_005_selectionner_et_valider_une_api_tierce_indeed - Selectionner et valider une API tierce Indeed
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 94
> Confidence: 84
> Progress: 70
> Complexity: Medium
> Theme: Provider validation
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex

# Definition of Done (DoD)
- [x] At least two third-party Indeed API options are compared with explicit criteria.
- [x] A recommended API is selected, or a no-go decision is documented with fallback.
- [x] Required local credentials/configuration are documented.
- [x] `scrappy/connectors/indeed.py` is adapted if the selected API needs provider-specific mapping or headers.
- [x] Fixture tests cover the selected API response shape.
- [ ] Real smoke run validates Indeed-only collection with credentials.
- [ ] Real smoke run validates WTTJ + Indeed multi-provider collection.
- [ ] XLSX output from the real smoke is usable for review.
- [x] README or Logics spec documents cost/quota/terms/risks and troubleshooting.
- [ ] Acceptance criteria are covered.
- [x] Validation passes.

# Backlog
- `item_005_selectionner_et_valider_une_api_tierce_indeed`

# Acceptance criteria
- AC1: Au moins deux options d'API tierce Indeed sont comparees avec criteres explicites: acces/cle, cout ou free tier, limites de quota, champs disponibles, pagination, fraicheur, pays supportes, risques et effort d'integration.
- AC2: Une option recommandee est choisie ou, si aucune option n'est acceptable, la raison est documentee avec une alternative concrete.
- AC3: Le connecteur `indeed-api` est adapte si necessaire au format de l'API choisie sans casser les tests existants ni le contrat multi-provider.
- AC4: Un smoke run reel avec credentials utilisateur ou environnement local valide la collecte Indeed seule, puis WTTJ + Indeed, et produit un XLSX exploitable.
- AC5: Les offres Indeed collectees alimentent le modele `Offer` avec au minimum titre, entreprise, localisation, URL, type de contrat si disponible, description/snippet et identifiant stable.
- AC6: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint et warning en cas de limite ou erreur API.
- AC7: La documentation indique comment configurer l'API choisie, quelles variables d'environnement sont requises, quelles limites/quota existent, et comment diagnostiquer un echec.
- AC8: Les limites legales/techniques de l'API retenue sont documentees avant tout usage regulier.

# Validation
- Run `python3 -m pytest`.
- Run `python3 -m scrappy run --provider indeed-api --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-indeed-real.xlsx`.
- Run `python3 -m scrappy run --provider wttj-public --provider indeed-api --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-multi-real.xlsx`.
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run `logics-manager health`.
- Run `logics-manager flow finish task logics/tasks/task_005_selectionner_et_valider_une_api_tierce_indeed.md` after implementation.

# Report
- Compared Apify, HasData, Browse AI / Oxylabs-style extractors. Apify is selected for first validation because it has a documented synchronous API route that runs an actor and returns dataset items directly to the local CLI.
- Recommended default: Apify `misceres~indeed-scraper`, because its input shape is documented as `country`, `location`, `position`, `maxItems`, `saveOnlyUniqueItems` and it is maintained on Apify.
- Supported alternative: Apify `borderline~indeed-scraper`, because it has a high current rating and pay-per-result pricing but uses a different input shape (`query`, `country`, `location`, `maxRows`).
- Fallback candidate: HasData Indeed scraper, because it returns normalized Indeed data across 60+ locales and has free trial credits, but its scraper flow is asynchronous and requires polling.
- Implemented Apify mode in `scrappy/connectors/indeed.py` via `SCRAPPY_INDEED_PROVIDER=apify`, `SCRAPPY_INDEED_APIFY_TOKEN`, `SCRAPPY_INDEED_APIFY_ACTOR`, `SCRAPPY_INDEED_COUNTRY`, and `SCRAPPY_INDEED_LOCATION`.
- Added tests for missing Apify token, Apify output mapping, and `borderline~indeed-scraper` input payload.
- Updated README with provider comparison, Apify configuration, smoke command and fallback notes.
- Validation run: `python3 -m pytest` passed with 25 tests.
- Available smoke without token: `SCRAPPY_INDEED_PROVIDER=apify python3 -m scrappy run --provider indeed-api --target-offers 2 --max-pages 1 --xlsx /tmp/scrappy-indeed-apify-missing-token.xlsx` continues with warning `SCRAPPY_INDEED_APIFY_TOKEN`.
- Blocker: no `SCRAPPY_INDEED_APIFY_TOKEN` or other real Indeed API key is present in the local environment, so AC4 real Indeed-only and WTTJ+Indeed smoke runs cannot be completed yet.

# Partial AC Traceability
- AC1 -> Provider comparison. Proof: README provider comparison covers Apify, HasData, Browse AI/Oxylabs-style extractors.
- AC2 -> Recommendation. Proof: README and report select Apify default with HasData fallback.
- AC3 -> Connector adaptation. Proof: `scrappy/connectors/indeed.py` supports `SCRAPPY_INDEED_PROVIDER=apify` and Apify actor input mapping.
- AC5 -> Offer model mapping. Proof: `tests/test_indeed_connector.py` maps Apify `positionName`, `company`, `location`, `jobType`, `url`, `id`, `description` to `Offer`.
- AC6 -> Provider stats and warnings. Proof: existing `DiscoveryResult` path is reused; missing-token smoke emits warning and continues.
- AC7 -> Configuration docs. Proof: README documents Apify env vars and smoke command.
- AC8 -> Limit docs. Proof: README documents cost/quota/terms considerations and fallback candidates.

# AI Context
- Summary: Compare, select, integrate and validate a real third-party Indeed API for Scrappy.
- Keywords: indeed, third-party-api, credentials, smoke-test, provider-validation, json-mapping
- Use when: Evaluating Indeed API providers or validating real Indeed collection.
- Skip when: Work is unrelated to Indeed provider access.

# Links
- Request: `req_004_validate_third_party_indeed_api`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
