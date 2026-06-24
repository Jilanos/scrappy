## item_005_selectionner_et_valider_une_api_tierce_indeed - Selectionner et valider une API tierce Indeed
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 94
> Confidence: 86
> Progress: 0%
> Complexity: Medium
> Theme: Provider validation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# Problem
Trouver une API tierce Indeed utilisable pour Scrappy, l'evaluer sur les requetes profil ciblees, puis l'integrer suffisamment pour remplacer le mock/local fixture du connecteur `indeed-api`.
Valider que l'API choisie fournit assez de champs pour alimenter le modele `Offer`, le scoring, la deduplication inter-source et le XLSX de review.
Obtenir un run automatique WTTJ + Indeed avec de vraies donnees Indeed, sans import manuel et sans scraping authentifie fragile.

# Scope
- In:
  - rechercher et comparer des APIs tierces Indeed
  - choisir une option prioritaire pour validation
  - configurer l'acces via variables d'environnement locales
  - adapter le mapping JSON Indeed si necessaire
  - tester le connecteur avec fixture et smoke reel
  - valider un run multi-provider WTTJ + Indeed
  - documenter configuration, cout, quota, limites et risques
- Out:
  - import manuel CSV/XLSX/HTML
  - scraping direct du site Indeed avec contournement anti-bot
  - automatisation LinkedIn
  - garantie d'un volume brut eleve
  - changement profond du scoring hors signaux necessaires a Indeed

# Acceptance criteria
- AC1: Au moins deux options d'API tierce Indeed sont comparees avec criteres explicites: acces/cle, cout ou free tier, limites de quota, champs disponibles, pagination, fraicheur, pays supportes, risques et effort d'integration.
- AC2: Une option recommandee est choisie ou, si aucune option n'est acceptable, la raison est documentee avec une alternative concrete.
- AC3: Le connecteur `indeed-api` est adapte si necessaire au format de l'API choisie sans casser les tests existants ni le contrat multi-provider.
- AC4: Un smoke run reel avec credentials utilisateur ou environnement local valide la collecte Indeed seule, puis WTTJ + Indeed, et produit un XLSX exploitable.
- AC5: Les offres Indeed collectees alimentent le modele `Offer` avec au minimum titre, entreprise, localisation, URL, type de contrat si disponible, description/snippet et identifiant stable.
- AC6: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint et warning en cas de limite ou erreur API.
- AC7: La documentation indique comment configurer l'API choisie, quelles variables d'environnement sont requises, quelles limites/quota existent, et comment diagnostiquer un echec.
- AC8: Les limites legales/techniques de l'API retenue sont documentees avant tout usage regulier.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Au moins deux options d'API tierce Indeed sont comparees avec criteres explicites: acces/cle, cout ou free tier, limites de quota, champs disponibles, pagination, fraicheur, pays supportes, risques et effort d'integration.
- request-AC2 -> This backlog slice. Proof: AC2: Une option recommandee est choisie ou, si aucune option n'est acceptable, la raison est documentee avec une alternative concrete.
- request-AC3 -> This backlog slice. Proof: AC3: Le connecteur `indeed-api` est adapte si necessaire au format de l'API choisie sans casser les tests existants ni le contrat multi-provider.
- request-AC4 -> This backlog slice. Proof: AC4: Un smoke run reel avec credentials utilisateur ou environnement local valide la collecte Indeed seule, puis WTTJ + Indeed, et produit un XLSX exploitable.
- request-AC5 -> This backlog slice. Proof: AC5: Les offres Indeed collectees alimentent le modele `Offer` avec au minimum titre, entreprise, localisation, URL, type de contrat si disponible, description/snippet et identifiant stable.
- request-AC6 -> This backlog slice. Proof: AC6: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint et warning en cas de limite ou erreur API.
- request-AC7 -> This backlog slice. Proof: AC7: La documentation indique comment configurer l'API choisie, quelles variables d'environnement sont requises, quelles limites/quota existent, et comment diagnostiquer un echec.
- request-AC8 -> This backlog slice. Proof: AC8: Les limites legales/techniques de l'API retenue sont documentees avant tout usage regulier.

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
- Request: `logics/request/req_004_validate_third_party_indeed_api.md`
- Primary task(s): (none yet)

# AI Context
- Summary: Selectionner et valider une API tierce Indeed
- Keywords: backlog-groom, request, selectionner et valider une api tierce indeed, bounded slice
- Use when: Use when implementing or reviewing the delivery slice for Selectionner et valider une API tierce Indeed.
- Skip when: Skip when the change is unrelated to this delivery slice or its linked request.

# Priority
- Impact:
- Permet de transformer le connecteur Indeed generique en source reelle et de diversifier le pool au-dela de WTTJ.
- Urgency:
- Suite directe du multi-provider: sans API tierce validee, `indeed-api` reste configure mais non exploitable en production locale.

# Candidate APIs
- Apify Indeed API / Indeed scraper actors
- HasData Indeed Jobs API
- Browse AI ou extracteur similaire avec sortie JSON API/webhook
- Oxylabs / ScraperAPI-like services uniquement si la sortie JSON et les conditions sont acceptables

# Notes
- Hybrid rationale: Derived from request `req_004_validate_third_party_indeed_api` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_004_validate_third_party_indeed_api.md`.
- Generated locally by logics-manager.

# Tasks
- `task_005_selectionner_et_valider_une_api_tierce_indeed`
