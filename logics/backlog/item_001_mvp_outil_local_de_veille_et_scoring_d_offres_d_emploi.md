## item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi - MVP outil local de veille et scoring d'offres d'emploi
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Operator workflow and runtime integration
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# Problem
Les recherches d'emploi sur plusieurs plateformes produisent beaucoup d'offres redondantes et difficiles a comparer. Le MVP doit fournir un outil local qui, a chaque lancement, recupere les offres configurees, ignore ce qui a deja ete traite, analyse les nouvelles annonces par rapport au profil utilisateur, puis propose un top argumente.

# Scope
- In:
  - CLI locale lancee a la demande.
  - Base SQLite pour offres, sources, executions, analyses et scores.
  - Profil utilisateur declaratif dans un fichier local.
  - Connecteurs isoles pour sources d'offres, avec au moins un connecteur simple utilisable en MVP.
  - Deduplication par URL canonique, identifiant source quand disponible et empreinte de contenu.
  - Scoring interpretable: correspondances, ecarts, signaux positifs et risques.
  - Sortie console ou fichier lisible presentant le top des nouvelles offres analysees.
- Out:
  - Connexion automatisee a des comptes personnels LinkedIn, Welcome to the Jungle ou Indeed.
  - Contournement de protections anti-bot, captchas ou limitations de plateformes.
  - Generation automatique de CV ou lettre de motivation.
  - Interface web ou app desktop.
  - Envoi automatique de candidatures.

# Acceptance criteria
- AC1: Une commande documentee initialise ou migre la base locale.
- AC2: Une commande documentee execute une collecte, ajoute uniquement les offres inconnues ou modifiees, et trace l'execution.
- AC3: Les offres nouvelles sont analysees contre un profil local et stockent score, ecarts, raisons et date d'analyse.
- AC4: Le top de sortie trie les offres par pertinence et affiche les informations necessaires pour decider quoi lire ou postuler.
- AC5: Les connecteurs de source sont decouples du pipeline d'analyse afin d'en ajouter ou remplacer un sans modifier le scoring.
- AC6: Les limites des plateformes et les modes d'entree acceptables sont documentes dans le README ou les specs.

# AC Traceability
- request-AC1 -> AC1, AC2. Proof: local ingestion and SQLite persistence are in scope.
- request-AC2 -> AC2. Proof: deduplication and content-change detection are explicit.
- request-AC3 -> AC3, AC4. Proof: scoring, gap classification and readable reasons are explicit.
- request-AC4 -> AC4. Proof: ranked output includes title, company, source, URL and reasons.
- request-AC5 -> AC5, AC6. Proof: connector isolation and platform limits are explicit.
- request-AC6 -> AC1, AC3. Proof: persisted analyses prepare later document generation.

# Decision framing
- Product framing: Needed to keep the MVP focused on decision support rather than application automation.
- Product signals: local-first, explainable ranking, repeatable runs, future document generation.
- Product follow-up: Keep the product brief updated when source strategy or scoring UX changes.
- Architecture framing: Needed because source ingestion is fragile and must be isolated from storage and scoring.
- Architecture signals: SQLite, connector interface, content fingerprints, deterministic scoring baseline.
- Architecture follow-up: Revisit once a browser-assisted or API-backed connector is selected.

# Links
- Product brief(s): `prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Architecture decision(s): `adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Request: `logics/request/req_000_mvp_job_reviewer.md`
- Primary task(s): (none yet)

# AI Context
- Summary: First implementation slice for a local job-offer review tool with source ingestion, SQLite deduplication, profile-based scoring and ranked output.
- Keywords: mvp, job-offer-ingestion, sqlite, local-run, profile-scoring, dedupe, connectors
- Use when: Implementing or reviewing the local ingestion, storage, scoring, or ranked-output workflow.
- Skip when: Work is limited to later CV/cover-letter generation or unrelated workflow tooling.

# Priority
- Impact: High, because it reduces repeated manual review and makes job search decisions comparable.
- Urgency: Medium, suitable as the first product slice before document-generation automation.

# Notes
- Hybrid rationale: Derived from request `req_000_mvp_job_reviewer` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_000_mvp_job_reviewer.md`.
- Generated locally by logics-manager, then refined for the job-search MVP.

# Tasks
- `task_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
