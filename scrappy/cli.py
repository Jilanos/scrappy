from __future__ import annotations

import argparse
from pathlib import Path

from scrappy.connectors import FranceTravailConnector, IndeedApiConnector, WttjPublicConnector
from scrappy.connectors.base import DiscoveryResult
from scrappy.models import RankedOffer
from scrappy.profile import load_profile, profile_terms
from scrappy.reporting import print_console, read_review_rows, write_xlsx
from scrappy.scoring import score_offer
from scrappy.storage import (
    connect,
    create_run,
    finish_run,
    init_db,
    iter_offers,
    latest_ranked,
    save_manual_review,
    save_analysis,
    upsert_offer,
)


DEFAULT_DB = "data/scrappy.sqlite"
DEFAULT_PROFILE = "examples/profile.yaml"
DEFAULT_REPORT = "reports/top_offers.xlsx"
DEFAULT_QUERIES = [
    "electronics engineer",
    "signal processing engineer",
    "R&D engineer",
    "medical imaging engineer",
]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="scrappy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help="Initialize or migrate the local SQLite database.")
    init_parser.add_argument("--db", default=DEFAULT_DB)

    run_parser = subparsers.add_parser("run", help="Collect, score, persist, and export a top shortlist.")
    run_parser.add_argument("--db", default=DEFAULT_DB)
    run_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    run_parser.add_argument(
        "--provider",
        action="append",
        choices=["wttj-public", "indeed-api", "france-travail"],
        help="Provider to collect from. Repeat for multi-platform runs. Defaults to wttj-public.",
    )
    run_parser.add_argument("--query", action="append", help="Override profile search query. Repeatable.")
    run_parser.add_argument("--max-pages", type=int, default=15)
    run_parser.add_argument("--target-offers", type=int, default=300)
    run_parser.add_argument("--hits-per-page", type=int, default=20)
    run_parser.add_argument("--top", type=int, default=5)
    run_parser.add_argument("--xlsx", default=DEFAULT_REPORT)

    rescore_parser = subparsers.add_parser("rescore", help="Rescore all stored offers with the current profile.")
    rescore_parser.add_argument("--db", default=DEFAULT_DB)
    rescore_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    rescore_parser.add_argument("--top", type=int, default=5)
    rescore_parser.add_argument("--xlsx", default=DEFAULT_REPORT)

    import_parser = subparsers.add_parser("import-reviews", help="Import manual XLSX review decisions.")
    import_parser.add_argument("--db", default=DEFAULT_DB)
    import_parser.add_argument("--xlsx", default=DEFAULT_REPORT)
    import_parser.add_argument("--sheet", default="all_scored")

    args = parser.parse_args(argv)
    if args.command == "init-db":
        _init_db(args.db)
    elif args.command == "run":
        _run(args)
    elif args.command == "rescore":
        _rescore(args)
    elif args.command == "import-reviews":
        _import_reviews(args)


def _init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        init_db(conn)
    print(f"Initialized database: {db_path}")


