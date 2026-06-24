## item_006_integrer_l_api_offres_d_emploi_france_travail - Integrer l API Offres d emploi France Travail
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 95
> Confidence: 90
> Progress: 0%
> Complexity: Medium
> Theme: Provider expansion
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# Problem
Integrer l'API Offres d'emploi France Travail comme provider gratuit/officiel dans Scrappy afin d'augmenter le pool d'offres France/Paris sans dependance a une API Indeed payante.
Permettre une collecte automatique France Travail via OAuth client credentials, normalisation vers le modele `Offer`, scoring commun, deduplication inter-source et export XLSX.
Valider que cette source apporte des offres pertinentes pour le profil cible, notamment CDI/full-time, Paris, full remote ou hybride substantiel, avec requetes profil ciblees.

# Scope
- In:
  - documenter la creation/configuration d'une application France Travail
  - ajouter un connecteur `FranceTravailConnector`
  - ajouter `france-travail` aux providers CLI
  - implementer OAuth client credentials avec cache memoire simple par execution
  - mapper les resultats d'offres vers `Offer`
  - paginer selon le contrat de l'API
  - ajouter tests fixtures et smoke reel si credentials presents
  - documenter limites et erreurs courantes
- Out:
  - scraping du site France Travail
  - candidature automatique
  - stockage des secrets
  - changement du scoring hors ajustements necessaires aux champs France Travail
  - garantie de volume eleve si les requetes ciblees produisent peu d'offres

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

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: La CLI supporte un provider `france-travail` activable avec `--provider france-travail`, compatible avec les providers existants.
- request-AC2 -> This backlog slice. Proof: AC2: Le connecteur France Travail obtient et utilise un token OAuth depuis des variables d'environnement locales, sans stocker de secret dans le depot.
- request-AC3 -> This backlog slice. Proof: AC3: Les offres France Travail sont mappees vers `Offer` avec au minimum identifiant stable, titre, entreprise, localisation, contrat, description/snippet, URL et champs remote/salaire si disponibles.
- request-AC4 -> This backlog slice. Proof: AC4: La collecte utilise les requetes profil ciblees et le perimetre Paris/full remote/substantial hybrid; les offres hors cible restent visibles avec raisons de rejet/downrank dans le XLSX.
- request-AC5 -> This backlog slice. Proof: AC5: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint, pagination/range utilisee, et warnings API.
- request-AC6 -> This backlog slice. Proof: AC6: La deduplication inter-source fonctionne entre France Travail, WTTJ et futurs providers en conservant les identifiants source.
- request-AC7 -> This backlog slice. Proof: AC7: Un smoke reel France Travail seul produit un XLSX exploitable.
- request-AC8 -> This backlog slice. Proof: AC8: Un smoke reel WTTJ + France Travail produit un XLSX exploitable et continue avec warning si un provider echoue.
- request-AC9 -> This backlog slice. Proof: AC9: La documentation explique comment creer/configurer l'application France Travail, quelles variables d'environnement utiliser, les scopes/API requis, limites connues et commandes de validation.

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
- Request: `logics/request/req_005_integrate_france_travail_jobs_api.md`
- Primary task(s): (none yet)

# AI Context
- Summary: Integrer l API Offres d emploi France Travail
- Keywords: backlog-groom, request, integrer l api offres d emploi france travail, bounded slice
- Use when: Use when implementing or reviewing the delivery slice for Integrer l API Offres d emploi France Travail.
- Skip when: Skip when the change is unrelated to this delivery slice or its linked request.

# Priority
- Impact:
- Source gratuite/officielle pertinente pour la France et Paris; reduit la dependance a Indeed payant et augmente le pool avec une API stable.
- Urgency:
- Prochaine source prioritaire apres le blocage economique autour d'Indeed/Apify.

# Notes
- Hybrid rationale: Derived from request `req_005_integrate_france_travail_jobs_api` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_005_integrate_france_travail_jobs_api.md`.
- Generated locally by logics-manager.

# Tasks
- `task_006_integrer_l_api_offres_d_emploi_france_travail`
