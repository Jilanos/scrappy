# Scrappy

Local-first job-offer review assistant.

The MVP goal is to collect configured job offers, store every encountered offer in a local SQLite database, avoid reprocessing unchanged offers, score new offers against a local user profile, and produce an explainable shortlist.

## Current implementation

- Python CLI with no runtime dependency.
- SQLite persistence for runs, offers, source observations and analyses.
- CV-derived profile seed in `examples/profile.yaml`.
- WTTJ public Algolia connector.
- Configurable Indeed API connector for automatic third-party or partner API access.
- Explainable deterministic scoring:
  - mandatory location gate: Paris from the normalized location field, explicit full remote, or substantial-remote hybrid;
  - mandatory contract gate: CDI/full-time;
  - mandatory domain primary skill match; Python alone is treated as a support skill;
  - seniority match with roles above 6 years of required experience excluded;
  - internship/apprenticeship exclusion;
  - ESN/consulting downrank;
  - sponsored/promoted, repost and recruitment-agency downrank signals;
  - direct military exclusion with adjacent detection/sensing/imaging/security allowed.
- Console output plus XLSX review workbook with `all_scored` and `rejected` sheets.
- Manual XLSX decision import for `selected`, `maybe`, and `rejected` decisions.
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
  --provider wttj-public \
  --target-offers 300 \
  --max-pages 15 \
  --xlsx reports/top_offers.xlsx
```

Run a multi-provider collection:

```bash
python3 -m scrappy run \
  --db data/scrappy.sqlite \
  --profile examples/profile.yaml \
  --provider wttj-public \
  --provider indeed-api \
  --target-offers 100 \
  --max-pages 5 \
  --xlsx reports/top_offers.xlsx
```

If one provider fails, the run continues with warnings and still writes the report from the successful providers.

The console top only shows eligible offers. The XLSX still keeps every scored offer in `all_scored`, with non-eligible offers also routed to `rejected` for calibration.

Default WTTJ queries are:

- `electronics engineer`
- `signal processing engineer`
- `R&D engineer`
- `medical imaging engineer`

Review the generated XLSX by filling the `decision`, `review_note`, and optionally `reviewed_at` columns in the `all_scored` sheet. Supported decisions are `selected`, `maybe`, and `rejected`.

Import manual decisions:

```bash
python3 -m scrappy import-reviews \
  --db data/scrappy.sqlite \
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

The current providers are Welcome to the Jungle and a configurable Indeed API adapter.

Welcome to the Jungle:

- The official WelcomeKit endpoint that lists all jobs requires a dedicated partnership and `su_jobs_r` scope.
- WTTJ search uses a public Algolia search endpoint behind the website. The connector currently calls:
  - `POST https://csekhvms53-dsn.algolia.net/1/indexes/*/queries`
  - app id: `CSEKHVMS53`
  - index: `wk_cms_jobs_production`
  - public search-only API key from the website bundle
  - required browser-like headers: `Origin`, `Referer`, `X-Algolia-Application-Id`, `X-Algolia-API-Key`
- Third-party APIs remain an accepted fallback because no privileged provider credentials are available.
- Current CLI target is around 300 offers per run, with de-duplication in SQLite by source id and canonical URL.

Indeed:

- The official Indeed partner documentation currently focuses on employer/ATS posting and apply integrations, not a general unauthenticated job-search API for this local candidate workflow.
- The public RSS endpoint was tested for the profile queries and returned `403 Forbidden`, so it is not used as the automatic provider.
- The `indeed-api` provider is therefore implemented as a configurable automatic HTTP JSON adapter. Configure it with:

```bash
export SCRAPPY_INDEED_API_URL="https://provider.example/indeed/jobs"
export SCRAPPY_INDEED_API_KEY="optional-api-key"
export SCRAPPY_INDEED_LOCATION="Paris"
```

The adapter sends common query parameters (`q`, `query`, `l`, `location`, `start`, `page`, `limit`) and accepts common JSON result shapes such as `jobs`, `results`, `data`, or `items`.

Multi-platform deduplication:

- Offers are still stored with their original `source` and `source_id`.
- High-confidence cross-source duplicates are merged by normalized title, company and location.
- `offer_aliases` preserves every source identifier for merged offers.
- The XLSX exposes `merged_sources` and `duplicate_reason`.

Initial Logics documents:

- `logics/request/req_000_mvp_job_reviewer.md`
- `logics/backlog/item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/product/prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/architecture/adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`

Platform note: LinkedIn, Welcome to the Jungle and Indeed integrations should be implemented as replaceable connectors. The core product should not depend on brittle or non-compliant scraping behavior.
