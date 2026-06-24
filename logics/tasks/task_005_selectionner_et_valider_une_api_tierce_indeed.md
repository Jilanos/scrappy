## task_005_selectionner_et_valider_une_api_tierce_indeed - Selectionner et valider une API tierce Indeed
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 94
> Confidence: 86
> Progress: 0%
> Complexity: Medium
> Theme: Provider validation
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# Definition of Done (DoD)
- [ ] At least two third-party Indeed API options are compared with explicit criteria.
- [ ] A recommended API is selected, or a no-go decision is documented with fallback.
- [ ] Required local credentials/configuration are documented.
- [ ] `scrappy/connectors/indeed.py` is adapted if the selected API needs provider-specific mapping or headers.
- [ ] Fixture tests cover the selected API response shape.
- [ ] Real smoke run validates Indeed-only collection with credentials.
- [ ] Real smoke run validates WTTJ + Indeed multi-provider collection.
- [ ] XLSX output from the real smoke is usable for review.
- [ ] README or Logics spec documents cost/quota/terms/risks and troubleshooting.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.

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
- Not started. Ready for implementation once provider comparison begins.

# AI Context
- Summary: Compare, select, integrate and validate a real third-party Indeed API for Scrappy.
- Keywords: indeed, third-party-api, credentials, smoke-test, provider-validation, json-mapping
- Use when: Evaluating Indeed API providers or validating real Indeed collection.
- Skip when: Work is unrelated to Indeed provider access.

# Links
- Request: `req_004_validate_third_party_indeed_api`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
