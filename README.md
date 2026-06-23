# Scrappy

Local-first job-offer review assistant.

The MVP goal is to collect configured job offers, store every encountered offer in a local SQLite database, avoid reprocessing unchanged offers, score new offers against a local user profile, and produce an explainable shortlist.

Initial Logics documents:

- `logics/request/req_000_mvp_job_reviewer.md`
- `logics/backlog/item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/product/prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/architecture/adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`

Platform note: LinkedIn, Welcome to the Jungle and Indeed integrations should be implemented as replaceable connectors. The core product should not depend on brittle or non-compliant scraping behavior.
