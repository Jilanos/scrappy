# Scrappy

Local-first job-offer review assistant.

The MVP goal is to collect configured job offers, store every encountered offer in a local SQLite database, avoid reprocessing unchanged offers, score new offers against a local user profile, and produce an explainable shortlist.

## Current implementation

- Python CLI with no runtime dependency.
- SQLite persistence for runs, offers, source observations and analyses.
- CV-derived profile seed in `examples/profile.yaml`.
- WTTJ public-page connector scaffold.
- Explainable deterministic scoring:
  - mandatory location gate: Paris, full remote, or substantial hybrid remote;
  - skill match;
  - seniority match;
  - internship/apprenticeship exclusion;
  - ESN/consulting downrank;
  - direct military exclusion with adjacent detection/sensing/imaging/security allowed.
- Console output plus XLSX report.
- Rescore command for replaying the whole history after profile/scoring changes.

## Usage

Initialize the local database:

```bash
python3 -m scrappy init-db --db data/scrappy.sqlite
```

Run collection and scoring:

```bash
python3 -m scrappy run \
  --db data/scrappy.sqlite \
  --profile examples/profile.yaml \
  --query "electronics engineer" \
  --max-pages 1 \
  --xlsx reports/top_offers.xlsx
```

Rescore all stored offers:

```bash
python3 -m scrappy rescore \
  --db data/scrappy.sqlite \
  --profile examples/profile.yaml \
  --xlsx reports/top_offers.xlsx
```

## Provider status

The first provider target is Welcome to the Jungle.

Current finding:

- The official WelcomeKit endpoint that lists all jobs requires a dedicated partnership and `su_jobs_r` scope.
- Public WTTJ job pages are accessible without authentication, but the current search page can render without job cards in the initial HTML. The connector is isolated and tested against public job-link markup, but direct discovery may return zero results until a stable public endpoint or third-party API is selected.
- Third-party APIs remain an accepted fallback because no privileged provider credentials are available.

Initial Logics documents:

- `logics/request/req_000_mvp_job_reviewer.md`
- `logics/backlog/item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/product/prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/architecture/adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`

Platform note: LinkedIn, Welcome to the Jungle and Indeed integrations should be implemented as replaceable connectors. The core product should not depend on brittle or non-compliant scraping behavior.
