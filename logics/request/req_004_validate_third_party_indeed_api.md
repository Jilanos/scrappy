## req_004_validate_third_party_indeed_api - Selectionner et valider une API tierce Indeed
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 94
> Confidence: 86
> Complexity: Medium
> Theme: Provider validation
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Trouver une API tierce Indeed utilisable pour Scrappy, l'evaluer sur les requetes profil ciblees, puis l'integrer suffisamment pour remplacer le mock/local fixture du connecteur `indeed-api`.
- Valider que l'API choisie fournit assez de champs pour alimenter le modele `Offer`, le scoring, la deduplication inter-source et le XLSX de review.
- Obtenir un run automatique WTTJ + Indeed avec de vraies donnees Indeed, sans import manuel et sans scraping authentifie fragile.

# Context
- Scrappy supporte deja `--provider indeed-api` via un adaptateur HTTP JSON configurable par `SCRAPPY_INDEED_API_URL` et `SCRAPPY_INDEED_API_KEY`.
- Le connecteur actuel est volontairement generique: il sait lire des shapes JSON communes (`jobs`, `results`, `data`, `items`) mais n'est pas encore valide contre une API tierce reelle.
- L'analyse precedente a ecarte le RSS Indeed public pour le profil car il repond `403 Forbidden`; l'API officielle Indeed documentee est surtout orientee publication/ATS/apply et ne couvre pas simplement la recherche candidat locale.
- L'objectif reste la qualite du top, avec requetes ciblees profil, perimetre Paris/full remote/substantial hybrid, fusion des doublons inter-source, et continuation avec warning si un provider echoue.
- L'utilisateur accepte d'analyser une API tierce avec cle; la decision finale doit tenir compte du cout, de la facilite d'obtention d'une cle, des limites d'usage, de la qualite des donnees et des contraintes legales/techniques.

# Acceptance criteria
- AC1: Au moins deux options d'API tierce Indeed sont comparees avec criteres explicites: acces/cle, cout ou free tier, limites de quota, champs disponibles, pagination, fraicheur, pays supportes, risques et effort d'integration.
- AC2: Une option recommandee est choisie ou, si aucune option n'est acceptable, la raison est documentee avec une alternative concrete.
- AC3: Le connecteur `indeed-api` est adapte si necessaire au format de l'API choisie sans casser les tests existants ni le contrat multi-provider.
- AC4: Un smoke run reel avec credentials utilisateur ou environnement local valide la collecte Indeed seule, puis WTTJ + Indeed, et produit un XLSX exploitable.
- AC5: Les offres Indeed collectees alimentent le modele `Offer` avec au minimum titre, entreprise, localisation, URL, type de contrat si disponible, description/snippet et identifiant stable.
- AC6: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint et warning en cas de limite ou erreur API.
- AC7: La documentation indique comment configurer l'API choisie, quelles variables d'environnement sont requises, quelles limites/quota existent, et comment diagnostiquer un echec.
- AC8: Les limites legales/techniques de l'API retenue sont documentees avant tout usage regulier.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Scope
- In:
  - rechercher et comparer des APIs tierces Indeed;
  - choisir une option prioritaire pour validation;
  - obtenir/configurer l'acces via variables d'environnement locales;
  - adapter le mapping JSON Indeed si l'API choisie exige des noms de champs ou headers specifiques;
  - tester le connecteur avec fixture et smoke reel;
  - valider un run multi-provider WTTJ + Indeed;
  - documenter configuration, cout, quota, limites et risques.
- Out:
  - import manuel CSV/XLSX/HTML;
  - scraping direct du site Indeed avec contournement anti-bot;
  - automatisation de compte LinkedIn;
  - garantie d'un volume brut eleve si le fournisseur choisi limite les resultats;
  - changement profond du scoring hors signaux necessaires a Indeed.

# Candidate APIs to investigate
- Apify Indeed API / Indeed scraper actors.
- HasData Indeed Jobs API.
- Browse AI / similar hosted extractor with API/webhook if it exposes structured JSON.
- Oxylabs / ScraperAPI-like services only if they provide a compliant JSON API and acceptable cost/complexity.

# Required validation commands
- `python3 -m pytest`
- `python3 -m scrappy run --provider indeed-api --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-indeed-real.xlsx`
- `python3 -m scrappy run --provider wttj-public --provider indeed-api --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-multi-real.xlsx`
- `logics-manager lint --require-status`
- `logics-manager audit --group-by-doc`
- `logics-manager health`

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- Existing Indeed adapter: `scrappy/connectors/indeed.py`
- Multi-provider CLI: `scrappy/cli.py`
- Provider docs in README: `README.md`
- Prior multi-provider request: `req_003_multi_platform_job_collection`
- Prior multi-provider task: `task_004_etendre_la_collecte_aux_offres_multi_plateformes`

# AI Context
- Summary: Select, integrate and validate a real third-party Indeed API for Scrappy's automatic `indeed-api` provider.
- Keywords: indeed, third-party-api, provider-validation, api-key, smoke-test, multi-provider, json-mapping
- Use when: Evaluating providers, configuring credentials, adapting the Indeed connector or validating real Indeed collection.
- Skip when: Work is only about WTTJ, scoring without provider changes, or manual imports.

# Backlog
- none
- `item_005_selectionner_et_valider_une_api_tierce_indeed`
