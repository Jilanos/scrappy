## req_002_diagnose_wttj_collection_limit - Diagnostiquer la limite de collecte WTTJ
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 98
> Confidence: 94
> Complexity: Low
> Theme: Provider diagnostics
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Explain why `scrappy run --target-offers 1000 --max-pages 5` only discovers around 140 WTTJ offers with the current default query set.
- Make the CLI report provider-side result capacity, raw hits and deduplication so the operator can tell whether the limiting factor is `target`, `max-pages`, query breadth, or provider availability.

# Context
- The observed command discovered 140 unique offers, with 83 new or changed, while the previous run discovered 109.
- WTTJ Algolia reports only 146 raw hits total across the default queries with the current parameters: `electronics engineer`, `signal processing engineer`, `R&D engineer`, `medical imaging engineer`.
- The current top can remain identical across runs because the report ranks latest analyses across the stored database; newly discovered offers only change the top if they score higher than stored offers.
- Increasing `--target-offers` alone cannot exceed provider/query capacity.

# Acceptance criteria
- AC1: The CLI explains when the requested target is not reached and includes target, unique discovered count, `max_pages` and `hits_per_page`.
- AC2: The CLI reports raw provider hits and duplicate hits removed during WTTJ discovery.
- AC3: The CLI reports per-query capacity using Algolia metadata (`nbHits`, `nbPages`) so low-volume queries are visible.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- User run: `python3 -m scrappy run --target-offers 1000 --max-pages 5 --xlsx reports/top_offers.xlsx`
- Connector: `scrappy/connectors/wttj.py`
- CLI: `scrappy/cli.py`

# AI Context
- Summary: Diagnose and expose WTTJ collection capacity limits in CLI output.
- Keywords: wttj, algolia, target-offers, max-pages, nbHits, nbPages, deduplication
- Use when: Investigating why WTTJ discovery returns fewer offers than requested.
- Skip when: Work concerns scoring quality or adding another provider.

# Backlog
- none
- `item_003_diagnostiquer_la_limite_de_collecte_wttj`
