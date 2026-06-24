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

The current providers are Welcome to the Jungle, a configurable Indeed API adapter, and France Travail.

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

Recommended third-party path:

- Apify is the recommended first provider to validate because it offers a documented synchronous API path that runs an Indeed actor and returns dataset items directly.
- Default actor: `misceres~indeed-scraper`, maintained on Apify, with documented input fields `country`, `location`, `position`, `maxItems`, and `saveOnlyUniqueItems`.
- Alternative Apify actor: `borderline~indeed-scraper`, with pay-per-result pricing and a different input shape. Set `SCRAPPY_INDEED_APIFY_ACTOR=borderline~indeed-scraper` to use that payload shape.
- HasData is a credible alternative with normalized Indeed data and a free trial, but its scraper flow is asynchronous and requires job polling, so it is not the first integration target for the local CLI.

Provider comparison:

| Option | Strength | Limitation | Decision |
| --- | --- | --- | --- |
| Apify `misceres~indeed-scraper` | Simple synchronous API, documented `position/location/maxItems` input, JSON dataset output, free account path | Requires Apify token and paid usage beyond trial/free credits | Selected default |
| Apify `borderline~indeed-scraper` | Higher current rating, recent updates, pay-per-result actor, supports `query/country/location/maxRows` | Different actor-specific input shape and higher listed per-1k price | Supported by config |
| HasData Indeed Jobs API | Normalized Indeed data, 60+ locales, documented fields, free trial | Asynchronous job + polling flow, 10 credits per returned row | Fallback candidate |
| Browse AI / Oxylabs style extractors | Hosted extraction, anti-bot handling | More product-specific setup, less direct local CLI fit, potential cost/terms review | Not selected for first validation |

Configure Apify:

```bash
export SCRAPPY_INDEED_PROVIDER="apify"
export SCRAPPY_INDEED_APIFY_TOKEN="apify_api_..."
export SCRAPPY_INDEED_APIFY_ACTOR="misceres~indeed-scraper"
export SCRAPPY_INDEED_COUNTRY="FR"
export SCRAPPY_INDEED_LOCATION="Paris"
```

Smoke Apify Indeed:

```bash
python3 -m scrappy run \
  --provider indeed-api \
  --target-offers 20 \
  --max-pages 2 \
  --xlsx /tmp/scrappy-indeed-real.xlsx
```

Multi-platform deduplication:

- Offers are still stored with their original `source` and `source_id`.
- High-confidence cross-source duplicates are merged by normalized title, company and location.
- `offer_aliases` preserves every source identifier for merged offers.
- The XLSX exposes `merged_sources` and `duplicate_reason`.

France Travail:

- France Travail's official job offers API returns active job offers collected by France Travail or shared by partners that consented to API distribution.
- It is the preferred free official source for France/Paris coverage.
- Access requires an application with OAuth client credentials.
- Default search endpoint: `https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search`
- Fallback historical endpoint supported through configuration: `https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search`

Configure France Travail:

```bash
export SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID="..."
export SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET="..."
export SCRAPPY_FRANCE_TRAVAIL_SCOPE="api_offresdemploiv2 o2dsoffre"
export SCRAPPY_FRANCE_TRAVAIL_LOCATION="75"
export SCRAPPY_FRANCE_TRAVAIL_CONTRACT="CDI"
```

Optional endpoint overrides:

```bash
export SCRAPPY_FRANCE_TRAVAIL_TOKEN_URL="https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
export SCRAPPY_FRANCE_TRAVAIL_SEARCH_URL="https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
```

Smoke France Travail:

```bash
python3 -m scrappy run \
  --provider france-travail \
  --target-offers 20 \
  --max-pages 2 \
  --xlsx /tmp/scrappy-france-travail.xlsx
```

Smoke WTTJ + France Travail:

```bash
python3 -m scrappy run \
  --provider wttj-public \
  --provider france-travail \
  --target-offers 20 \
  --max-pages 2 \
  --xlsx /tmp/scrappy-wttj-france-travail.xlsx
```

Initial Logics documents:

- `logics/request/req_000_mvp_job_reviewer.md`
- `logics/backlog/item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/product/prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- `logics/architecture/adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`

Platform note: LinkedIn, Welcome to the Jungle and Indeed integrations should be implemented as replaceable connectors. The core product should not depend on brittle or non-compliant scraping behavior.
