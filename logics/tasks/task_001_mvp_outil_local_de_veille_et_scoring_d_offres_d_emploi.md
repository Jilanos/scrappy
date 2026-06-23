## task_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi - MVP outil local de veille et scoring d'offres d'emploi
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# Definition of Done (DoD)
- [ ] CLI entrypoints for database initialization and run execution are implemented or scaffolded.
- [ ] SQLite schema covers offers, source observations, runs, analysis results and scoring reasons.
- [ ] User profile schema is documented with an example.
- [ ] At least one MVP ingestion path can load offers without relying on authenticated scraping.
- [ ] Deduplication and scoring behavior are covered by focused tests or documented validation steps.
- [ ] Logics validation passes.

# Backlog
- `item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`

# Acceptance criteria
- AC1: Une commande documentee initialise ou migre la base locale.
- AC2: Une commande documentee execute une collecte, ajoute uniquement les offres inconnues ou modifiees, et trace l'execution.
- AC3: Les offres nouvelles sont analysees contre un profil local et stockent score, ecarts, raisons et date d'analyse.
- AC4: Le top de sortie trie les offres par pertinence et affiche les informations necessaires pour decider quoi lire ou postuler.
- AC5: Les connecteurs de source sont decouples du pipeline d'analyse afin d'en ajouter ou remplacer un sans modifier le scoring.
- AC6: Les limites des plateformes et les modes d'entree acceptables sont documentes dans le README ou les specs.

# Validation
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run project tests once the implementation exists.
- Run `logics-manager flow finish task task_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md` after implementation.

# Report
- Initial task created for the MVP implementation slice. Implementation is not started in this commit.

# AI Context
- Summary: Implement the local MVP skeleton for job-offer ingestion, SQLite deduplication, profile scoring and ranked output.
- Keywords: task, implementation, cli, sqlite, profile-schema, source-connectors, scoring
- Use when: Implementing the first runnable local version of the job-offer review assistant.
- Skip when: The work is still product discovery or later document-generation automation.

# Links
- Request: `req_000_mvp_job_reviewer`
- Product brief(s): `prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Architecture decision(s): `adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
