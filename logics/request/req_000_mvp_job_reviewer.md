## req_000_mvp_job_reviewer - MVP outil local de veille et scoring d'offres d'emploi
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: Medium
> Theme: Operator workflow
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Mettre en place un MVP local qui collecte des offres d'emploi depuis des sources configurees, detecte les offres deja rencontrees, analyse uniquement les nouvelles offres contre le profil utilisateur, puis restitue un classement des opportunites les plus pertinentes.
- Construire la base de donnees et le modele de donnees de facon a preparer une phase ulterieure de generation de CV et lettres de motivation adaptes.

# Context
- Les sources cibles sont LinkedIn, Welcome to the Jungle et Indeed, avec une approche prudente: le MVP doit privilegier les entrees configurees, les exports, les pages publiques ou les flux autorises plutot qu'un scraping agressif fragile.
- L'outil tourne localement et uniquement a la demande de l'utilisateur.
- La base locale conserve l'historique des offres vues pour eviter de retraiter les memes annonces lors des executions suivantes.
- Le profil utilisateur doit etre declaratif et versionnable, par exemple dans un fichier local, afin de pouvoir ajuster les competences, niveaux, envies, contraintes et mots-cles sans modifier le code.
- Le scoring doit expliquer pourquoi une offre est proche ou eloignee du profil, pas seulement fournir une note opaque.

# Acceptance criteria
- AC1: Une execution locale peut ingerer une liste d'offres nouvelles depuis au moins une source configuree et les enregistrer dans une base SQLite.
- AC2: Une offre deja rencontree est reconnue et n'est pas analysee une seconde fois, sauf si son contenu source a change.
- AC3: Chaque nouvelle offre analysee recoit un score de pertinence, un niveau d'ecart au profil et des raisons lisibles.
- AC4: La sortie presente un top des offres avec titre, entreprise, source, URL, score, points forts, ecarts et prochaine action recommandee.
- AC5: Le MVP documente clairement les limites d'integration avec LinkedIn, Welcome to the Jungle et Indeed, et isole les connecteurs pour pouvoir les remplacer.
- AC6: La generation automatique de CV et lettre de motivation est hors MVP, mais les donnees stockees conservent les elements necessaires pour cette phase.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Architecture decision(s): `adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`

# References
- Product brief: `logics/product/prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- Architecture decision: `logics/architecture/adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- Backlog slice: `logics/backlog/item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`

# AI Context
- Summary: MVP local pour collecter des offres d'emploi, dedupliquer les annonces vues, scorer les nouvelles offres contre un profil utilisateur et proposer un top exploitable.
- Keywords: job-search, local-cli, sqlite, scoring, deduplication, linkedin, welcome-to-the-jungle, indeed, profile-match
- Use when: You need context for the first implementation slice of the job-offer review assistant.
- Skip when: The work concerns later CV or cover-letter generation without touching ingestion, storage, or scoring.

# Backlog
- none
- `item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