def _run(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    queries = args.query or _default_queries(profile)
    connectors = [_connector(provider) for provider in (args.provider or ["wttj-public"])]

    with connect(args.db) as conn:
        init_db(conn)
        discoveries: list[DiscoveryResult] = []
        total_changed = 0
        for connector in connectors:
            run_id = create_run(conn, connector.name, len(queries))
            try:
                discovery = connector.discover_with_stats(
                    queries,
                    max_pages=args.max_pages,
                    target_count=args.target_offers,
                    hits_per_page=args.hits_per_page,
                )
            except RuntimeError as error:
                finish_run(conn, run_id, discovered=0, changed=0, status="failed")
                discoveries.append(
                    DiscoveryResult(
                        provider=connector.name,
                        offers=[],
                        pages=[],
                        raw_hits=0,
                        duplicate_hits=0,
                        target_reached=False,
                        error=str(error),
                    )
                )
                continue

            changed_count = 0
            for offer in discovery.offers:
                offer_id, changed = upsert_offer(conn, run_id, offer)
                if changed:
                    changed_count += 1
                    save_analysis(conn, run_id, offer_id, _profile_version(profile), score_offer(offer, profile))
            finish_run(conn, run_id, discovered=len(discovery.offers), changed=changed_count)
            total_changed += changed_count
            discoveries.append(discovery)
        ranked = latest_ranked(conn, limit=None)

    for discovery in discoveries:
        print(f"Provider: {discovery.provider}")
        if discovery.error:
            print(f"Warning: provider failed: {discovery.error}")
            continue
        print(f"Discovered: {len(discovery.offers)}")
        _print_discovery_diagnostics(discovery, args.target_offers, args.max_pages, args.hits_per_page)
    print(f"New or changed: {total_changed}")
    _print_top_eligible(ranked, args.top)
    write_xlsx(args.xlsx, ranked)
    print(f"XLSX report: {args.xlsx}")


def _rescore(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    with connect(args.db) as conn:
        init_db(conn)
        run_id = create_run(conn, "rescore", 0)
        count = 0
        for offer_id, offer in iter_offers(conn):
            save_analysis(conn, run_id, offer_id, _profile_version(profile), score_offer(offer, profile))
            count += 1
        finish_run(conn, run_id, discovered=count, changed=count)
        ranked = latest_ranked(conn, limit=None)
    print(f"Rescored offers: {count}")
    _print_top_eligible(ranked, args.top)
    write_xlsx(args.xlsx, ranked)
    print(f"XLSX report: {args.xlsx}")


def _import_reviews(args: argparse.Namespace) -> None:
    rows = read_review_rows(args.xlsx, sheet_name=args.sheet)
    imported = 0
    skipped_empty = 0
    skipped_missing = 0
    with connect(args.db) as conn:
        init_db(conn)
        for row in rows:
            decision = row.get("decision", "").strip().lower()
            if not decision:
                skipped_empty += 1
                continue
            source = row.get("source", "").strip()
            source_id = row.get("source_id", "").strip()
            if not source or not source_id:
                skipped_missing += 1
                continue
            saved = save_manual_review(
                conn,
                source=source,
                source_id=source_id,
                decision=decision,
                review_note=row.get("review_note", ""),
                reviewed_at=row.get("reviewed_at", ""),
            )
            if saved:
                imported += 1
            else:
                skipped_missing += 1
    print(f"Imported reviews: {imported}")
    print(f"Skipped empty decisions: {skipped_empty}")
    print(f"Skipped missing offers: {skipped_missing}")


def _profile_version(profile: dict) -> str:
    return str(profile.get("version") or "unversioned")


def _print_top_eligible(ranked: list[RankedOffer], top: int) -> None:
    eligible = [item for item in ranked if item.score.eligible]
    print(f"Eligible offers: {len(eligible)}")
    print_console(eligible[:top])


def _default_queries(profile: dict) -> list[str]:
    queries = profile_terms(profile, "search", "default_queries")
    return queries or DEFAULT_QUERIES


def _connector(provider: str):
    if provider == "wttj-public":
        return WttjPublicConnector()
    if provider == "indeed-api":
        return IndeedApiConnector.from_env()
    if provider == "france-travail":
        return FranceTravailConnector.from_env()
    raise ValueError(f"Unsupported provider: {provider}")


def _print_discovery_diagnostics(
    discovery: DiscoveryResult,
    target_offers: int,
    max_pages: int,
    hits_per_page: int,
) -> None:
    print(f"Raw provider hits: {discovery.raw_hits}")
    if discovery.duplicate_hits:
        print(f"Duplicate hits removed: {discovery.duplicate_hits}")
    if discovery.target_reached:
        return

    print(
        "Target not reached: "
        f"requested {target_offers}, discovered {len(discovery.offers)} unique offers "
        f"with max_pages={max_pages} and hits_per_page={hits_per_page}."
    )
    for line in _query_capacity_lines(discovery):
        print(line)


def _query_capacity_lines(discovery: DiscoveryResult) -> list[str]:
    by_query: dict[str, dict[str, int]] = {}
    for page in discovery.pages:
        stats = by_query.setdefault(page.query, {"raw": 0, "nb_hits": page.nb_hits, "nb_pages": page.nb_pages})
        stats["raw"] += page.hits
        stats["nb_hits"] = max(stats["nb_hits"], page.nb_hits)
        stats["nb_pages"] = max(stats["nb_pages"], page.nb_pages)

    return [
        f"Query capacity: {query!r} returned {stats['raw']} hits in this run; provider reports {stats['nb_hits']} total hits across {stats['nb_pages']} pages."
        for query, stats in by_query.items()
    ]


if __name__ == "__main__":
    main()
