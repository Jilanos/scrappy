## req_003_multi_platform_job_collection - Etendre la collecte aux offres multi-plateformes
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 96
> Confidence: 88
> Complexity: Medium
> Theme: Provider expansion
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Etendre l'outil Scrappy pour mixer les offres issues de plusieurs plateformes dans un meme pool local deduplique, score et exporte.
- Ajouter au moins un second provider utilisable a cote de Welcome to the Jungle, en priorisant Indeed pour la prochaine analyse d'acces.
- Conserver une experience CLI simple: une execution doit pouvoir collecter depuis plusieurs sources configurees, enregistrer chaque observation, dedupliquer les annonces equivalentes et produire le meme XLSX de review.
- Rendre visible la contribution de chaque plateforme au pool: hits bruts, offres uniques, doublons, erreurs provider et limites de capacite.

# Context
- Le provider WTTJ Algolia fonctionne deja, mais les requetes profil actuelles plafonnent autour de 140 offres uniques sur 5 pages. Le volume et la diversite doivent maintenant venir de sources complementaires.
- Le coeur existant couvre deja SQLite, runs, offers, source observations, analyses, scoring, XLSX et import de decisions manuelles.
- La prochaine tranche doit eviter de coupler le scoring aux specificites d'une plateforme: chaque provider doit normaliser ses resultats vers le modele `Offer` existant ou son evolution minimale.
- LinkedIn et Indeed ont des surfaces web sensibles au scraping, susceptibles de bloquer l'automatisation ou d'enfreindre leurs conditions. Le mode d'entree cible est automatique uniquement; l'import manuel n'est pas accepte pour cette tranche.
- Le multi-plateforme doit gerer les doublons entre sources: meme annonce vue sur WTTJ et Indeed/LinkedIn, URLs differentes, titre/entreprise/localisation proches.
- La sortie doit rester actionnable: le top ne doit pas etre domine par des doublons ni masquer la source qui a fourni l'offre.
- L'objectif prioritaire est la qualite du top, pas le volume brut. Les requetes doivent rester ciblees profil, meme si cela limite le nombre d'offres collectees.
- Le perimetre geographique reste celui du MVP actuel: Paris intramuros, full remote, ou hybride avec remote substantiel.
- Les annonces sponsorisees, cabinets de recrutement et reposts doivent etre signales et downrankes plutot qu'exclus automatiquement.

# Acceptance criteria
- AC1: La CLI permet de lancer une collecte multi-source explicite, par exemple WTTJ plus Indeed si l'analyse d'acces le confirme, avec options documentees pour selectionner les providers actifs.
- AC2: Le second provider implemente une strategie d'acces automatique stable et documentee, sans import manuel et sans dependance obligatoire a un scraping authentifie fragile.
- AC3: Chaque provider expose des statistiques de run homogenes: hits bruts, offres normalisees, offres uniques, doublons intra/inter-source, erreurs et raison d'arret lorsque le target n'est pas atteint.
- AC4: La base locale conserve la provenance source et permet de relier des annonces equivalentes vues sur plusieurs plateformes sans perdre les identifiants source originaux.
- AC5: Le scoring et le XLSX restent communs a toutes les sources; le XLSX permet de filtrer par source et de voir si une offre a ete observee sur plusieurs plateformes.
- AC6: Les doublons probables entre plateformes sont fusionnes automatiquement lorsque le niveau de confiance est suffisant, avec conservation des identifiants source et d'une raison de similarite lisible.
- AC7: Le comportement en cas d'echec partiel d'un provider est robuste: les autres providers continuent, le run est trace, et l'utilisateur voit quelles sources ont echoue avec warning.
- AC8: Les limites legales/techniques de LinkedIn, Indeed et du provider choisi sont documentees dans le README ou une spec Logics avant implementation complete.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Scope
- In:
  - analyser et choisir un mode d'entree automatique pour Indeed en priorite, LinkedIn en alternative;
  - ajouter une orchestration multi-provider dans la CLI;
  - ajouter les statistiques provider homogenes;
  - ajouter une strategie de fusion des doublons inter-source;
  - adapter le XLSX pour rendre source, fusion et signaux de downrank visibles;
  - downranker et signaler les annonces sponsorisees, cabinets de recrutement et reposts.
- Out:
  - generation de CV et lettre de motivation;
  - interface web;
  - import manuel CSV/XLSX/HTML comme mode provider principal;
  - automatisation d'un compte LinkedIn connecte sans validation explicite;
  - contournement de protections anti-bot ou scraping agressif;
  - garantie d'atteindre 1000 offres si les sources configurees ne les exposent pas.

# Decisions
- D1: Provider prioritaire: Indeed. LinkedIn reste une alternative si Indeed n'offre pas de voie automatique raisonnable.
- D2: Mode d'entree: automatique uniquement. Pas d'import manuel comme solution MVP pour cette tranche.
- D3: Objectif: qualite du top plutot que volume brut.
- D4: Requetes: rester ciblees sur le profil, pas d'elargissement massif pour gonfler le volume.
- D5: Deduplication: fusionner automatiquement les doublons inter-source lorsque la confiance est suffisante.
- D6: Cabinets de recrutement, sponsorises et reposts: downranker et signaler, ne pas exclure par defaut.
- D7: Geographie: conserver le perimetre actuel, Paris/full remote/substantial hybrid.
- D8: Echec partiel: continuer avec warnings et tracer l'echec provider.

# To analyze
- TA1: Determiner la voie d'acces automatique la plus stable pour Indeed, puis LinkedIn si Indeed n'est pas praticable: API officielle/partenaire, endpoint public raisonnable, service tiers avec cle, ou autre option conforme. L'usage d'une API tierce payante ou avec cle reste a analyser avant decision.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- Existing WTTJ provider: `scrappy/connectors/wttj.py`
- Current CLI orchestration: `scrappy/cli.py`
- Current storage schema: `scrappy/storage.py`
- Current XLSX reporting: `scrappy/reporting.py`
- WTTJ stabilization request: `req_001_stabilize_wttj_review`
- WTTJ collection diagnostics request: `req_002_diagnose_wttj_collection_limit`

# AI Context
- Summary: Extend Scrappy from one WTTJ provider to a multi-platform offer pool with Indeed or LinkedIn as the next source.
- Keywords: multi-provider, indeed, linkedin, wttj, deduplication, provider-stats, source-normalization, xlsx-review
- Use when: Planning or implementing the next ingestion slice after WTTJ.
- Skip when: Work is only about scoring changes, CV generation, or WTTJ-only diagnostics.

# Backlog
- none
- `item_004_etendre_la_collecte_aux_offres_multi_plateformes`
