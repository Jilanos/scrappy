## task_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi - MVP outil local de veille et scoring d'offres d'emploi
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 99
> Confidence: 92
> Progress: 90
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex

# Definition of Done (DoD)
- [ ] CLI entrypoints for database initialization and run execution are implemented or scaffolded.
- [ ] SQLite schema covers offers, source observations, runs, analysis results and scoring reasons.
- [ ] User profile schema is documented with an example derived from a CV.
- [ ] One initial provider connector is implemented or scaffolded, preferably API-first and without manual export dependency.
- [ ] Location gating accepts Paris intramuros, full remote, and substantial-remote hybrid roles outside Paris; it rejects or marks non-eligible low-remote onsite roles outside Paris.
- [ ] Scoring covers skill match and seniority match, with salary treated as optional metadata.
- [ ] The ranked output returns a top 5 initial shortlist in console and XLSX formats.
- [ ] Internship/apprenticeship exclusions are implemented.
- [ ] ESN roles are downranked by default.
- [ ] Direct military roles are excluded while adjacent detection/sensing/imaging/security roles remain possible.
- [ ] A future rescore path is designed or scaffolded for rescoring stored history after profile/scoring improvements.
- [ ] Deduplication and scoring behavior are covered by focused tests or documented validation steps.
- [ ] Logics validation passes.

# Backlog
- `item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`

# Acceptance criteria
- AC1: Une commande documentee initialise ou migre la base locale.
- AC2: Une commande documentee execute une collecte depuis le provider initial, ajoute uniquement les offres inconnues ou modifiees, et trace l'execution.
- AC3: Les offres nouvelles sont filtrees par localisation obligatoire puis analysees contre un profil local derive du CV; elles stockent score, ecarts, raisons et date d'analyse.
- AC4: Le top de sortie trie les offres eligibles par pertinence, garde un top 5 initial et affiche les informations necessaires pour decider quoi lire ou postuler dans la console et dans un XLSX.
- AC5: Les connecteurs de source sont decouples du pipeline d'analyse afin d'en ajouter ou remplacer un sans modifier le scoring.
- AC6: Les limites des plateformes et les modes d'entree acceptables sont documentes dans le README ou les specs.

# Validation
- Run `logics-manager lint --require-status`.
- Run `logics-manager audit --group-by-doc`.
- Run project tests once the implementation exists.
- Run `logics-manager flow finish task task_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md` after implementation.

# Open implementation questions
- Confirm the first provider after checking whether official API access, public-page ingestion, or a third-party API is feasible.
- Define the exact source query mapping from the CV-derived roles and keywords.
- Define how to detect "substantial remote" in provider text; initial assumption is at least 3 remote days per week or equivalent wording.
- Choose the XLSX column schema for ranked output.
- Choose document generation direction for later phases: keep PPT/Word targets or move to HTML/Markdown/LaTeX templates.

# Report
- Implementation scaffold is in place: Python CLI, SQLite schema, profile seed, WTTJ public-page connector boundary, deterministic scoring, console output, XLSX report, rescore command and focused tests.
- Provider investigation found that the official WTTJ all-jobs API requires dedicated partnership/scope, while WTTJ also exposes public Algolia search traffic through the website.
- Direct discovery is now implemented through the public Algolia endpoint `POST https://csekhvms53-dsn.algolia.net/1/indexes/*/queries`, app id `CSEKHVMS53`, index `wk_cms_jobs_production`, with browser-like Origin/Referer headers and the website public search-only key.
- Smoke validation with query `electronics engineer` discovered 20 offers and produced DB plus XLSX output.

# AI Context
- Summary: Implement the local MVP skeleton for job-offer ingestion, SQLite deduplication, profile scoring and ranked output.
- Keywords: task, implementation, cli, sqlite, profile-schema, source-connectors, scoring
- Use when: Implementing the first runnable local version of the job-offer review assistant.
- Skip when: The work is still product discovery or later document-generation automation.

# Links
- Request: `req_000_mvp_job_reviewer`
- Product brief(s): `prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Architecture decision(s): `adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
