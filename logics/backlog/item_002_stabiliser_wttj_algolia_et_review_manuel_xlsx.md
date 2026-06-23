## item_002_stabiliser_wttj_algolia_et_review_manuel_xlsx - Stabiliser WTTJ Algolia et review manuel XLSX
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 98
> Confidence: 92
> Progress: 0
> Complexity: High
> Theme: Operator workflow and runtime integration
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# Problem
Le connecteur WTTJ Algolia est fonctionnel mais encore minimal. Il faut le rendre exploitable pour une vraie session de veille: collecter assez d'offres, filtrer proprement les stages/non-CDI, garder les offres non eligibles pour calibration, produire un XLSX lisible, puis capturer les decisions humaines pour ameliorer le scoring plus tard.

# Scope
- In:
  - Pagination WTTJ Algolia avec limite cible autour de 100 offres par run.
  - Extension possible au-dela de 100 offres lorsque le top pertinent est insuffisant.
  - Retry/backoff et erreurs explicites pour appels Algolia.
  - Requetes initiales: `electronics engineer`, `signal processing engineer`, `R&D engineer`, `medical imaging engineer`.
  - Exclusion du terme `FPGA engineer` du set initial.
  - Filtrage ou marquage CDI/full-time, Paris, internship/apprenticeship.
  - Conservation des offres non eligibles avec `eligible=false` et raisons.
  - XLSX avec onglets `all_scored` et `rejected`.
  - Colonnes de review manuel: `decision`, `review_note`, `reviewed_at`.
  - Commande CLI pour reimporter les decisions XLSX dans SQLite.
  - Stockage des decisions manuelles en base, liees a l'offre et a la version de scoring.
- Out:
  - Ajout d'Indeed ou LinkedIn.
  - Interface web.
  - Generation CV ou lettre.
  - Candidature automatique.
  - Optimisation ML du scoring a partir des decisions; cette tranche collecte seulement les labels.

# Acceptance criteria
- AC1: `scrappy run` peut collecter environ 100 offres WTTJ via pagination Algolia et produire un XLSX.
- AC2: La collecte gere les erreurs transitoires Algolia avec retry/backoff borne et messages utiles.
- AC3: Les requetes par defaut issues du profil excluent `FPGA engineer` et incluent les quatre requetes ciblees.
- AC4: Les stages/apprenticeships sont exclus ou marques rejetes automatiquement avec raison visible.
- AC5: Les offres hors criteres de localisation ou contrat restent dans `all_scored` avec `eligible=false`.
- AC6: Le XLSX contient `all_scored` et `rejected`; `all_scored` inclut `decision`, `review_note`, `eligible`, `score`, `reasons`, `url`.
- AC7: Une commande CLI importe les decisions `selected`, `rejected`, `maybe` depuis le XLSX et les persiste.
- AC8: Le workflow reste CLI only.

# AC Traceability
- request-AC1 -> AC1, AC2. Proof: pagination, target volume and retry are in scope.
- request-AC2 -> AC3, AC4. Proof: source/default filters are explicit and testable.
- request-AC3 -> AC5, AC6. Proof: ineligible offers stay visible in `all_scored`.
- request-AC4 -> AC6. Proof: XLSX sheet structure is explicit.
- request-AC5 -> AC7. Proof: manual decisions are imported into SQLite.
- request-AC6 -> AC3. Proof: query set is specified.
- request-AC7 -> AC8. Proof: CLI-only workflow is explicit.

# Decision framing
- Product framing: Needed, because this changes the review workflow from passive output to human-in-the-loop labeling.
- Product signals: WTTJ stabilization, manual review, all_scored/rejected sheets, future scoring calibration.
- Product follow-up: Use imported decisions later to tune scoring and thresholds.
- Architecture framing: Needed, because XLSX import requires durable decision storage and schema changes.
- Architecture signals: SQLite decision table, XLSX parser/writer, retry/backoff, provider pagination.
- Architecture follow-up: Revisit after the first manually reviewed batch.

# Links
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
- Request: `logics/request/req_001_stabilize_wttj_review.md`
- Primary task(s): (none yet)

# AI Context
- Summary: Stabilize WTTJ Algolia collection and add CLI/XLSX manual review import for selected/rejected/maybe decisions.
- Keywords: wttj, algolia, pagination, retry, xlsx, review-import, sqlite, selected, rejected, maybe
- Use when: Implementing pagination, provider reliability, XLSX sheet structure or manual review persistence.
- Skip when: Adding new providers, web UI, CV generation or model-based scoring optimization.

# Priority
- Impact: High, because manual decisions create the feedback loop needed to improve scoring.
- Urgency: High, because WTTJ is the first real provider and must be reliable before adding others.

# Notes
- Hybrid rationale: Derived from request `req_001_stabilize_wttj_review` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_001_stabilize_wttj_review.md`.
- Generated locally by logics-manager, then refined with user decisions from the WTTJ stabilization planning.

# Tasks
- `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx`
