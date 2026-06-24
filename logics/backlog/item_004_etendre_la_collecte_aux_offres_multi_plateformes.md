## item_004_etendre_la_collecte_aux_offres_multi_plateformes - Etendre la collecte aux offres multi-plateformes
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 96
> Confidence: 88
> Progress: 100%
> Complexity: High
> Theme: Operator workflow and runtime integration
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# Problem
Etendre l'outil Scrappy pour mixer les offres issues de plusieurs plateformes dans un meme pool local deduplique, score et exporte.
Ajouter au moins un second provider utilisable a cote de Welcome to the Jungle, en priorisant Indeed et en gardant LinkedIn comme alternative si Indeed n'offre pas de voie automatique raisonnable.
Conserver une experience CLI simple: une execution doit pouvoir collecter depuis plusieurs sources configurees, enregistrer chaque observation, dedupliquer les annonces equivalentes et produire le meme XLSX de review.
Rendre visible la contribution de chaque plateforme au pool: hits bruts, offres uniques, doublons, erreurs provider et limites de capacite.

# Scope
- In:
  - analyser et choisir un mode d'entree automatique pour Indeed en priorite
  - ajouter une orchestration multi-provider dans la CLI
  - ajouter des statistiques provider homogenes
  - ajouter une strategie de fusion des doublons inter-source
  - adapter le XLSX pour rendre source, fusion et signaux de downrank visibles
  - downranker et signaler sponsorises, cabinets de recrutement et reposts
- Out:
  - generation de CV et lettre de motivation
  - interface web
  - import manuel CSV/XLSX/HTML comme mode provider principal
  - automatisation LinkedIn authentifiee sans validation explicite
  - contournement anti-bot ou scraping agressif
  - garantie d'atteindre 1000 offres si les providers configures ne les exposent pas

# Acceptance criteria
- AC1: La CLI permet de lancer une collecte multi-source explicite, par exemple WTTJ plus Indeed si l'analyse d'acces le confirme, avec options documentees pour selectionner les providers actifs.
- AC2: Le second provider implemente une strategie d'acces automatique stable et documentee, sans import manuel et sans dependance obligatoire a un scraping authentifie fragile.
- AC3: Chaque provider expose des statistiques de run homogenes: hits bruts, offres normalisees, offres uniques, doublons intra/inter-source, erreurs et raison d'arret lorsque le target n'est pas atteint.
- AC4: La base locale conserve la provenance source et permet de relier des annonces equivalentes vues sur plusieurs plateformes sans perdre les identifiants source originaux.
- AC5: Le scoring et le XLSX restent communs a toutes les sources; le XLSX permet de filtrer par source et de voir si une offre a ete observee sur plusieurs plateformes.
- AC6: Les doublons probables entre plateformes sont fusionnes automatiquement lorsque le niveau de confiance est suffisant, avec conservation des identifiants source et d'une raison de similarite lisible.
- AC7: Le comportement en cas d'echec partiel d'un provider est robuste: les autres providers continuent, le run est trace, et l'utilisateur voit quelles sources ont echoue avec warning.
- AC8: Les limites legales/techniques de LinkedIn, Indeed et du provider choisi sont documentees dans le README ou une spec Logics avant implementation complete.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: La CLI permet de lancer une collecte multi-source explicite, par exemple WTTJ plus un second provider, avec options documentees pour selectionner les providers actifs.
- request-AC2 -> This backlog slice. Proof: AC2: Le second provider implemente une strategie d'acces stable et documentee, sans dependance obligatoire a un scraping authentifie fragile.
- request-AC3 -> This backlog slice. Proof: AC3: Chaque provider expose des statistiques de run homogenes: hits bruts, offres normalisees, offres uniques, doublons intra/inter-source, erreurs et raison d'arret lorsque le target n'est pas atteint.
- request-AC4 -> This backlog slice. Proof: AC4: La base locale conserve la provenance source et permet de relier des annonces equivalentes vues sur plusieurs plateformes sans perdre les identifiants source originaux.
- request-AC5 -> This backlog slice. Proof: AC5: Le scoring et le XLSX restent communs a toutes les sources; le XLSX permet de filtrer par source et de voir si une offre a ete observee sur plusieurs plateformes.
- request-AC6 -> This backlog slice. Proof: AC6: Les doublons probables entre plateformes sont soit fusionnes, soit signales avec une raison de similarite lisible avant affichage du top.
- request-AC7 -> This backlog slice. Proof: AC7: Le comportement en cas d'echec partiel d'un provider est robuste: les autres providers continuent, le run est trace, et l'utilisateur voit quelles sources ont echoue.
- request-AC8 -> This backlog slice. Proof: AC8: Les limites legales/techniques de LinkedIn, Indeed et du provider choisi sont documentees dans le README ou une spec Logics avant implementation complete.

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
- Request: `logics/request/req_003_multi_platform_job_collection.md`
- Primary task(s): (none yet)

# AI Context
- Summary: Etendre la collecte aux offres multi-plateformes
- Keywords: backlog-groom, request, etendre la collecte aux offres multi-plateformes, bounded slice
- Use when: Use when implementing or reviewing the delivery slice for Etendre la collecte aux offres multi-plateformes.
- Skip when: Skip when the change is unrelated to this delivery slice or its linked request.

# Priority
- Impact:
- Elargit le pool au-dela de WTTJ et rend la shortlist moins dependante de la capacite d'un seul provider.
- Urgency:
- Prochaine tranche logique apres l'investigation de volume WTTJ.

# Decisions
- Provider prioritaire: Indeed; LinkedIn reste l'alternative.
- Mode d'entree: automatique uniquement, pas d'import manuel.
- Objectif: qualite du top plutot que volume brut.
- Requetes: ciblees profil.
- Doublons inter-source: fusion automatique lorsque la confiance est suffisante.
- Sponsorises, cabinets de recrutement et reposts: downrank et signalement.
- Geographie: Paris/full remote/substantial hybrid.
- Echec provider: continuer avec warning.
- A analyser: voie d'acces automatique Indeed/LinkedIn et opportunite d'une API tierce avec cle.

# Notes
- Hybrid rationale: Derived from request `req_003_multi_platform_job_collection` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_003_multi_platform_job_collection.md`.
- Generated locally by logics-manager.
- Task `task_004_etendre_la_collecte_aux_offres_multi_plateformes` was finished via `logics-manager flow finish task` on 2026-06-24.

# Tasks
- `task_004_etendre_la_collecte_aux_offres_multi_plateformes`
