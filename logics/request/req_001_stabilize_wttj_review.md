## req_001_stabilize_wttj_review - Stabiliser WTTJ Algolia et review manuel XLSX
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 98
> Confidence: 93
> Complexity: Medium
> Theme: Operator workflow
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Stabiliser le provider Welcome to the Jungle via l'endpoint public Algolia afin de collecter un volume utile d'offres en CLI, avec pagination, limites, retry/backoff et filtres initiaux.
- Ajouter un workflow de review manuel base sur le XLSX: l'utilisateur doit pouvoir marquer les offres `selected`, `rejected` ou `maybe`, puis reimporter ces decisions dans SQLite.
- Produire un fichier XLSX oriente tri humain avec au minimum deux onglets: `all_scored` et `rejected`.

# Context
- Le connecteur WTTJ Algolia fonctionne deja en smoke test et remonte des offres depuis l'index `wk_cms_jobs_production`.
- Le prochain palier combine la stabilisation provider et le mode review manuel, sans ajouter de deuxieme provider.
- La collecte doit viser environ 100 offres par run, avec possibilite d'aller au-dela si aucune offre pertinente n'apparait dans le scoring initial.
- Les filtres a appliquer des la collecte ou juste apres normalisation sont: CDI/full-time, Paris, exclusion internship/apprenticeship.
- Les offres hors localisation stricte ou non eligibles doivent etre conservees au debut, avec `eligible=false`, afin d'aider a calibrer le scoring.
- Les requetes initiales derivees du profil sont: `electronics engineer`, `signal processing engineer`, `R&D engineer`, `medical imaging engineer`. `FPGA engineer` est exclu du set initial car trop technique/specialise.
- L'interface reste CLI pour cette tranche.

# Acceptance criteria
- AC1: Une execution WTTJ peut paginer et collecter environ 100 offres, ou davantage lorsque le top pertinent est insuffisant.
- AC2: Les filtres CDI/full-time, Paris et exclusion internship/apprenticeship sont appliques de facon testable et tracable.
- AC3: Les offres non eligibles sont conservees dans la base et dans l'onglet `all_scored`, avec raisons d'ineligibilite visibles.
- AC4: Le XLSX contient au minimum les onglets `all_scored` et `rejected`, avec les colonnes necessaires a la revue manuelle.
- AC5: L'utilisateur peut renseigner une decision `selected`, `rejected` ou `maybe` dans le XLSX, puis la reimporter en base via une commande CLI.
- AC6: La collecte initiale utilise les requetes profil prioritaires sans `FPGA engineer`.
- AC7: Le workflow reste utilisable en CLI sans interface web.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- Previous implementation task: `task_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- WTTJ connector: `scrappy/connectors/wttj.py`
- CLI: `scrappy/cli.py`
- Initial profile: `examples/profile.yaml`

# Acceptance Traceability
- AC1 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; `scrappy/connectors/wttj.py` paginates with `max_pages`, `target_count`, `hits_per_page`; smoke collected 20 WTTJ offers with `--target-offers 20 --max-pages 1`.
- AC2 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; `scrappy/scoring.py` applies CDI/full-time, location and internship/apprenticeship gates; covered by `tests/test_scoring.py`.
- AC3 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; `scrappy/reporting.py` writes all ranked offers to `all_scored` and non-eligible offers to `rejected`; covered by `tests/test_reporting.py`.
- AC4 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; `scrappy/reporting.py` writes `all_scored` and `rejected` sheets with source identifiers and review fields; covered by `tests/test_reporting.py`.
- AC5 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; `scrappy import-reviews` persists `selected`, `maybe`, `rejected` into SQLite; covered by `tests/test_cli.py` and smoke import on `/tmp/scrappy-review.sqlite`.
- AC6 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; `examples/profile.yaml` and `scrappy/cli.py` define default queries without `FPGA engineer`.
- AC7 proof: `task_002_stabiliser_wttj_algolia_et_review_manuel_xlsx` Done; implementation only changes the CLI and introduces no web UI.

# AI Context
- Summary: Stabilize WTTJ Algolia collection and add manual XLSX review decisions in the CLI workflow.
- Keywords: wttj, algolia, pagination, retry, xlsx, manual-review, selected, rejected, maybe, sqlite
- Use when: Implementing or reviewing WTTJ collection quality, XLSX review workflow or manual decision import.
- Skip when: Work concerns adding another provider or generating CV/cover letters.

# Backlog
- none
- `item_002_stabiliser_wttj_algolia_et_review_manuel_xlsx`
